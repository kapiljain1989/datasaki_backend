from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from app.db.database import Base

class Connector(Base):
    __tablename__ = "connectors"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "clickhouse", "postgres", etc.
    connector_type = Column(String, nullable=False)  # "source" or "destination"
    file_path = Column(Text, nullable=True)
    connection_details = Column(JSON, nullable=True)  # Store connection details as JSON
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)