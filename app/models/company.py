from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    domain = Column(String, unique=True, index=True)
    industry = Column(String)
    size = Column(String)
    
    # Relationships
    users = relationship("User", back_populates="company")
    resources = relationship("Resource", back_populates="company") 