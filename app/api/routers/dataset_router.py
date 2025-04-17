from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.services.dataset_service import DatasetService, TransformationConfig
from app.models.dataset import DataSourceType
from app.dependencies import get_db

router = APIRouter(prefix="/datasets", tags=["datasets"])

class DatasetCreate(BaseModel):
    name: str
    description: str
    connector_id: str
    source_type: DataSourceType
    source_path: str
    dataset_metadata: Optional[Dict[str, Any]] = None

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dataset_metadata: Optional[Dict[str, Any]] = None

@router.post("/")
async def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db)
):
    """Create a new dataset."""
    try:
        service = DatasetService(db)
        result = service.create_dataset(
            name=dataset.name,
            description=dataset.description,
            connector_id=dataset.connector_id,
            source_type=dataset.source_type,
            source_path=dataset.source_path,
            metadata=dataset.dataset_metadata
        )
        return {"message": "Dataset created successfully", "dataset_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Get dataset information including transformations."""
    try:
        service = DatasetService(db)
        return service.get_dataset(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{dataset_id}")
async def update_dataset(
    dataset_id: int,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db)
):
    """Update dataset information."""
    try:
        service = DatasetService(db)
        result = service.update_dataset(
            dataset_id=dataset_id,
            name=dataset.name,
            description=dataset.description,
            metadata=dataset.dataset_metadata
        )
        return {"message": "Dataset updated successfully", "dataset_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """Delete a dataset and its transformations."""
    try:
        service = DatasetService(db)
        service.delete_dataset(dataset_id)
        return {"message": "Dataset deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dataset_id}/transformations")
async def add_transformation(
    dataset_id: int,
    transformation: TransformationConfig,
    db: Session = Depends(get_db)
):
    """Add a transformation to a dataset."""
    try:
        service = DatasetService(db)
        result = service.add_transformation(dataset_id, transformation)
        return {"message": "Transformation added successfully", "transformation_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 