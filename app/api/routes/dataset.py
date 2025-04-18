from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.services.dataset_service import DatasetService
from app.models.user import User
from app.models.dataset import DataSourceType
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    DatasetList,
    TransformationCreate,
    TransformationResponse
)
from app.dependencies import get_db, get_current_user, validate_token
from app.utils.logging import logger

router = APIRouter(dependencies=[Depends(validate_token)])

@router.post("/", response_model=DatasetResponse)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Create a new dataset for the current user."""
    try:
        logger.info(f"API: Creating dataset for user {current_user.id}")
        service = DatasetService(db)
        return service.create_dataset(dataset, current_user.id, db)
    except Exception as e:
        logger.error(f"API: Failed to create dataset - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=DatasetList)
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    source_type: Optional[DataSourceType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """List datasets for the current user with pagination and optional filtering."""
    try:
        logger.info(f"API: Listing datasets for user {current_user.id}")
        service = DatasetService(db)
        datasets, total = service.list_datasets(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            search=search,
            source_type=source_type,
            db=db
        )
        return DatasetList(total=total, items=datasets)
    except Exception as e:
        logger.error(f"API: Failed to list datasets - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Get dataset information including transformations for the current user."""
    try:
        logger.info(f"API: Getting dataset {dataset_id} for user {current_user.id}")
        service = DatasetService(db)
        return service.get_dataset(dataset_id, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to get dataset - {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: int,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Update dataset information for the current user."""
    try:
        logger.info(f"API: Updating dataset {dataset_id} for user {current_user.id}")
        service = DatasetService(db)
        return service.update_dataset(
            dataset_id=dataset_id,
            user_id=current_user.id,
            name=dataset.name,
            description=dataset.description,
            metadata=dataset.dataset_metadata,
            db=db
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to update dataset - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{dataset_id}", response_model=Dict[str, str])
async def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Delete a dataset and its transformations for the current user."""
    try:
        logger.info(f"API: Deleting dataset {dataset_id} for user {current_user.id}")
        service = DatasetService(db)
        service.delete_dataset(dataset_id, current_user.id, db)
        return {"message": "Dataset deleted successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to delete dataset - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dataset_id}/transformations", response_model=TransformationResponse)
async def add_transformation(
    dataset_id: int,
    transformation: TransformationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Add a transformation to a dataset for the current user."""
    try:
        logger.info(f"API: Adding transformation to dataset {dataset_id} for user {current_user.id}")
        service = DatasetService(db)
        return service.add_transformation(
            dataset_id=dataset_id,
            user_id=current_user.id,
            transformation=transformation,
            db=db
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to add transformation - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dataset_id}/transformations", response_model=List[TransformationResponse])
async def list_transformations(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """List transformations for a dataset."""
    try:
        logger.info(f"API: Listing transformations for dataset {dataset_id} for user {current_user.id}")
        service = DatasetService(db)
        return service.list_transformations(dataset_id, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to list transformations - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview dataset content with optional transformations applied for the current user."""
    try:
        service = DatasetService(db)
        dataset = service.get_dataset(dataset_id, user_id=current_user.id)
        
        # TODO: Implement preview logic based on connector type and transformations
        # This is a placeholder that should be implemented based on your requirements
        return {
            "dataset_id": dataset_id,
            "name": dataset.name,
            "preview": "Preview functionality to be implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 