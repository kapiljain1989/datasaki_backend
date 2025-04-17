from uuid import uuid4
from typing import Dict, Optional, List, Any
import os
from sqlalchemy.orm import Session
from app.utils.logging import logger
from app.models.connector import Connector
from app.schemas.connector import ConnectorConfig, ConnectorResponse

class ConnectorAgent:

    def create_connector(self, config: ConnectorConfig, db: Session) -> ConnectorResponse:
        """
        Create a new connector in the database.
        
        Args:
            config (ConnectorConfig): Configuration for the new connector
            db (Session): Database session
            
        Returns:
            ConnectorResponse: Created connector details
        """
        try:
            connector = Connector(
                id=str(uuid4()),
                name=config.name,
                type=config.type,
                connector_type=config.connector_type,
                file_path=config.file_path,
                connection_details=config.connection_details,
                user_id=config.user_id
            )
            
            db.add(connector)
            db.commit()
            db.refresh(connector)
            
            logger.info(f"Created new connector: {connector.id}")
            return self._convert_to_response(connector)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating connector: {str(e)}")
            raise

    def get_connector(self, connector_id: str, db: Session) -> ConnectorResponse:
        """
        Retrieve a connector by ID.
        
        Args:
            connector_id (str): ID of the connector to retrieve
            db (Session): Database session
            
        Returns:
            ConnectorResponse: Connector details
        """
        connector = db.query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            logger.error(f"Connector {connector_id} not found")
            raise ValueError("Connector not found")
            
        return self._convert_to_response(connector)

    def get_user_connectors(self, user_id: str, db: Session, connector_type: str = None) -> List[ConnectorResponse]:
        """
        Retrieve all connectors for a user, optionally filtered by connector type.
        
        Args:
            user_id (str): ID of the user
            db (Session): Database session
            connector_type (str, optional): Filter by connector type ("source" or "destination")
            
        Returns:
            List[ConnectorResponse]: List of connector details
        """
        query = db.query(Connector).filter(Connector.user_id == user_id)
        if connector_type:
            query = query.filter(Connector.connector_type == connector_type)
            
        connectors = query.all()
        return [self._convert_to_response(connector) for connector in connectors]

    def delete_connector(self, connector_id: str, user_id: str, db: Session) -> bool:
        """
        Delete a connector.
        
        Args:
            connector_id (str): ID of the connector to delete
            user_id (str): ID of the user requesting deletion
            db (Session): Database session
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            connector = db.query(Connector).filter(
                Connector.id == connector_id,
                Connector.user_id == user_id
            ).first()
            
            if not connector:
                logger.error(f"Connector {connector_id} not found or unauthorized")
                raise ValueError("Connector not found or unauthorized")
                
            db.delete(connector)
            db.commit()
            
            logger.info(f"Deleted connector: {connector_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting connector: {str(e)}")
            raise

    def _convert_to_response(self, connector: Connector) -> ConnectorResponse:
        """
        Convert a Connector model instance to a ConnectorResponse.
        
        Args:
            connector (Connector): Connector model instance
            
        Returns:
            ConnectorResponse: Converted response
        """
        return ConnectorResponse(
            id=connector.id,
            name=connector.name,
            type=connector.type,
            connector_type=connector.connector_type,
            file_path=connector.file_path,
            connection_details=connector.connection_details,
            user_id=connector.user_id
        )
