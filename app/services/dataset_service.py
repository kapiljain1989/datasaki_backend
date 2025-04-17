from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, Transformation, DataSourceType
from app.models.connector import Connector
from app.services.data_catalog import DataCatalogService
from app.utils.logging import logger
from pydantic import BaseModel

class TransformationConfig(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    order: int

class DatasetService:
    """Service for managing datasets and their transformations."""

    def __init__(self, db: Session):
        self.db = db
        self.catalog_service = DataCatalogService(db)

    def create_dataset(
        self,
        name: str,
        description: str,
        connector_id: str,
        source_type: DataSourceType,
        source_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dataset:
        """Create a new dataset."""
        try:
            # Get the connector
            connector = self.db.query(Connector).filter(Connector.id == connector_id).first()
            if not connector:
                raise ValueError(f"Connector with ID {connector_id} not found")

            # Infer schema information
            schema_info = self.catalog_service.infer_schema(connector, source_path, source_type)

            # Create the dataset
            dataset = Dataset(
                name=name,
                description=description,
                connector_id=connector_id,
                source_type=source_type,
                source_path=source_path,
                schema_info=schema_info,
                dataset_metadata=metadata or {}
            )

            self.db.add(dataset)
            self.db.commit()
            self.db.refresh(dataset)

            logger.info(f"Created dataset: {name}")
            return dataset

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating dataset: {str(e)}")
            raise

    def add_transformation(
        self,
        dataset_id: int,
        transformation: TransformationConfig
    ) -> Transformation:
        """Add a transformation to a dataset."""
        try:
            dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset with ID {dataset_id} not found")

            # Create the transformation
            new_transformation = Transformation(
                dataset_id=dataset_id,
                name=transformation.name,
                type=transformation.type,
                config=transformation.config,
                order=transformation.order
            )

            self.db.add(new_transformation)
            self.db.commit()
            self.db.refresh(new_transformation)

            logger.info(f"Added transformation {transformation.name} to dataset {dataset.name}")
            return new_transformation

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding transformation: {str(e)}")
            raise

    def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
        """Get dataset information including transformations."""
        try:
            dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset with ID {dataset_id} not found")

            # Get transformations ordered by their order field
            transformations = (
                self.db.query(Transformation)
                .filter(Transformation.dataset_id == dataset_id)
                .order_by(Transformation.order)
                .all()
            )

            return {
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
                "source_type": dataset.source_type.value,
                "source_path": dataset.source_path,
                "schema_info": dataset.schema_info,
                "dataset_metadata": dataset.dataset_metadata,
                "transformations": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "type": t.type,
                        "config": t.config,
                        "order": t.order
                    }
                    for t in transformations
                ]
            }

        except Exception as e:
            logger.error(f"Error getting dataset: {str(e)}")
            raise

    def update_dataset(
        self,
        dataset_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dataset:
        """Update dataset information."""
        try:
            dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset with ID {dataset_id} not found")

            if name is not None:
                dataset.name = name
            if description is not None:
                dataset.description = description
            if metadata is not None:
                dataset.dataset_metadata = metadata

            self.db.commit()
            self.db.refresh(dataset)

            logger.info(f"Updated dataset: {dataset.name}")
            return dataset

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating dataset: {str(e)}")
            raise

    def delete_dataset(self, dataset_id: int) -> None:
        """Delete a dataset and its transformations."""
        try:
            dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                raise ValueError(f"Dataset with ID {dataset_id} not found")

            self.db.delete(dataset)
            self.db.commit()

            logger.info(f"Deleted dataset with ID: {dataset_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting dataset: {str(e)}")
            raise 