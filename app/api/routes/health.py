from fastapi import APIRouter
from app.utils.logging import logger
router = APIRouter()

@router.get("/")
def health_check():
    logger.info(f"Application Health Check:OK", exc_info=True)
    return {"status": "ok"}
