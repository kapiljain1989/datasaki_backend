from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    company_name: str
    email: EmailStr
    company_industry: str
    company_size: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
