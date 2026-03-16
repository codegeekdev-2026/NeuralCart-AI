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


@router.post("", response_model=Order)
async def create_order(request: OrderCreateRequest):
    """Create a new order

    The request should include a user ID, line items, and total amount.
    """
    try:
        order = order_service.create_order(request)
        return order
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: str = Path(..., description="Order ID")):
    """Retrieve order details by order ID"""
    order = order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/user/{user_id}", response_model=List[Order])
async def list_orders(user_id: str = Path(..., description="User ID")):
    """List all orders for a given user"""
    return order_service.list_orders_by_user(user_id)


@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: str = Path(..., description="Order ID"),
    update: OrderStatusUpdate = None
):
    """Change the status of an order (e.g., pending, shipped, completed)"""
    if not update or not update.status:
        raise HTTPException(status_code=400, detail="Status is required")
    order = order_service.update_order_status(order_id, update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.delete("/{order_id}", response_model=Order)
async def cancel_order(order_id: str = Path(..., description="Order ID")):
    """Cancel an order (marks status as 'canceled')"""
    order = order_service.cancel_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
