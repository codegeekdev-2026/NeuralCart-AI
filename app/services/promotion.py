"""
Promotion and Pricing Service
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models import Promotion, PromotionResponse
import random

logger = logging.getLogger(__name__)


class PromotionService:
    """Service for managing promotions and dynamic pricing"""
    
    def __init__(self):
        self.active_promotions = {}
        self._initialize_sample_promotions()
    
    def _initialize_sample_promotions(self):
        """Initialize sample promotions"""
        self.active_promotions = {
            'promo_001': {
                'product_id': 'prod_001',
                'discount_percentage': 10,
                'discount_type': 'percentage',
                'discount_value': 10,
                'upsell_product_ids': ['prod_002', 'prod_003'],
                'conditions': {'min_cart_value': 100}
            }
        }
    
    def calculate_promotions(self, user_id: str, cart_items: List[str], total_value: float) -> PromotionResponse:
        """
        Calculate applicable promotions and discounts
        
        Args:
            user_id: User identifier
            cart_items: List of items in cart
            total_value: Total cart value
            
        Returns:
            PromotionResponse with applicable promotions
        """
        promotions = []
        total_savings = 0.0
        
        # Check for applicable promotions based on cart items
        for promo_id, promo_data in self.active_promotions.items():
            if promo_data['product_id'] in cart_items:
                # Check conditions
                if self._check_conditions(promo_data['conditions'], total_value):
                    promotion = Promotion(
                        product_id=promo_data['product_id'],
                        discount_percentage=promo_data['discount_percentage'],
                        discount_type=promo_data['discount_type'],
                        discount_value=promo_data['discount_value'],
                        upsell_product_ids=promo_data['upsell_product_ids'],
                        conditions=promo_data['conditions']
                    )
                    promotions.append(promotion)
                    total_savings += promo_data['discount_value']
        
        # Add upsell opportunities
        for promo in promotions:
            upsell = self._generate_upsell(promo.upsell_product_ids)
            if upsell:
                promo.upsell_product_ids = upsell
        
        confidence = self._calculate_confidence(len(promotions), total_value)
        
        return PromotionResponse(
            promotions=promotions,
            total_potential_savings=total_savings,
            recommendation_confidence=confidence
        )
    
    def _check_conditions(self, conditions: Dict[str, Any], cart_value: float) -> bool:
        """Check if promotion conditions are met"""
        if 'min_cart_value' in conditions:
            return cart_value >= conditions['min_cart_value']
        return True
    
    def _generate_upsell(self, product_ids: List[str]) -> List[str]:
        """Generate upsell recommendations"""
        if product_ids:
            # In production, use ML to rank upsells
            return product_ids[:min(2, len(product_ids))]
        return []
    
    def _calculate_confidence(self, promo_count: int, cart_value: float) -> float:
        """Calculate confidence score for promotions"""
        base_confidence = min(promo_count * 0.3, 0.9)
        if cart_value > 500:
            base_confidence += 0.1
        return min(base_confidence, 1.0)


promotion_service = PromotionService()
