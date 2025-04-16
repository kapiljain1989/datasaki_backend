from fastapi import APIRouter, Depends
from app.services.ml_service import MLService
from app.dependencies import common_dependency
from app.utils.logging import logger

router = APIRouter()

@router.get("/train")
def train_model(dependency: dict = Depends(common_dependency)):
    user_email = dependency["user_email"]
    service = MLService()
    logger.info(f"Model training initiated by user: {user_email}")
    return service.train(user_email=user_email)
