from pydantic import BaseModel
from typing import Optional

class ConnectorConfig(BaseModel):
    name: str
    type: str
    file_path: Optional[str] = None
    connection_uri: Optional[str] = None
    user_id: Optional[str] = None
