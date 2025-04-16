# app/agents/reader_agent.py
import pandas as pd
from app.db.database import get_db
from app.models.connector import Connector
from app.utils.logging import logger
from app.utils.readers import read_from_file, read_from_db, read_from_cloud
import os

class ReaderAgent:
    def __init__(self):
        self.db = get_db()

    def read_data(self, connector_id: int, selected_file: str = None) -> pd.DataFrame:
        connector = self.db.__next__().query(Connector).filter(Connector.id == connector_id).first()
        if not connector:
            logger.error(f"Connector ID {connector_id} not found.")
            raise ValueError("Connector not found.")

        logger.info(f"Reading data using connector: {connector.name} of type {connector.type}")

        # If file path is set and a file is selected
        if selected_file:
            if connector.file_path:
                full_path = os.path.join(connector.file_path, selected_file)
            else:
                full_path = selected_file
                
            if not os.path.exists(full_path):
                logger.error(f"Selected file {selected_file} not found")
                raise ValueError(f"File not found: {selected_file}")
            connector.file_path = full_path

        if connector.type in ["csv", "pdf", "txt", "image", "xlsx"]:
            return read_from_file(connector)
        elif connector.type in ["postgres", "mysql", "mongodb", "clickhouse", "snowflake"]:
            return read_from_db(connector)
        elif connector.type in ["googledrive", "s3", "googlesheets"]:
            return read_from_cloud(connector)
        else:
            logger.error(f"Unsupported connector type: {connector.type}")
            raise ValueError("Unsupported connector type")
