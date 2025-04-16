from uuid import uuid4
from typing import Dict, Optional
import os
from sqlalchemy.orm import Session
from app.utils.logging import logger
from app.models.connector import Connector
from app.schemas.connector import ConnectorConfig

class ConnectorAgent:

    def create_connector(self, config: ConnectorConfig, db: Session) -> Dict:
        logger.info(f"Attempting to create connector: {config.name} of type {config.type} for user {config.user_id}")
        if config.type in ["csv", "pdf", "image", "xlsx", "txt"]:
            if not config.file_path or not os.path.exists(config.file_path):
                logger.error(f"File path invalid or not found: {config.file_path}")
                raise FileNotFoundError(f"File not found: {config.file_path}")
        elif config.type in ["postgresql", "mysql"]:
            if not config.connection_uri:
                logger.error(f"Missing connection URI for connector type: {config.type}")
                raise ValueError("Connection URI must be provided for this connector type")

        connector_id = str(uuid4())
        db_connector = Connector(
            id=connector_id,
            name=config.name,
            type=config.type,
            file_path=config.file_path,
            connection_uri=config.connection_uri,
            user_id=config.user_id
        )
        db.add(db_connector)
        db.commit()
        db.refresh(db_connector)

        logger.info(f"Connector saved to DB successfully: {connector_id}")
        return {"message": "Connector created successfully", "connector_id": connector_id}

    def get_connector(self, connector_id: str, db: Session) -> Optional[Dict]:
        logger.info(f"Retrieving connector with ID: {connector_id}")
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            logger.error(f"Connector with ID {connector_id} not found")
            raise ValueError(f"Connector with ID {connector_id} not found")

        logger.info(f"Connector retrieved: {connector_id}")
        return {
            "id": connector.id,
            "name": connector.name,
            "type": connector.type,
            "file_path": connector.file_path,
            "connection_uri": connector.connection_uri,
            "user_id": connector.user_id
        }
