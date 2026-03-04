"""
Cart API Routes

Provides endpoints for cart management including:
- Get, create, update, delete cart operations
- Item management (add, remove, update quantity)
- Cart validation and summaries
- Promotion and coupon application
- Cart merging and delivery estimation
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
from app.models import (
    Cart, CartItem, CartResponse, CartValidationResult,
    CartAddRequest, CartUpdateRequest
)
from app.integrations.cart import cart_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.get("/{user_id}", response_model=CartResponse)
async def get_cart(user_id: str = Path(..., description="User ID")):
    """
    Get user's cart
    
    Returns:
        Cart object with all items and totals
    """
    try:
        cart = await cart_service.get_cart(user_id)
        if not cart:
            raise HTTPException(
                status_code=404,
                detail=f"Cart not found for user {user_id}"
            )
        
        return CartResponse(
            success=True,
            cart=cart,
            message="Cart retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/items", response_model=CartResponse)
async def add_item_to_cart(
    user_id: str = Path(..., description="User ID"),
    item: CartAddRequest = None
):
    """
    Add item to cart
    
    Args:
        user_id: User ID
        item: Cart item details (product_id, quantity, price)
    
    Returns:
        Updated cart
    """
    try:
        if not item:
            raise HTTPException(status_code=400, detail="Item data required")
        
        success = await cart_service.add_to_cart(
            user_id,
            item.product_id,
            item.quantity,
            item.price or 0
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add item to cart")
        
        cart = await cart_service.get_cart(user_id)
        return CartResponse(
            success=True,
            cart=cart,
            message=f"Item {item.product_id} added successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/items/{product_id}", response_model=CartResponse)
async def update_item_quantity(
    user_id: str = Path(..., description="User ID"),
    product_id: str = Path(..., description="Product ID"),
    update: CartUpdateRequest = None
):
    """
    Update quantity of item in cart
    
    Args:
        user_id: User ID
        product_id: Product ID
        update: New quantity
    
    Returns:
        Updated cart
    """
    try:
        if not update:
            raise HTTPException(status_code=400, detail="Update data required")
        
        success = await cart_service.update_item_quantity(
            user_id,
            product_id,
            update.quantity
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update item quantity")
        
        cart = await cart_service.get_cart(user_id)
        return CartResponse(
            success=True,
            cart=cart,
            message=f"Product {product_id} quantity updated to {update.quantity}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item quantity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/items/{product_id}", response_model=CartResponse)
async def remove_item_from_cart(
    user_id: str = Path(..., description="User ID"),
    product_id: str = Path(..., description="Product ID")
):
    """
    Remove item from cart
    
    Args:
        user_id: User ID
        product_id: Product ID to remove
    
    Returns:
        Updated cart
    """
    try:
        success = await cart_service.remove_from_cart(user_id, product_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to remove item from cart")
        
        cart = await cart_service.get_cart(user_id)
        return CartResponse(
            success=True,
            cart=cart,
            message=f"Product {product_id} removed from cart"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=Dict[str, Any])
async def clear_cart(user_id: str = Path(..., description="User ID")):
    """
    Clear entire cart
    
    Args:
        user_id: User ID
    
    Returns:
        Confirmation message
    """
    try:
        success = await cart_service.clear_cart(user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to clear cart")
        
        return {
            "success": True,
            "message": "Cart cleared successfully",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/summary", response_model=Dict[str, Any])
async def get_cart_summary(user_id: str = Path(..., description="User ID")):
    """
    Get detailed cart summary with item breakdown
    
    Returns:
        Cart summary including items, totals, discounts
    """
    try:
        summary = await cart_service.get_cart_summary(user_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        summary["success"] = True
        summary["timestamp"] = datetime.utcnow().isoformat()
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cart summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/validate", response_model=CartValidationResult)
async def validate_cart(user_id: str = Path(..., description="User ID")):
    """
    Validate cart for issues, warnings, and suggestions
    
    Returns:
        Validation result with errors, warnings, and suggestions
    """
    try:
        result = await cart_service.validate_cart(user_id)
        return result
    except Exception as e:
        logger.error(f"Error validating cart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/apply-coupon", response_model=Dict[str, Any])
async def apply_coupon(
    user_id: str = Path(..., description="User ID"),
    coupon_code: str = Query(..., description="Coupon code")
):
    """
    Apply coupon/promotion code to cart
    
    Args:
        user_id: User ID
        coupon_code: Promotion code
    
    Returns:
        Result with discount information
    """
    try:
        if not coupon_code:
            raise HTTPException(status_code=400, detail="Coupon code required")
        
        result = await cart_service.apply_coupon(user_id, coupon_code)
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying coupon: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/merge", response_model=Dict[str, Any])
async def merge_carts(
    user_id: str = Path(..., description="Target user ID"),
    source_user_id: str = Query(..., description="Source user ID to merge from")
):
    """
    Merge another user's cart into this user's cart
    
    Useful for guest to registered user account migration
    
    Args:
        user_id: Target user ID (receives items)
        source_user_id: Source user ID (items will be moved)
    
    Returns:
        Merge result with count of merged items
    """
    try:
        if not source_user_id:
            raise HTTPException(status_code=400, detail="Source user ID required")
        
        if user_id == source_user_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot merge cart with itself"
            )
        
        result = await cart_service.merge_carts(user_id, source_user_id)
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error merging carts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/delivery-estimate", response_model=Dict[str, Any])
async def estimate_delivery(
    user_id: str = Path(..., description="User ID"),
    days: int = Query(default=3, ge=1, le=30, description="Delivery days")
):
    """
    Estimate delivery date for cart items
    
    Args:
        user_id: User ID
        days: Number of days for delivery (1-30, default 3)
    
    Returns:
        Delivery estimate with date and details
    """
    try:
        result = await cart_service.estimate_delivery(user_id, days)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        result["success"] = True
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating delivery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/batch-add", response_model=Dict[str, Any])
async def batch_add_items(
    user_id: str = Path(..., description="User ID"),
    items: List[CartAddRequest] = None
):
    """
    Add multiple items to cart in bulk
    
    Args:
        user_id: User ID
        items: List of items to add
    
    Returns:
        Batch operation result with success/failure counts
    """
    try:
        if not items:
            raise HTTPException(status_code=400, detail="Items list required")
        
        items_list = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price or 0
            }
            for item in items
        ]
        
        result = await cart_service.batch_add_items(user_id, items_list)
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch add: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/recalculate", response_model=Dict[str, Any])
async def recalculate_totals(user_id: str = Path(..., description="User ID")):
    """
    Recalculate cart totals after price changes
    
    Args:
        user_id: User ID
    
    Returns:
        Confirmation of recalculation
    """
    try:
        success = await cart_service.recalculate_total(user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to recalculate totals")
        
        cart = await cart_service.get_cart(user_id)
        
        return {
            "success": True,
            "message": "Cart totals recalculated",
            "user_id": user_id,
            "new_total": cart.total_price if cart else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating totals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/items", response_model=Dict[str, Any])
async def get_cart_items(
    user_id: str = Path(..., description="User ID"),
    product_id: Optional[str] = Query(None, description="Filter by product ID")
):
    """
    Get items in cart with optional filtering
    
    Args:
        user_id: User ID
        product_id: Optional product ID to filter
    
    Returns:
        List of cart items
    """
    try:
        cart = await cart_service.get_cart(user_id)
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        items = cart.items if cart.items else []
        
        # Filter by product_id if provided
        if product_id:
            items = [item for item in items if item.product_id == product_id]
        
        return {
            "success": True,
            "user_id": user_id,
            "item_count": len(items),
            "items": items,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cart items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/total", response_model=Dict[str, Any])
async def get_cart_total(user_id: str = Path(..., description="User ID")):
    """
    Get cart total amount
    
    Returns:
        Cart total with breakdown
    """
    try:
        total = await cart_service.get_cart_total(user_id)
        cart = await cart_service.get_cart(user_id)
        
        if cart is None:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        return {
            "success": True,
            "user_id": user_id,
            "subtotal": cart.subtotal or 0,
            "discount": cart.discount_amount or 0,
            "total": total,
            "item_count": len(cart.items) if cart.items else 0,
            "currency": "USD",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cart total: {e}")
        raise HTTPException(status_code=500, detail=str(e))
