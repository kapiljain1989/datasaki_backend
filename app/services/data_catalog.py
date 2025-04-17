from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, DataSourceType
from app.models.connector import Connector
from app.utils.logging import logger
import pandas as pd
import json

class DataCatalogService:
    """Service for managing data catalog and metadata."""

    def __init__(self, db: Session):
        self.db = db

    def infer_schema(self, connector: Connector, source_path: str, source_type: DataSourceType) -> Dict[str, Any]:
        """Infer schema information from the data source."""
        try:
            if source_type == DataSourceType.DATABASE:
                # For database tables
                schema_info = self._infer_database_schema(connector, source_path)
            elif source_type == DataSourceType.FILE:
                # For files (CSV, Excel, etc.)
                schema_info = self._infer_file_schema(connector, source_path)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")

            return schema_info
        except Exception as e:
            logger.error(f"Error inferring schema: {str(e)}")
            raise

    def _infer_database_schema(self, connector: Connector, table_name: str) -> Dict[str, Any]:
        """Infer schema from a database table."""
        try:
            # Use connector to get table schema
            schema = connector.get_table_schema(table_name)
            return {
                "columns": schema,
                "row_count": connector.get_row_count(table_name),
                "primary_keys": connector.get_primary_keys(table_name),
                "foreign_keys": connector.get_foreign_keys(table_name)
            }
        except Exception as e:
            logger.error(f"Error inferring database schema: {str(e)}")
            raise

    def _infer_file_schema(self, connector: Connector, file_path: str) -> Dict[str, Any]:
        """Infer schema from a file."""
        try:
            # Read a sample of the file
            df = connector.read_file(file_path, nrows=1000)
            
            schema = []
            for column in df.columns:
                dtype = str(df[column].dtype)
                sample_values = df[column].head(5).tolist()
                null_count = df[column].isnull().sum()
                
                schema.append({
                    "name": column,
                    "type": dtype,
                    "sample_values": sample_values,
                    "null_count": int(null_count),
                    "unique_count": int(df[column].nunique())
                })

            return {
                "columns": schema,
                "row_count": len(df),
                "file_format": file_path.split('.')[-1].lower()
            }
        except Exception as e:
            logger.error(f"Error inferring file schema: {str(e)}")
            raise

    def get_dataset_metadata(self, dataset_id: int) -> Dict[str, Any]:
        """Get metadata for a specific dataset."""
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found")

        return {
            "name": dataset.name,
            "description": dataset.description,
            "source_type": dataset.source_type.value,
            "source_path": dataset.source_path,
            "schema_info": dataset.schema_info,
            "dataset_metadata": dataset.dataset_metadata,
            "created_at": dataset.created_at,
            "updated_at": dataset.updated_at
        }

    def update_dataset_metadata(self, dataset_id: int, metadata: Dict[str, Any]) -> None:
        """Update metadata for a specific dataset."""
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found")

        dataset.dataset_metadata = metadata
        self.db.commit() 