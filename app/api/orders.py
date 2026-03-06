"""
Order API Routes

Endpoints for creating, retrieving, and managing orders.
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List
import logging
from app.models import (
    Order,
    OrderCreateRequest,
    OrderStatusUpdate,
)
from app.services.order import order_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
