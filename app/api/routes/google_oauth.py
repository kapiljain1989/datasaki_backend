import os
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.utils.logging import logger  # Import the logger

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://localhost:8000/auth/google/callback")

@router.get("/google/login")
def google_login():
    """Generate Google OAuth login URL."""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )

    logger.info("Generated Google login URL")
    return {"login_url": google_auth_url}

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback and authenticate user."""
    logger.info("Google OAuth callback received")

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    try:
        logger.info("Requesting access token from Google")
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if "access_token" not in token_json:
            logger.warning("Google authentication failed: No access token received")
            raise HTTPException(status_code=400, detail="Google authentication failed")

        logger.info("Google access token received successfully")

        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        user_info = requests.get(user_info_url, headers=headers).json()

        if not user_info.get("email"):
            logger.warning("Google account does not have an email")
            raise HTTPException(status_code=400, detail="Google account must have an email")

        email = user_info["email"]
        logger.info(f"Google user authenticated: {email}")

        # Check if the user exists in the database
        existing_user = AuthService.get_user_by_email(db, email)
        if not existing_user:
            logger.info(f"Registering new user: {email}")
            user_data = UserCreate(
                name=user_info.get("name", ""),
                email=email,
                company_name="Unknown",
                company_industry="Unknown",
                company_size="Unknown",
                password="oauth_user"  # Placeholder password (not used for OAuth users)
            )
            user = AuthService.register_user(db, user_data)
            logger.info(f"New user registered successfully: {email}")
        else:
            user = existing_user
            logger.info(f"Existing user logged in: {email}")

        return {"message": "User authenticated successfully", "user": user.email}

    except Exception as e:
        logger.error(f"Google authentication failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
