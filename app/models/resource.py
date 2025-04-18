from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # e.g., 'dataset', 'llm', 'connector'
    
    # Company association
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="resources")
    
    # Owner association
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="resources")
    
    # Additional metadata
    resource_metadata = Column(String)  # JSON string for additional resource-specific data 