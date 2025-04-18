from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role
import json

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip RBAC for public endpoints
        public_paths = [
            "/",
            "/auth/login",
            "/auth/register",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Check if user is set in request state
        if not hasattr(request.state, 'user'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Get user's roles and permissions
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == request.state.user.id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            # Check if user has required permissions
            required_permission = self._get_required_permission(request)
            if not self._has_permission(user, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

            # Add company context to request
            request.state.company_id = user.company_id

            return await call_next(request)
        finally:
            db.close()

    def _get_required_permission(self, request: Request) -> str:
        """Determine required permission based on HTTP method and path"""
        method = request.method
        path = request.url.path

        # Map HTTP methods to CRUD operations
        method_to_operation = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "DELETE": "delete"
        }

        # Get resource type from path
        resource_type = path.split("/")[2]  # Assuming path format: /api/v1/resource_type/...

        return f"{method_to_operation.get(method, 'read')}:{resource_type}"

    def _has_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has the required permission"""
        for role in user.roles:
            permissions = json.loads(role.permissions)
            if required_permission in permissions:
                return True
        return False 