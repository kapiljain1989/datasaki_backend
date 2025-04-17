from typing import Dict, Any, List
import pandas as pd
from clickhouse_driver import Client
from app.db.database import get_db
from app.models.connector import Connector
from app.utils.logging import logger

class WriterAgent:
    def __init__(self):
        self.db = get_db()

    def write_to_clickhouse(self, connector_id: int, data: pd.DataFrame, table_name: str) -> bool:
        """
        Write data to ClickHouse database using the specified connector.
        
        Args:
            connector_id (int): ID of the ClickHouse connector
            data (pd.DataFrame): Data to be written
            table_name (str): Target table name in ClickHouse
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        try:
            # Get connector details
            connector = self.db.__next__().query(Connector).filter(Connector.id == connector_id).first()
            if not connector:
                logger.error(f"Connector ID {connector_id} not found.")
                raise ValueError("Connector not found")

            if connector.type != "clickhouse":
                logger.error(f"Connector type {connector.type} is not ClickHouse")
                raise ValueError("Invalid connector type. Expected ClickHouse")

            # Parse connection details
            connection_details = connector.connection_details
            host = connection_details.get('host')
            port = connection_details.get('port', 9000)
            user = connection_details.get('user')
            password = connection_details.get('password')
            database = connection_details.get('database')

            # Create ClickHouse client
            client = Client(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )

            # Convert DataFrame to list of dictionaries
            data_dict = data.to_dict('records')
            
            # Get column names and types
            columns = list(data.columns)
            
            # Prepare the insert query
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
            
            # Execute the insert
            client.execute(query, data_dict)
            
            logger.info(f"Successfully wrote {len(data)} rows to ClickHouse table {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error writing to ClickHouse: {str(e)}")
            raise

    def create_table_if_not_exists(self, connector_id: int, table_name: str, schema: Dict[str, str]) -> bool:
        """
        Create a table in ClickHouse if it doesn't exist.
        
        Args:
            connector_id (int): ID of the ClickHouse connector
            table_name (str): Name of the table to create
            schema (Dict[str, str]): Dictionary mapping column names to ClickHouse data types
            
        Returns:
            bool: True if table was created or already exists, False otherwise
        """
        try:
            # Get connector details
            connector = self.db.__next__().query(Connector).filter(Connector.id == connector_id).first()
            if not connector:
                logger.error(f"Connector ID {connector_id} not found.")
                raise ValueError("Connector not found")

            # Parse connection details
            connection_details = connector.connection_details
            host = connection_details.get('host')
            port = connection_details.get('port', 9000)
            user = connection_details.get('user')
            password = connection_details.get('password')
            database = connection_details.get('database')

            # Create ClickHouse client
            client = Client(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )

            # Prepare column definitions
            column_definitions = [f"{col} {dtype}" for col, dtype in schema.items()]
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(column_definitions)}
                ) ENGINE = MergeTree()
                ORDER BY tuple()
            """

            # Execute the create table query
            client.execute(create_table_query)
            logger.info(f"Successfully created or verified table {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error creating table in ClickHouse: {str(e)}")
            raise 