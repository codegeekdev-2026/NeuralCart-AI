"""
Cart API Integration
"""
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.config import settings
from app.models import Cart, CartItem
import asyncio

logger = logging.getLogger(__name__)


class CartService:
    """Service for cart API integration"""
    
    def __init__(self):
        self.base_url = settings.CART_API_BASE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
    
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


cart_service = CartService()
