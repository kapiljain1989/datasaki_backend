from datetime import datetime
from sqlalchemy.orm import Session
from app.models.log import Log
from app.db.database import SessionLocal
from typing import Optional, Dict, Any
from app.utils.logging import logger

def log_action(
    action: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None
) -> None:
    """
    Log an action to both the database and the application logger.
    
    Args:
        action: The type of action being logged
        user_id: The ID of the user performing the action
        details: Additional details about the action
        db: Optional database session. If not provided, a new session will be created.
    """
    # Log to application logger
    log_message = f"Action: {action}"
    if user_id:
        log_message += f" | User ID: {user_id}"
    if details:
        log_message += f" | Details: {details}"
    logger.info(log_message)
    
    # Log to database
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True
    
    try:
        log_entry = Log(
            action=action,
            user_id=user_id,
            details=details or {},
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to log action to database: {str(e)}")
        raise e
    finally:
        if should_close_db:
            db.close() 