from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class LLM(Base):
    """Model for storing LLM configurations."""
    __tablename__ = "llms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    config = Column(JSON, nullable=False, default={})

    # Relationships
    user = relationship("User", back_populates="llms") 