from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum
from typing import Optional

class ConnectorType(enum.Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"

class Connector(Base):
    __tablename__ = "connectors"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    type = Column(Enum(ConnectorType))
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    connector_type = Column(String, nullable=False)  # "source" or "destination"
    file_path = Column(Text, nullable=True)
    connection_details = Column(JSON, nullable=True)  # Store connection details as JSON
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    datasets = relationship("Dataset", back_populates="connector", cascade="all, delete-orphan")

    def get_table_schema(self, table_name: str) -> list:
        """Get schema information for a table."""
        # This should be implemented based on the connector type
        pass

    def get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        # This should be implemented based on the connector type
        pass

    def get_primary_keys(self, table_name: str) -> list:
        """Get primary key columns for a table."""
        # This should be implemented based on the connector type
        pass

    def get_foreign_keys(self, table_name: str) -> list:
        """Get foreign key columns for a table."""
        # This should be implemented based on the connector type
        pass

    def read_file(self, file_path: str, nrows: Optional[int] = None) -> 'pd.DataFrame':
        """Read a file and return a pandas DataFrame."""
        # This should be implemented based on the connector type
        pass