from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate




def create_user(db: Session, user_data: UserCreate):
    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        name=user_data.name,
        company_name=user_data.company_name,
        email=user_data.email,
        company_industry=user_data.company_industry,
        company_size=user_data.company_size,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

