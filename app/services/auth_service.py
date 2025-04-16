from datetime import timedelta
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt, JWTError
from app.core.config import config
from app.utils.logging import logger
from app.core.exceptions import credentials_exception

class AuthService:
    @staticmethod
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def register_user(user_data: UserCreate, db: Session):
        """Register a new user with hashed password."""
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            logger.error(f"Email already registered, {user_data.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            company_name=user_data.company_name,
            company_industry=user_data.company_industry,
            company_size=user_data.company_size,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User registered successfully, {new_user.email}")
        return {"message": "User registered successfully"}

    @staticmethod
    def login_user(email: str, password: str, db: Session):
        """Authenticate user and generate access token."""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            logger.error(f"Invalid credentials, {email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(minutes=60))
        logger.info(f"User logged in successfully, {email}")
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        logger.info(f"User details accessed, {email}")
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_email_from_token(token: str):
        """Extract user email from JWT token."""
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            logger.info(f"User details git form secret token")
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            db = AuthService.get_db()
            return db.__next__().query(User).filter(User.email == email).first()
        except JWTError:
            return credentials_exception
