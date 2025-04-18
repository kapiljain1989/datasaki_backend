from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, Transformation, DataSourceType
from app.models.connector import Connector
from app.services.data_catalog import DataCatalogService
from app.utils.logging import logger
from pydantic import BaseModel
import sqlalchemy as sa
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    DatasetList,
    TransformationCreate,
    TransformationResponse
)

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
        user_id: int,
        name: str,
        description: Optional[str] = None,
        connector_id: Optional[int] = None,
        source_type: Optional[DataSourceType] = None,
        source_path: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> DatasetResponse:
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
                user_id=user_id,
                name=name,
                description=description,
                connector_id=connector_id,
                source_type=source_type,
                source_path=source_path,
                schema_info=schema_info,
                metadata=metadata
            )

            self.db.add(dataset)
            self.db.commit()
            self.db.refresh(dataset)

            logger.info(f"Created dataset: {name}")
            return DatasetResponse.from_orm(dataset)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating dataset: {str(e)}")
            raise

    def add_transformation(
        self,
        dataset_id: int,
        user_id: int,
        transformation: TransformationCreate
    ) -> TransformationResponse:
        """Add a transformation to a dataset."""
        try:
            dataset = self.db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()
            if not dataset:
                raise ValueError("Dataset not found")

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
            return TransformationResponse(
                id=new_transformation.id,
                dataset_id=new_transformation.dataset_id,
                type=new_transformation.type,
                config=new_transformation.config,
                created_at=new_transformation.created_at.isoformat()
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding transformation: {str(e)}")
            raise

    def get_dataset(self, dataset_id: int, user_id: int) -> DatasetResponse:
        """Get dataset information including transformations."""
        try:
            dataset = self.db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()
            if not dataset:
                raise ValueError("Dataset not found")

            # Get transformations ordered by their order field
            transformations = (
                self.db.query(Transformation)
                .filter(Transformation.dataset_id == dataset_id)
                .order_by(Transformation.order)
                .all()
            )

            return DatasetResponse(
                id=dataset.id,
                name=dataset.name,
                description=dataset.description,
                source_type=dataset.source_type.value,
                source_path=dataset.source_path,
                schema_info=dataset.schema_info,
                metadata=dataset.metadata,
                transformations=[
                    TransformationResponse(
                        id=t.id,
                        name=t.name,
                        type=t.type,
                        config=t.config,
                        created_at=t.created_at.isoformat()
                    )
                    for t in transformations
                ]
            )

        except Exception as e:
            logger.error(f"Error getting dataset: {str(e)}")
            raise

    def update_dataset(
        self,
        dataset_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> DatasetResponse:
        """Update dataset information."""
        try:
            dataset = self.db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()
            if not dataset:
                raise ValueError("Dataset not found")

            if name is not None:
                dataset.name = name
            if description is not None:
                dataset.description = description
            if metadata is not None:
                dataset.metadata = metadata

            self.db.commit()
            self.db.refresh(dataset)

            logger.info(f"Updated dataset: {dataset.name}")
            return DatasetResponse.from_orm(dataset)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating dataset: {str(e)}")
            raise

    def delete_dataset(self, dataset_id: int, user_id: int) -> None:
        """Delete a dataset and its transformations."""
        try:
            dataset = self.db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()
            if not dataset:
                raise ValueError("Dataset not found")

            self.db.delete(dataset)
            self.db.commit()

            logger.info(f"Deleted dataset with ID: {dataset_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting dataset: {str(e)}")
            raise

    def list_datasets(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        source_type: Optional[DataSourceType] = None
    ) -> Tuple[int, List[DatasetResponse]]:
        """List datasets with pagination and optional filtering."""
        try:
            query = self.db.query(Dataset).filter(Dataset.user_id == user_id)
            
            if search:
                query = query.filter(Dataset.name.ilike(f"%{search}%"))
            if source_type:
                query = query.filter(Dataset.source_type == source_type)
            
            total = query.count()
            datasets = query.offset(skip).limit(limit).all()
            return total, [DatasetResponse.from_orm(dataset) for dataset in datasets]

        except Exception as e:
            logger.error(f"Error listing datasets: {str(e)}")
            raise 