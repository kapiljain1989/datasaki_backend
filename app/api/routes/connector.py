from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.services.connector_service import ConnectorService
from app.schemas.connector import ConnectorConfig, ConnectorResponse, WriteRequest
from app.db.database import get_db
from app.dependencies import common_dependency
from app.utils.logging import logger
from typing import List, Dict, Any

router = APIRouter()
connector_service = ConnectorService()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ConnectorResponse)
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

@router.get("/{connector_id}", response_model=ConnectorResponse)
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

@router.get("/", response_model=List[ConnectorResponse])
def list_connectors(
    connector_type: str = Query(None, description="Filter by connector type (source/destination)"),
    db: Session = Depends(get_db),
    dependency: dict = Depends(common_dependency)
):
    try:
        user_id = dependency["user_id"]
        logger.info(f"API: Listing connectors for user {user_id}")
        return connector_service.get_user_connectors(user_id, db, connector_type)
    except Exception as e:
        logger.error(f"API: Failed to list connectors - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connector(
    connector_id: str,
    db: Session = Depends(get_db),
    dependency: dict = Depends(common_dependency)
):
    try:
        user_id = dependency["user_id"]
        logger.info(f"API: Deleting connector {connector_id} for user {user_id}")
        connector_service.delete_connector(connector_id, user_id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to delete connector - {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{connector_id}/test", response_model=Dict[str, Any])
def test_connection(
    connector_id: str,
    db: Session = Depends(get_db),
    dependency: dict = Depends(common_dependency)
):
    """
    Test the connection for a given connector.
    
    This endpoint will attempt to establish a connection using the connector's configuration
    and return the test results.
    """
    try:
        user_id = dependency["user_id"]
        logger.info(f"API: Testing connection for connector {connector_id}")
        return connector_service.test_connection(connector_id, user_id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to test connection - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/write", response_model=Dict[str, Any])
def write_data(
    request: WriteRequest,
    db: Session = Depends(get_db),
    dependency: dict = Depends(common_dependency)
):
    """
    Write data to a destination connector.
    
    This endpoint allows writing data to a destination connector (e.g., ClickHouse).
    If a schema is provided, it will create the table if it doesn't exist.
    
    Example request:
    {
        "connector_id": "your-connector-id",
        "table_name": "your_table",
        "data": [
            {"column1": "value1", "column2": 123},
            {"column1": "value2", "column2": 456}
        ],
        "schema": {
            "column1": "String",
            "column2": "Int32"
        }
    }
    """
    try:
        user_id = dependency["user_id"]
        logger.info(f"API: Writing data to connector {request.connector_id}")
        return connector_service.write_data(request, user_id, db)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Failed to write data - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
