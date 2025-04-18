from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.db.database import Base, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.company import Company
import re

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for Google OAuth users
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)  # Profile picture URL for Google OAuth users
    is_active = Column(Boolean, default=True)
    is_google_auth = Column(Boolean, default=False)  # Flag for Google OAuth users
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Company association
    company = relationship("Company", back_populates="users")
    
    # Role association
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    # Resources owned by the user
    resources = relationship("Resource", back_populates="owner")
    
    # LLM configurations
    llms = relationship("LLM", back_populates="user")
    
    # Logs associated with the user
    logs = relationship("Log", back_populates="user")

    @staticmethod
    def get_company_by_email(email: str, db: Session) -> Company:
        """Get or create company based on email domain."""
        domain = email.split('@')[1]
        company = db.query(Company).filter(Company.domain == domain).first()
        return company

# Event listener to automatically set company based on email domain
@event.listens_for(User, 'before_insert')
def set_company_before_insert(mapper, connection, target):
    """Set company based on email domain before user insertion."""
    if not target.company_id:
        domain = target.email.split('@')[1]
        company = User.get_company_by_email(target.email, connection)
        if company:
            target.company_id = company.id
