from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.dataset import DataSourceType

class TransformationBase(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    order: int

class TransformationCreate(TransformationBase):
    pass

class TransformationResponse(TransformationBase):
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DatasetBase(BaseModel):
    name: str
    description: str
    source_type: DataSourceType
    source_path: str
    dataset_metadata: Optional[Dict[str, Any]] = None

class DatasetCreate(DatasetBase):
    connector_id: str

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dataset_metadata: Optional[Dict[str, Any]] = None

class DatasetResponse(DatasetBase):
    id: int
    connector_id: str
    schema_info: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    transformations: List[TransformationResponse]

    class Config:
        from_attributes = True

class DatasetList(BaseModel):
    total: int
    items: List[DatasetResponse]

    class Config:
        from_attributes = True 