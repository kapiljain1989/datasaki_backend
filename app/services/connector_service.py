from sqlalchemy.orm import Session
from app.core.agents.connector_agent import ConnectorAgent
from app.schemas.connector import ConnectorConfig
from app.utils.logging import logger

class ConnectorService:
    def __init__(self):
        self.agent = ConnectorAgent()

    def create_connector(self, config: ConnectorConfig, db: Session):
        logger.info(f"Service: Creating connector for user {config.user_id}")
        return self.agent.create_connector(config, db)

    def get_connector(self, connector_id: str, user_id: str, db: Session):
        logger.info(f"Service: Retrieving connector {connector_id} for user {user_id}")
        connector = self.agent.get_connector(connector_id, db)

        if connector["user_id"] != user_id:
            logger.warning(f"Unauthorized access to connector {connector_id} by user {user_id}")
            raise PermissionError("Unauthorized access")

        return connector
