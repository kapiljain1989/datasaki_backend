from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.db.database import SessionLocal
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.models.company import Company
from app.models.role import Role
from app.core.logging import log_action
from app.utils.logging import logger
from app.core.google_oauth import GoogleOAuth
from fastapi import status
from sqlalchemy.exc import IntegrityError
import re

router = APIRouter()

# List of common public email domains
PUBLIC_EMAIL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
    'icloud.com', 'protonmail.com', 'zoho.com', 'mail.com', 'yandex.com'
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Extract domain from email
        email_domain = user_data.email.split('@')[1]
        
        # Check if domain is public
        is_public_domain = email_domain.lower() in PUBLIC_EMAIL_DOMAINS
        
        # Create or get company
        company = None
        if is_public_domain:
            # For public domains, use the provided company name
            company = Company(
                name=user_data.company_name,
                domain=email_domain,
                industry=user_data.industry,
                size=user_data.size
            )
        else:
            # For private domains, check if company exists
            company = db.query(Company).filter(Company.domain == email_domain).first()
            if not company:
                company = Company(
                    name=user_data.company_name,
                    domain=email_domain,
                    industry=user_data.industry,
                    size=user_data.size
                )
                db.add(company)
                db.flush()  # Get the company ID without committing
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            name=user_data.name,
            company_id=company.id
        )
        
        # Add default role
        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role:
            user.roles.append(default_role)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log the registration
        log_action(
            action="register",
            user_id=user.id,
            details={
                "email": user.email,
                "company_id": company.id,
                "is_public_domain": is_public_domain
            }
        )
        
        return user
        
    except IntegrityError as e:
        db.rollback()
        if "ix_companies_domain" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A company with this domain already exists. Please contact support if you believe this is an error."
            )
        elif "ix_users_email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    """Authenticates user and returns access token."""
    logger.info(f"Login attempt for email: {form_data.username}")

    try:
        auth_service = AuthService(db)
        token = auth_service.login_user(form_data.username, form_data.password, db)
        logger.info(f"Login successful for email: {form_data.username}")
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException as e:
        # Re-raise HTTP exceptions with their original status code and detail
        raise e
    except Exception as e:
        logger.error(f"Login failed for email: {form_data.username} - {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.get("/google/login")
async def google_login(use_https: bool = True):
    """Redirect to Google OAuth login page.
    
    Args:
        use_https (bool): Whether to use HTTPS redirect URI. Defaults to True.
    """
    google_oauth = GoogleOAuth()
    auth_url = google_oauth.get_auth_url(use_https=use_https)
    return {"url": auth_url}

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback and return access token."""
    try:
        google_oauth = GoogleOAuth()
        result = await google_oauth.handle_google_auth(code, db)
        return result
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )
