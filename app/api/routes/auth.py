from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.db.database import SessionLocal
from app.schemas.user import UserCreate
from app.utils.logging import logger  # Import the logger

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register")
def register(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        company_name: str = Form(...),
        industry: str = Form(...),
        company_size: str = Form(...),
        db: Session = Depends(get_db),
):
    """Registers a user and stores hashed password in the database."""
    logger.info(f"User registration attempt: {email}")

    try:
        user_data = UserCreate(
            name=name,
            email=email,
            password=password,
            company_name=company_name,
            company_industry=industry,
            company_size=company_size,
        )
        user = AuthService.register_user(user_data, db)

        logger.info(f"User registered successfully: {email}")
        return user
    except Exception as e:
        logger.error(f"User registration failed for {email}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Registration failed")

@router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    """Authenticates user and returns access token."""
    logger.info(f"Login attempt for email: {form_data.username}")

    try:
        token = AuthService.login_user(form_data.username, form_data.password, db)

        if token:
            logger.info(f"Login successful for email: {form_data.username}")
            return token
        else:
            logger.warning(f"Invalid login credentials for email: {form_data.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Login failed for email: {form_data.username} - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
