from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.request_log import RequestLog
from app.utils.logging import logger
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api-logs")
def get_api_logs(db: Session = Depends(get_db)):
    """Retrieve API access logs."""
    logger.info("Accessing /api-logs endpoint to retrieve API logs.")
    return db.query(RequestLog).order_by(RequestLog.timestamp.desc()).all()
