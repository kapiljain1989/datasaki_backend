from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union

class ConnectorConfig(BaseModel):
    name: str
    type: str  # e.g., "clickhouse", "postgres", etc.
    connector_type: str  # "source" or "destination"
    file_path: Optional[str] = None
    connection_details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class ConnectorResponse(BaseModel):
    id: str
    name: str
    type: str
    connector_type: str
    file_path: Optional[str] = None
    connection_details: Optional[Dict[str, Any]] = None
    user_id: str

class WriteRequest(BaseModel):
    """Schema for writing data to a destination connector."""
    connector_id: str
    table_name: str
    data: List[Dict[str, Any]]  # List of records to write
    table_schema: Optional[Dict[str, str]] = None  # Optional schema definition for creating table
