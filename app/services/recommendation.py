"""
Recommendation Service with AI-powered logic
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
import json
from app.config import settings
from app.models import (
    Recommendation, 
    RecommendationResponse, 
    UserContext,
    RecommendationRequest
)
from app.utils import embedding_service, vector_db

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating personalized product recommendations"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.min_confidence = settings.MIN_RECOMMENDATION_CONFIDENCE
        self.max_recommendations = settings.MAX_RECOMMENDATIONS
    
    def _build_user_profile(self, context: UserContext) -> str:
        """Build user profile from context"""
        profile = f"""
        User ID: {context.user_id}
        Device: {context.device_type}
        Previous Purchases: {', '.join(context.previous_purchases) or 'None'}
        Cart Items: {', '.join(context.cart_items) or 'None'}
        Browsing History: {', '.join(context.browsing_history[:5]) or 'None'}
        """
        return profile
    
    def _get_relevant_products(self, context: UserContext, limit: int = 50) -> List[Dict[str, Any]]:
        """Get relevant products based on user context"""
        # For demonstration, this would query product catalog
        # In production, this would integrate with product database
        products = [
            {
                'id': 'prod_001',
                'name': 'Premium Laptop',
                'category': 'Electronics',
                'price': 1299.99,
                'description': 'High-performance laptop for professionals'
            },
            {
                'id': 'prod_002',
                'name': 'Wireless Mouse',
                'category': 'Accessories',
                'price': 49.99,
                'description': 'Ergonomic wireless mouse'
            },
            {
                'id': 'prod_003',
                'name': 'USB-C Hub',
                'category': 'Accessories',
                'price': 79.99,
                'description': 'Multi-port USB-C hub for connectivity'
            },
        ]
        return products[:limit]
    
    def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Generate personalized product recommendations using AI
        
        Args:
            request: Recommendation request with user context
            
        Returns:
            RecommendationResponse with recommended products
        """
        try:
            user_profile = self._build_user_profile(request.context)
            products = self._get_relevant_products(request.context)
            
            # Generate embedding for user profile
            user_embedding = embedding_service.get_embedding(user_profile)
            
            # Find similar products using vector search
            recommendations_list = []
            
            for product in products:
                product_text = f"{product.get('name', '')} {product.get('description', '')} {product.get('category', '')}"
                product_embedding = embedding_service.get_embedding(product_text)
                
                similarity = embedding_service.similarity(user_embedding, product_embedding)
                
                if similarity >= self.min_confidence:
                    recommendation = Recommendation(
                        product_id=product['id'],
                        product_name=product['name'],
                        score=similarity,
                        reason=f"This {product.get('category', 'product')} matches your preferences based on your browsing history",
                        price=product['price'],
                        category=product.get('category', 'Unknown'),
                        discount_available=self._calculate_discount(product)
                    )
                    recommendations_list.append(recommendation)
            
            # Sort by score and limit
            recommendations_list.sort(key=lambda x: x.score, reverse=True)
            recommendations_list = recommendations_list[:request.num_recommendations]
            
            return RecommendationResponse(
                recommendations=recommendations_list,
                user_segment=self._classify_user_segment(request.context)
            )
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return RecommendationResponse(recommendations=[])
    
    def _calculate_discount(self, product: Dict[str, Any]) -> Optional[float]:
        """Calculate applicable discount for product"""
        # In production, this would check promotion rules
        base_discount = 0
        if product.get('price', 0) > 100:
            base_discount = 0.05  # 5% discount for expensive items
        return base_discount if base_discount > 0 else None
    
    def _classify_user_segment(self, context: UserContext) -> str:
        """Classify user into segment based on context"""
        purchase_count = len(context.previous_purchases)
        cart_value = len(context.cart_items)
        
        if purchase_count >= 10:
            return "VIP"
        elif purchase_count >= 5:
            return "Regular"
        elif purchase_count > 0:
            return "Returning"
        else:
            return "New"


recommendation_service = RecommendationService()
