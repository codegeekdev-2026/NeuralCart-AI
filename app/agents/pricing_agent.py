"""
Dynamic Pricing Agent using agentic AI
"""
import logging
from typing import Dict, Any, List, Optional
import openai
from datetime import datetime
from app.config import settings
from app.models import UserContext

logger = logging.getLogger(__name__)


class DynamicPricingAgent:
    """
    Agentic AI for dynamic pricing based on multiple factors:
    - User segment and loyalty
    - Inventory levels
    - Demand signals
    - Competitor pricing
    - Time-based factors
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    def _get_demand_signal(self, product_id: str) -> float:
        """Get current demand signal for product (0 to 1)"""
        # In production, calculate from search volume, cart adds, etc.
        import random
        return random.uniform(0.3, 0.9)
    
    def _get_inventory_level(self, product_id: str) -> float:
        """Get inventory level as percentage (0 to 1)"""
        # In production, query actual inventory
        import random
        return random.uniform(0.1, 0.95)
    
    def _get_competitor_price(self, product_id: str, base_price: float) -> float:
        """Get competitor pricing for product"""
        # In production, fetch from price monitoring service
        variance = 0.95 + (hash(product_id) % 10) / 100
        return base_price * variance
    
    def _calculate_user_segment_multiplier(self, context: UserContext) -> float:
        """Calculate price multiplier based on user segment"""
        purchase_history_length = len(context.previous_purchases)
        
        if purchase_history_length >= 10:
            return 0.95  # 5% discount for VIP customers
        elif purchase_history_length >= 5:
            return 0.97  # 3% discount for regular customers
        elif purchase_history_length > 0:
            return 0.99  # 1% discount for returning customers
        else:
            return 1.0  # No discount for new customers
    
    def calculate_price(self, product_id: str, base_price: float, context: UserContext) -> Dict[str, Any]:
        """
        Calculate dynamic price based on multiple factors
        
        Args:
            product_id: Product identifier
            base_price: Base product price
            context: User context
            
        Returns:
            Pricing information
        """
        try:
            # Get market signals
            demand_signal = self._get_demand_signal(product_id)
            inventory_level = self._get_inventory_level(product_id)
            competitor_price = self._get_competitor_price(product_id, base_price)
            user_multiplier = self._calculate_user_segment_multiplier(context)
            
            # Calculate price adjustments
            demand_adjustment = 1.0 + (demand_signal * 0.1)  # Up to 10% increase based on demand
            inventory_adjustment = 1.0 if inventory_level > 0.5 else (1.0 - (0.5 - inventory_level) * 0.1)  # Decrease if low stock
            competitor_adjustment = 1.0 if base_price <= competitor_price else 0.98  # 2% discount if above competitor
            
            # Calculate final price
            final_price = base_price * demand_adjustment * inventory_adjustment * competitor_adjustment * user_multiplier
            
            # Round to nearest cent
            final_price = round(final_price, 2)
            
            discount_percentage = ((base_price - final_price) / base_price * 100) if base_price > 0 else 0
            
            return {
                'product_id': product_id,
                'base_price': base_price,
                'final_price': final_price,
                'discount_percentage': round(discount_percentage, 2),
                'demand_signal': round(demand_signal, 2),
                'inventory_level': round(inventory_level, 2),
                'competitor_price': round(competitor_price, 2),
                'user_segment_multiplier': round(user_multiplier, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error calculating dynamic price: {e}")
            return {
                'product_id': product_id,
                'base_price': base_price,
                'final_price': base_price,
                'discount_percentage': 0.0,
                'error': str(e)
            }


dynamic_pricing_agent = DynamicPricingAgent()
