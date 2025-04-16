from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.agents.reader_agent import ReaderAgent
from app.dependencies import get_db, common_dependency
from app.services.connector_service import ConnectorService
from app.utils.logging import logger
import os
from typing import List

router = APIRouter()

@router.post("/read-from-connector/{connector_id}")
def read_from_connector(
    connector_id: str,
    selected_files: list[str] = None,
    dependency: dict = Depends(common_dependency),
    db: Session = Depends(get_db),
):
    user_id = dependency["user_id"]
    logger.info(f"ReaderAgent triggered by user_id={user_id} for connector_id={connector_id} with files={selected_files}")

    try:
        connector = ConnectorService().get_connector(connector_id, user_id, db)
        if not connector:
            logger.warning(f"Connector {connector_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Connector not found")

        if not connector["file_path"] and not selected_files:
            raise HTTPException(status_code=400, detail="Either file_path must be set or files must be provided")

        reader_agent = ReaderAgent()
        results = []
        
        if selected_files:
            for file in selected_files:
                result = reader_agent.read_data(connector_id, file)
                results.append({"file": file, "data_preview": result[:5]})
        else:
            # If no files provided, read all files in directory
            files = list_files(connector_id, dependency, db)
            for file in files:
                result = reader_agent.read_data(connector_id, file)
                results.append({"file": file, "data_preview": result[:5]})

        logger.info(f"ReaderAgent successfully read from connector {connector_id}")
        return {"status": "success", "results": results}

    except Exception as e:
        logger.error(f"Failed to read from connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to read from connector")

@router.get("/list-files/{connector_id}")
def list_files(
    connector_id: str,
    dependency: dict = Depends(common_dependency),
    db: Session = Depends(get_db),
) -> List[str]:
    user_id = dependency["user_id"]
    logger.info(f"Listing files for connector_id={connector_id} by user_id={user_id}")

    try:
        connector = ConnectorService().get_connector(connector_id, user_id, db)
        if not connector:
            logger.warning(f"Connector {connector_id} not found for user {user_id}")
            raise HTTPException(status_code=404, detail="Connector not found")

        if not connector["file_path"]:
            raise HTTPException(status_code=400, detail="File path not configured")

        # Get all files in directory
        all_files = os.listdir(connector["file_path"])
        
        # Filter files based on connector type
        if connector["type"] == "csv":
            filtered_files = [f for f in all_files if f.endswith('.csv')]
        elif connector["type"] == "pdf":
            filtered_files = [f for f in all_files if f.endswith('.pdf')]
        elif connector["type"] == "txt":
            filtered_files = [f for f in all_files if f.endswith('.txt')]
        elif connector["type"] == "xlsx":
            filtered_files = [f for f in all_files if f.endswith(('.xlsx', '.xls'))]
        elif connector["type"] == "image":
            filtered_files = [f for f in all_files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        else:
            raise HTTPException(status_code=400, detail="Unsupported connector type for file listing")

        return filtered_files

    except Exception as e:
        logger.error(f"Failed to list files for connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list files")
