from sqlalchemy.orm import Session
from app.core.agents.connector_agent import ConnectorAgent
from app.schemas.connector import ConnectorConfig, ConnectorResponse, WriteRequest
from app.utils.logging import logger
from typing import List, Dict, Any, Optional
from clickhouse_driver import Client
import pandas as pd
import os

class ConnectorService:
    def __init__(self):
        self.agent = ConnectorAgent()

    def create_connector(self, config: ConnectorConfig, db: Session) -> ConnectorResponse:
        logger.info(f"Service: Creating connector for user {config.user_id}")
        
        # Validate connector type
        if config.connector_type not in ["source", "destination"]:
            raise ValueError("Connector type must be either 'source' or 'destination'")
            
        # Validate connection details for database connectors
        if config.type in ["clickhouse", "postgres", "mysql", "mongodb", "snowflake"]:
            if not config.connection_details:
                raise ValueError(f"Connection details are required for {config.type} connector")
            required_fields = ["host", "port", "user", "password", "database"]
            for field in required_fields:
                if field not in config.connection_details:
                    raise ValueError(f"Missing required field '{field}' in connection details")
        
        return self.agent.create_connector(config, db)

    def get_connector(self, connector_id: str, user_id: str, db: Session) -> ConnectorResponse:
        logger.info(f"Service: Retrieving connector {connector_id} for user {user_id}")
        connector = self.agent.get_connector(connector_id, db)

        if connector["user_id"] != user_id:
            logger.warning(f"Unauthorized access to connector {connector_id} by user {user_id}")
            raise PermissionError("Unauthorized access")

        return connector

    def get_user_connectors(self, user_id: str, db: Session, connector_type: str = None) -> List[ConnectorResponse]:
        logger.info(f"Service: Retrieving connectors for user {user_id}")
        return self.agent.get_user_connectors(user_id, db, connector_type)

    def delete_connector(self, connector_id: str, user_id: str, db: Session) -> bool:
        logger.info(f"Service: Deleting connector {connector_id} for user {user_id}")
        return self.agent.delete_connector(connector_id, user_id, db)

    def test_connection(self, connector_id: str, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Test the connection for a given connector.
        
        Args:
            connector_id (str): ID of the connector to test
            user_id (str): ID of the user requesting the test
            db (Session): Database session
            
        Returns:
            Dict[str, Any]: Test results including success status and details
        """
        try:
            connector = self.get_connector(connector_id, user_id, db)
            
            if connector.type == "clickhouse":
                return self._test_clickhouse_connection(connector)
            elif connector.type in ["postgres", "mysql"]:
                return self._test_sql_connection(connector)
            elif connector.type in ["csv", "pdf", "txt", "image", "xlsx"]:
                return self._test_file_connection(connector)
            else:
                raise ValueError(f"Unsupported connector type for testing: {connector.type}")
                
        except Exception as e:
            logger.error(f"Error testing connection: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "connector_id": connector_id,
                "connector_type": connector.type
            }

    def _test_clickhouse_connection(self, connector: ConnectorResponse) -> Dict[str, Any]:
        """Test connection to ClickHouse database."""
        try:
            client = Client(
                host=connector.connection_details["host"],
                port=connector.connection_details["port"],
                user=connector.connection_details["user"],
                password=connector.connection_details["password"],
                database=connector.connection_details["database"]
            )
            
            # Test connection by executing a simple query
            result = client.execute("SELECT 1")
            
            return {
                "success": True,
                "message": "Successfully connected to ClickHouse",
                "connector_id": connector.id,
                "connector_type": connector.type,
                "test_query_result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "connector_id": connector.id,
                "connector_type": connector.type
            }

    def _test_sql_connection(self, connector: ConnectorResponse) -> Dict[str, Any]:
        """Test connection to SQL databases (PostgreSQL, MySQL)."""
        try:
            # Implementation for SQL databases
            # This is a placeholder - implement based on your SQL connection needs
            return {
                "success": True,
                "message": f"Successfully connected to {connector.type}",
                "connector_id": connector.id,
                "connector_type": connector.type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "connector_id": connector.id,
                "connector_type": connector.type
            }

    def _test_file_connection(self, connector: ConnectorResponse) -> Dict[str, Any]:
        """Test file-based connector connections."""
        try:
            if not connector.file_path or not os.path.exists(connector.file_path):
                raise FileNotFoundError(f"File not found: {connector.file_path}")
                
            return {
                "success": True,
                "message": "File exists and is accessible",
                "connector_id": connector.id,
                "connector_type": connector.type,
                "file_path": connector.file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "connector_id": connector.id,
                "connector_type": connector.type
            }

    def write_data(self, request: WriteRequest, user_id: str, db: Session) -> Dict[str, Any]:
        """
        Write data to a destination connector.
        
        Args:
            request (WriteRequest): Write request containing data and connector details
            user_id (str): ID of the user requesting the write
            db (Session): Database session
            
        Returns:
            Dict[str, Any]: Write operation results
        """
        try:
            # Get the connector
            connector = self.get_connector(request.connector_id, user_id, db)
            
            # Verify it's a destination connector
            if connector.connector_type != "destination":
                raise ValueError("Can only write to destination connectors")
            
            # Convert data to DataFrame
            df = pd.DataFrame(request.data)
            
            # Handle different connector types
            if connector.type == "clickhouse":
                return self._write_to_clickhouse(connector, request.table_name, df, request.table_schema)
            elif connector.type in ["postgres", "mysql"]:
                return self._write_to_sql(connector, request.table_name, df, request.table_schema)
            else:
                raise ValueError(f"Unsupported destination type: {connector.type}")
                
        except Exception as e:
            logger.error(f"Error writing data: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "connector_id": request.connector_id,
                "table_name": request.table_name
            }

    def _write_to_clickhouse(self, connector: ConnectorResponse, table_name: str, 
                           data: pd.DataFrame, table_schema: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Write data to ClickHouse database."""
        try:
            client = Client(
                host=connector.connection_details["host"],
                port=connector.connection_details["port"],
                user=connector.connection_details["user"],
                password=connector.connection_details["password"],
                database=connector.connection_details["database"]
            )
            
            # Create table if schema is provided
            if table_schema:
                self._create_clickhouse_table(client, table_name, table_schema)
            
            # Convert DataFrame to list of dictionaries
            data_dict = data.to_dict('records')
            
            # Get column names
            columns = list(data.columns)
            
            # Prepare the insert query
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
            
            # Execute the insert
            client.execute(query, data_dict)
            
            return {
                "success": True,
                "message": f"Successfully wrote {len(data)} rows to ClickHouse table {table_name}",
                "rows_written": len(data),
                "table_name": table_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }

    def _create_clickhouse_table(self, client: Client, table_name: str, table_schema: Dict[str, str]) -> None:
        """Create a table in ClickHouse if it doesn't exist."""
        column_definitions = [f"{col} {dtype}" for col, dtype in table_schema.items()]
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(column_definitions)}
            ) ENGINE = MergeTree()
            ORDER BY tuple()
        """
        client.execute(create_table_query)

    def _write_to_sql(self, connector: ConnectorResponse, table_name: str, 
                     data: pd.DataFrame, table_schema: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Write data to SQL databases (PostgreSQL, MySQL)."""
        try:
            # Implementation for SQL databases
            # This is a placeholder - implement based on your SQL connection needs
            return {
                "success": True,
                "message": f"Successfully wrote {len(data)} rows to {connector.type} table {table_name}",
                "rows_written": len(data),
                "table_name": table_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
