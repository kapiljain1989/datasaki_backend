from sqlalchemy import Column, String, Text,Integer,ForeignKey
from app.db.database import Base

class Connector(Base):
    __tablename__ = "connectors"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    file_path = Column(Text, nullable=True)
    connection_uri = Column(Text, nullable=True)
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)