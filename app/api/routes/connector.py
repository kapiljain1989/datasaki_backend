from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.connector_service import ConnectorService
from app.schemas.connector import ConnectorConfig
from app.db.database import get_db
from app.dependencies import common_dependency
from app.utils.logging import logger

router = APIRouter()
connector_service = ConnectorService()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_connector(
    config: ConnectorConfig,
    db: Session = Depends(get_db),
    dependency: dict = Depends(common_dependency)
):
    try:
        config.user_id = dependency["user_id"]
        logger.info(f"API: Creating connector for user {config.user_id}")
        return connector_service.create_connector(config, db)
    except Exception as e:
        logger.error(f"API: Failed to create connector - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{connector_id}")
def get_connector(
    connector_id: str,
    db: Session = Depends(get_db),
    dependency: dict = Depends(common_dependency)
):
    try:
        user_id = dependency["user_id"]
        logger.info(f"API: Getting connector {connector_id} for user {user_id}")
        return connector_service.get_connector(connector_id, user_id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to get connector - {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
