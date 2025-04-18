from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: str
    config: Dict = {}

class ModelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: str
    config: Dict[str, Any]

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_type: str
    config: Dict[str, Any]
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ModelList(BaseModel):
    total: int
    items: List[ModelResponse]

class ModelListResponse(BaseModel):
    total: int
    items: List[ModelResponse]

class TrainingConfig(BaseModel):
    dataset_id: int
    parameters: Dict[str, Any] = Field(default_factory=dict)

class TrainingResponse(BaseModel):
    model_id: int
    status: str
    metrics: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True 