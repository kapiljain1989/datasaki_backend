from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import get_current_user
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from app.core.logging import log_action
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer()

    async def dispatch(self, request: Request, call_next):
        # Skip auth for certain paths
        public_paths = [
            "/",  # Root path
            "/docs",  
            "/redoc",  
            "/api/v1/docs",  # Swagger UI
            "/api/v1/redoc",  # ReDoc
            "/api/v1/openapi.json",  # OpenAPI schema
            "/api/v1/auth/login",  # Login endpoint
            "/api/v1/auth/register",  # Register endpoint
            "/api/v1/auth/google/login",  # Google OAuth login
            "/api/v1/auth/google/callback",  # Google OAuth callback
            "/favicon.ico",  # Favicon
        ]
        
        # Also allow access to static files for documentation
        if (request.url.path in public_paths or 
            request.url.path.startswith(("/static/", "/api/v1/docs/", "/api/v1/redoc/"))):
            return await call_next(request)

        try:
            # Get token from header
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )

            # Get database session
            db: Session = SessionLocal()
            try:
                # Get current user from token
                user = await get_current_user(credentials.credentials, db)
                
                # Log the request
                log_action(
                    action="api_request",
                    user_id=user.id,
                    details={
                        "path": request.url.path,
                        "method": request.method,
                        "ip": request.client.host
                    }
                )
                
                # Add user to request state
                request.state.user = user
                
                # Process request
                response = await call_next(request)
                return response
            finally:
                db.close()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            ) 