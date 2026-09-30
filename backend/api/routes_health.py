import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.config import settings
from backend.models.database import get_db
from backend.services.llm.llm_service import llm_service
from backend.utils.logger import logger

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check verifying DB connectivity, LLM provider, and environment settings."""
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    llm_status = "healthy" if llm_service.is_healthy() else "unhealthy"
    demo_mode = settings.is_demo_mode()

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "llm_provider": llm_status,
        "demo_mode": demo_mode,
        "model": settings.GEMINI_MODEL,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "version": "1.0.0",
    }
