from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    domain: str
    industry: Optional[str] = None
    size: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None 