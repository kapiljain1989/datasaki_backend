from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: constr(min_length=8)
    company_name: str
    industry: str
    size: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    company_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
