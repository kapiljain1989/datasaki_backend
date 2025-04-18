from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.dependencies import get_db, get_current_user, validate_token
from app.models.user import User
from app.services.ml_service import MLService
from app.schemas.ml import (
    ModelCreate,
    ModelResponse,
    ModelUpdate,
    ModelListResponse,
    TrainingConfig,
    TrainingResponse
)
from app.utils.logging import logger

router = APIRouter(dependencies=[Depends(validate_token)])
ml_service = MLService()

@router.post("/models", response_model=ModelResponse)
def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Create a new ML model for the current user."""
    try:
        logger.info(f"API: Creating ML model for user {current_user.id}")
        return ml_service.create_model(model, current_user.id, db)
    except Exception as e:
        logger.error(f"API: Failed to create ML model - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models", response_model=ModelListResponse)
def list_models(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """List ML models for the current user."""
    try:
        logger.info(f"API: Listing ML models for user {current_user.id}")
        return ml_service.list_models(current_user.id, db, skip, limit)
    except Exception as e:
        logger.error(f"API: Failed to list ML models - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Get a specific ML model for the current user."""
    try:
        logger.info(f"API: Getting ML model {model_id} for user {current_user.id}")
        return ml_service.get_model(model_id, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to get ML model - {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/models/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: int,
    model_update: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Update an ML model for the current user."""
    try:
        logger.info(f"API: Updating ML model {model_id} for user {current_user.id}")
        return ml_service.update_model(model_id, model_update, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to update ML model - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/models/{model_id}", response_model=Dict[str, str])
def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Delete an ML model for the current user."""
    try:
        logger.info(f"API: Deleting ML model {model_id} for user {current_user.id}")
        ml_service.delete_model(model_id, current_user.id, db)
        return {"message": "ML model deleted successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to delete ML model - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/models/{model_id}/train", response_model=TrainingResponse)
def train_model(
    model_id: int,
    config: TrainingConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Train an ML model."""
    try:
        logger.info(f"API: Training ML model {model_id} for user {current_user.id}")
        return ml_service.train_model(model_id, config, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to train ML model - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/models/{model_id}/predict", response_model=Dict[str, Any])
def predict(
    model_id: int,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Make predictions using an ML model."""
    try:
        logger.info(f"API: Making predictions with ML model {model_id} for user {current_user.id}")
        return ml_service.predict(model_id, data, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to make predictions - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
