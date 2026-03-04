"""
Health check and utility endpoints
"""
from fastapi import APIRouter
from app.config import settings
from app.models import HealthResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    services = {
        "api": "running",
        "vector_db": "running",
        "elasticsearch": "running",
        "stripe": "connected" if settings.STRIPE_API_KEY else "unconfigured",
        "aws": "connected" if settings.AWS_ACCESS_KEY_ID else "unconfigured"
    }
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        services=services
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint
    
    Returns:
        Readiness status
    """
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.API_VERSION
    }


@router.get("/config")
async def get_config():
    """
    Get non-sensitive configuration
    
    Returns:
        Configuration
    """
    return {
        "api_title": settings.API_TITLE,
        "api_version": settings.API_VERSION,
        "debug": settings.DEBUG,
        "embedding_model": settings.EMBEDDING_MODEL,
        "vector_db_type": settings.VECTOR_DB_TYPE,
        "max_recommendations": settings.MAX_RECOMMENDATIONS
    }
