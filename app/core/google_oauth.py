from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings
from app.models.user import User
from app.models.company import Company
from app.models.role import Role
from app.core.security import create_access_token
from app.core.logging import log_action
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from urllib.parse import quote

class GoogleOAuth:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        # Get base URL from settings
        base_url = settings.BASE_URL
        # Ensure base URL has protocol
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        # Create redirect URI with proper encoding
        self.redirect_uri = quote(f"{base_url}/api/v1/auth/google/callback", safe='')
        # Create HTTP redirect URI for local development
        if base_url.startswith('https://'):
            http_base_url = base_url.replace('https://', 'http://')
            self.http_redirect_uri = quote(f"{http_base_url}/api/v1/auth/google/callback", safe='')
        else:
            self.http_redirect_uri = self.redirect_uri

    def get_auth_url(self, use_https: bool = True) -> str:
        """Get the Google OAuth URL with the appropriate redirect URI."""
        redirect_uri = self.redirect_uri if use_https else self.http_redirect_uri
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope=openid%20email%20profile"
        )

    async def verify_token(self, token: str) -> dict:
        """Verify Google OAuth token and return user info."""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            return idinfo
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

    async def handle_google_auth(self, token: str, db: Session) -> dict:
        """Handle Google authentication and return access token."""
        try:
            # Verify Google token
            user_info = await self.verify_token(token)
            
            # Extract user info
            email = user_info['email']
            name = user_info.get('name', '')
            picture = user_info.get('picture', '')
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                email_domain = email.split('@')[1]
                
                # Create or get company
                company = db.query(Company).filter(Company.domain == email_domain).first()
                if not company:
                    company = Company(
                        name=email_domain.split('.')[0].capitalize(),
                        domain=email_domain,
                        industry="Technology",  # Default industry
                        size="1-50"  # Default size
                    )
                    db.add(company)
                    db.flush()
                
                # Create user
                user = User(
                    email=email,
                    name=name,
                    picture=picture,
                    company_id=company.id,
                    is_google_auth=True
                )
                
                # Add default role
                default_role = db.query(Role).filter(Role.name == "user").first()
                if default_role:
                    user.roles.append(default_role)
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                # Log registration
                log_action(
                    action="google_register",
                    user_id=user.id,
                    details={
                        "email": email,
                        "company_id": company.id
                    }
                )
            
            # Generate access token
            access_token = create_access_token(data={"sub": user.email})
            
            # Log login
            log_action(
                action="google_login",
                user_id=user.id,
                details={"email": email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "picture": user.picture
                }
            }
            
        except IntegrityError as e:
            db.rollback()
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