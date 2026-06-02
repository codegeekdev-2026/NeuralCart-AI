"""
Promotion API endpoints
"""
from fastapi import APIRouter, HTTPException
import logging
from app.models import PromotionRequest, PromotionResponse
from app.services import promotion_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/promotions", tags=["promotions"])