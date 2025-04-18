from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.role import Role
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from jose import jwt, JWTError
from app.core.config import settings
from app.utils.logging import logger
from app.core.exceptions import credentials_exception
from app.core.logging import log_action
import json

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user and return the user object if successful."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token_for_user(self, user: User) -> str:
        """Create an access token for a user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )

    def login_user(self, email: str, password: str, db: Session) -> Optional[str]:
        """Authenticate user and return access token if successful."""
        try:
            user = self.authenticate_user(email, password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            return self.create_access_token_for_user(user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during login"
            )

    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        try:
            # Create company
            company = Company(
                name=user_data.company_name,
                domain=user_data.email.split('@')[1],
                industry=user_data.industry,
                size=user_data.size
            )
            self.db.add(company)
            self.db.flush()  # Get company ID without committing

            # Create user
            hashed_password = get_password_hash(user_data.password)
            user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                name=user_data.name,
                company_id=company.id
            )

            # Add default role
            default_role = self.db.query(Role).filter(Role.name == "user").first()
            if default_role:
                user.roles.append(default_role)

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            # Log the registration
            log_action(
                action="register",
                user_id=user.id,
                details={
                    "email": user.email,
                    "company_id": company.id
                }
            )

            return user

        except IntegrityError as e:
            self.db.rollback()
            if "ix_users_email" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )

    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        logger.info(f"User details accessed, {email}")
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_email_from_token(token: str) -> str:
        """Get email from JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            return email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
