"""
Payment API endpoints
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional, Dict, Any
import logging
from app.models import PaymentRequest, PaymentResponse
from app.integrations import payment_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/intent", response_model=Dict[str, Any])
async def create_payment_intent(request: PaymentRequest):
    """
    Create a payment intent for client-side processing
    
    Args:
        request: Payment request
        
    Returns:
        Payment intent with client secret
    """
    try:
        # ensure order_id is included in metadata for webhook processing
        if request.order_id:
            request.metadata = request.metadata or {}
            request.metadata["order_id"] = request.order_id

        intent = payment_service.create_payment_intent(request)
        return intent
    
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


