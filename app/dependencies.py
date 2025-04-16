from fastapi import Depends
from app.services.auth_service import AuthService
from app.models.user import User
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

def common_dependency(current_user: User = Depends(AuthService.get_email_from_token)):

    return {
        "user_email": current_user.email,
        "user_id": current_user.id
    }
