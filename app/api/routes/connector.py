from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.connector_service import ConnectorService
from app.models.user import User
from app.schemas.connector import (
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorResponse,
    ConnectorListResponse
)
from app.dependencies import get_db, get_current_user, validate_token
from app.utils.logging import logger

router = APIRouter(dependencies=[Depends(validate_token)])
connector_service = ConnectorService()

@router.post("/", response_model=ConnectorResponse)
def create_connector(
    connector: ConnectorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Create a new connector for the current user."""
    try:
        logger.info(f"API: Creating connector for user {current_user.id}")
        return connector_service.create_connector(connector, current_user.id, db)
    except Exception as e:
        logger.error(f"API: Failed to create connector - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=ConnectorListResponse)
def list_connectors(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """List connectors for the current user."""
    try:
        logger.info(f"API: Listing connectors for user {current_user.id}")
        return connector_service.list_connectors(current_user.id, db, skip, limit)
    except Exception as e:
        logger.error(f"API: Failed to list connectors - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{connector_id}", response_model=ConnectorResponse)
def get_connector(
    connector_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Get a specific connector for the current user."""
    try:
        logger.info(f"API: Getting connector {connector_id} for user {current_user.id}")
        return connector_service.get_connector(connector_id, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to get connector - {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{connector_id}", response_model=ConnectorResponse)
def update_connector(
    connector_id: str,
    connector_update: ConnectorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Update a connector for the current user."""
    try:
        logger.info(f"API: Updating connector {connector_id} for user {current_user.id}")
        return connector_service.update_connector(connector_id, connector_update, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to update connector - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{connector_id}", response_model=Dict[str, str])
def delete_connector(
    connector_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Delete a connector for the current user."""
    try:
        logger.info(f"API: Deleting connector {connector_id} for user {current_user.id}")
        connector_service.delete_connector(connector_id, current_user.id, db)
        return {"message": "Connector deleted successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to delete connector - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{connector_id}/test", response_model=Dict[str, Any])
def test_connection(
    connector_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    authorization: str = Header(...)
):
    """Test the connection for a given connector."""
    try:
        logger.info(f"API: Testing connection for connector {connector_id} for user {current_user.id}")
        return connector_service.test_connection(connector_id, current_user.id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to test connection - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
