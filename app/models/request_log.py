from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    method = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    user_email = Column(String, nullable=True)  # Optional, if user is authenticated
    client_ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
