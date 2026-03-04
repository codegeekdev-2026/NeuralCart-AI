"""
Cart API Integration with Enhanced Features
"""
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.models import Cart, CartItem, CartValidationResult
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class CartService:
    """Enhanced service for cart management and API integration"""
    
    def __init__(self):
        self.base_url = settings.CART_API_BASE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        self.max_items_per_product = 999
        self.cart_expiration_days = 7
    
    async def get_cart(self, user_id: str) -> Optional[Cart]:
        """
        Get user's cart
        
        Args:
            user_id: User identifier
            
        Returns:
            Cart object
        """
        try:
            response = await self.client.get(f"/carts/{user_id}")
            if response.status_code == 200:
                data = response.json()
                return Cart(**data)
            return None
        except Exception as e:
            logger.error(f"Error fetching cart: {e}")
            return None
    
    async def add_to_cart(self, user_id: str, product_id: str, quantity: int, price: float) -> bool:
        """
        Add item to cart
        
        Args:
            user_id: User identifier
            product_id: Product ID to add
            quantity: Quantity to add
            price: Product price
            
        Returns:
            Success status
        """
        try:
            payload = {
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            }
            response = await self.client.post(f"/carts/{user_id}/items", json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False
    
    async def remove_from_cart(self, user_id: str, product_id: str) -> bool:
        """
        Remove item from cart
        
        Args:
            user_id: User identifier
            product_id: Product ID to remove
            
        Returns:
            Success status
        """
        try:
            response = await self.client.delete(f"/carts/{user_id}/items/{product_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error removing from cart: {e}")
            return False
    
    async def apply_promotion(self, user_id: str, promotion_code: str) -> Dict[str, Any]:
        """
        Apply promotion code to cart
        
        Args:
            user_id: User identifier
            promotion_code: Promotion code
            
        Returns:
            Promotion result
        """
        try:
            payload = {'code': promotion_code}
            response = await self.client.post(f"/carts/{user_id}/apply-promotion", json=payload)
            if response.status_code == 200:
                return response.json()
            return {'success': False, 'error': 'Failed to apply promotion'}
        except Exception as e:
            logger.error(f"Error applying promotion: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_cart_total(self, user_id: str) -> float:
        """
        Get cart total
        
        Args:
            user_id: User identifier
            
        Returns:
            Total cart value
        """
        try:
            cart = await self.get_cart(user_id)
            if cart:
                return cart.total_price
            return 0.0
        except Exception as e:
            logger.error(f"Error getting cart total: {e}")
            return 0.0
    
    async def clear_cart(self, user_id: str) -> bool:
        """
        Clear user's cart
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            response = await self.client.delete(f"/carts/{user_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error clearing cart: {e}")
            return False
    
    async def update_item_quantity(self, user_id: str, product_id: str, quantity: int) -> bool:
        """
        Update quantity of item in cart
        
        Args:
            user_id: User identifier
            product_id: Product ID
            quantity: New quantity
            
        Returns:
            Success status
        """
        try:
            if quantity < 1:
                return await self.remove_from_cart(user_id, product_id)
            
            if quantity > self.max_items_per_product:
                logger.warning(f"Quantity {quantity} exceeds max {self.max_items_per_product}")
                quantity = self.max_items_per_product
            
            payload = {'quantity': quantity}
            response = await self.client.patch(f"/carts/{user_id}/items/{product_id}", json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error updating item quantity: {e}")
            return False
    
    async def get_cart_item(self, user_id: str, product_id: str) -> Optional[CartItem]:
        """
        Get specific item from cart
        
        Args:
            user_id: User identifier
            product_id: Product ID
            
        Returns:
            CartItem or None
        """
        try:
            cart = await self.get_cart(user_id)
            if cart:
                for item in cart.items:
                    if item.product_id == product_id:
                        return item
            return None
        except Exception as e:
            logger.error(f"Error getting cart item: {e}")
            return None
    
    async def validate_cart(self, user_id: str) -> CartValidationResult:
        """
        Validate cart for issues
        
        Args:
            user_id: User identifier
            
        Returns:
            CartValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        suggestions = []
        
        try:
            cart = await self.get_cart(user_id)
            if not cart:
                errors.append("Cart not found")
                return CartValidationResult(valid=False, errors=errors)
            
            if not cart.items:
                errors.append("Cart is empty")
            
            if cart.total_price < 0:
                errors.append("Cart total is invalid (negative value)")
            
            if cart.total_price == 0 and cart.items:
                errors.append("Cart items exist but total is zero")
            
            # Check for duplicate items (shouldn't exist)
            product_ids = [item.product_id for item in cart.items]
            if len(product_ids) != len(set(product_ids)):
                errors.append("Duplicate items found in cart")
            
            # Warnings
            if len(cart.items) > 20:
                warnings.append(f"Cart has many items ({len(cart.items)}) - consider splitting order")
            
            if cart.total_price > 10000:
                suggestions.append("Large order detected - verify shipping address and timeline")
            
            # Check if cart is abandoned (not updated for days)
            if cart.last_updated:
                days_old = (datetime.utcnow() - cart.last_updated).days
                if days_old > self.cart_expiration_days:
                    warnings.append(f"Cart not updated for {days_old} days")
            
            return CartValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
        except Exception as e:
            logger.error(f"Error validating cart: {e}")
            return CartValidationResult(valid=False, errors=[str(e)])
    
    async def apply_coupon(self, user_id: str, coupon_code: str) -> Dict[str, Any]:
        """
        Apply coupon code to cart
        
        Args:
            user_id: User identifier
            coupon_code: Coupon code
            
        Returns:
            Coupon result with discount info
        """
        return await self.apply_promotion(user_id, coupon_code)
    
    async def get_cart_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed cart summary with statistics
        
        Args:
            user_id: User identifier
            
        Returns:
            Cart summary with statistics
        """
        try:
            cart = await self.get_cart(user_id)
            if not cart:
                return {"error": "Cart not found"}
            
            return {
                "user_id": user_id,
                "item_count": len(cart.items) if cart.items else 0,
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name or "Unknown",
                        "quantity": item.quantity,
                        "unit_price": item.price,
                        "total": item.total or (item.quantity * item.price),
                        "discount": item.discount_percentage or 0
                    } for item in cart.items
                ] if cart.items else [],
                "subtotal": cart.subtotal or 0,
                "discount_amount": cart.discount_amount or 0,
                "total": cart.total_price,
                "coupon": cart.coupon_code,
                "coupon_discount": cart.coupon_discount,
                "last_updated": cart.last_updated.isoformat() if cart.last_updated else None,
                "abandoned": cart.abandoned or False
            }
        except Exception as e:
            logger.error(f"Error getting cart summary: {e}")
            return {"error": str(e)}
    
    async def merge_carts(self, user_id_1: str, user_id_2: str) -> Dict[str, Any]:
        """
        Merge two carts (useful for guest to registered user conversion)
        
        Args:
            user_id_1: Target user ID (receives items)
            user_id_2: Source user ID (items will be moved)
            
        Returns:
            Success result with merge details
        """
        try:
            cart_1 = await self.get_cart(user_id_1)
            cart_2 = await self.get_cart(user_id_2)
            
            if not cart_1:
                logger.error(f"Cart for {user_id_1} not found")
                return {"success": False, "error": f"Cart for {user_id_1} not found"}
            
            if not cart_2:
                logger.error(f"Cart for {user_id_2} not found")
                return {"success": False, "error": f"Cart for {user_id_2} not found"}
            
            merged_count = 0
            
            # Add items from cart_2 to cart_1
            for item in cart_2.items:
                existing = await self.get_cart_item(user_id_1, item.product_id)
                if existing:
                    # Update quantity
                    success = await self.update_item_quantity(
                        user_id_1,
                        item.product_id,
                        existing.quantity + item.quantity
                    )
                    if success:
                        merged_count += 1
                else:
                    # Add new item
                    success = await self.add_to_cart(
                        user_id_1,
                        item.product_id,
                        item.quantity,
                        item.price
                    )
                    if success:
                        merged_count += 1
            
            # Clear cart_2
            await self.clear_cart(user_id_2)
            
            return {
                "success": True,
                "merged_items": merged_count,
                "target_user": user_id_1,
                "source_user": user_id_2
            }
        except Exception as e:
            logger.error(f"Error merging carts: {e}")
            return {"success": False, "error": str(e)}
    
    async def estimate_delivery(self, user_id: str, days: int = 3) -> Dict[str, Any]:
        """
        Estimate delivery date for cart
        
        Args:
            user_id: User identifier
            days: Number of days for delivery
            
        Returns:
            Delivery estimate
        """
        try:
            cart = await self.get_cart(user_id)
            if not cart:
                return {"error": "Cart not found"}
            
            estimated_date = datetime.utcnow() + timedelta(days=days)
            
            return {
                "estimated_delivery": estimated_date.isoformat(),
                "days": days,
                "item_count": len(cart.items) if cart.items else 0,
                "total_value": cart.total_price
            }
        except Exception as e:
            logger.error(f"Error estimating delivery: {e}")
            return {"error": str(e)}
    
    async def batch_add_items(self, user_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple items to cart in bulk
        
        Args:
            user_id: User identifier
            items: List of items with product_id, quantity, price
            
        Returns:
            Batch operation result
        """
        results = {
            "total": len(items),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            for item in items:
                try:
                    success = await self.add_to_cart(
                        user_id,
                        item.get("product_id"),
                        item.get("quantity", 1),
                        item.get("price", 0)
                    )
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to add {item.get('product_id')}")
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Error adding {item.get('product_id')}: {str(e)}")
            
            return results
        except Exception as e:
            logger.error(f"Error in batch add items: {e}")
            results["errors"].append(str(e))
            return results
    
    async def recalculate_total(self, user_id: str) -> bool:
        """
        Recalculate cart total (useful after price changes)
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            payload = {}
            response = await self.client.post(f"/carts/{user_id}/recalculate", json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error recalculating total: {e}")
            return False


cart_service = CartService()
