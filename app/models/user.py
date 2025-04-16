from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    company_industry = Column(String, nullable=False)
    company_size = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)  # Optional for OAuth users
