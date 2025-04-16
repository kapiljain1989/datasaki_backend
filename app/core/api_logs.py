from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.request_log import RequestLog
from app.services.auth_service import AuthService
from app.utils.logging import logger

class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db: Session = SessionLocal()

        try:
            response = await call_next(request)

            # Extract request details
            method = request.method
            endpoint = request.url.path
            client_ip = request.client.host
            user_agent = request.headers.get("User-Agent", "Unknown")

            # Extract authenticated user (if available)
            user_email = None
            token = request.headers.get("Authorization")
            if token and "Bearer " in token:
                token = token.split("Bearer ")[1]
                user_email = AuthService.get_email_from_token(token)

            # Log request in the database
            log_entry = RequestLog(
                method=method,
                endpoint=endpoint,
                client_ip=client_ip,
                user_email=user_email,
                user_agent=user_agent
            )
            db.add(log_entry)
            db.commit()

            # Log request details in the log file
            logger.info(f"Request: {method} {endpoint} | IP: {client_ip} | User: {user_email} | User-Agent: {user_agent}")

            return response
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}", exc_info=True)
            return await call_next(request)
        finally:
            db.close()
