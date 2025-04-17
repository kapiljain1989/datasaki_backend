from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum

class DataSourceType(enum.Enum):
    FILE = "file"
    DATABASE = "database"
    API = "api"
    STREAM = "stream"

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    connector_id = Column(String, ForeignKey("connectors.id"))
    source_type = Column(Enum(DataSourceType))
    source_path = Column(String)  # File path, table name, or API endpoint
    schema_info = Column(JSON)  # Store schema information
    dataset_metadata = Column(JSON)  # Additional metadata for cataloging
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connector = relationship("Connector", back_populates="datasets")
    transformations = relationship("Transformation", back_populates="dataset", cascade="all, delete-orphan")

class Transformation(Base):
    __tablename__ = "transformations"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    name = Column(String)
    type = Column(String)  # filter, transform, aggregate, etc.
    config = Column(JSON)  # Configuration for the transformation
    order = Column(Integer)  # Order of application
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="transformations") 