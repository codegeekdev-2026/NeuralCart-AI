"""
Agentic AI system for recommendation decisions
"""
import logging
from typing import List, Dict, Any, Optional
import openai
import json
from datetime import datetime
from app.config import settings
from app.models import (
    AgentRecommendation,
    AgentThought,
    Recommendation,
    RecommendationRequest,
    UserContext
)
from app.services import recommendation_service, search_service, promotion_service
from app.utils import embedding_service

logger = logging.getLogger(__name__)


class RecommendationAgent:
    """
    Agentic AI that synthesizes recommendations from multiple services
    and makes intelligent decisions about product suggestions
    """
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.thoughts = []
    
    def _think(self, reasoning: str, confidence: float, next_step: str) -> AgentThought:
        """Record agent thinking process"""
        thought = AgentThought(
            reasoning=reasoning,
            confidence=confidence,
            next_step=next_step
        )
        self.thoughts.append(thought)
        return thought
    
    def _get_product_catalog(self) -> List[Dict[str, Any]]:
        """Get current product catalog"""
        # In production, this would fetch from database
        return [
            {'id': 'prod_001', 'name': 'Premium Laptop', 'category': 'Electronics', 'price': 1299.99},
            {'id': 'prod_002', 'name': 'Wireless Mouse', 'category': 'Accessories', 'price': 49.99},
            {'id': 'prod_003', 'name': 'USB-C Hub', 'category': 'Accessories', 'price': 79.99},
            {'id': 'prod_004', 'name': 'Mechanical Keyboard', 'category': 'Accessories', 'price': 149.99},
        ]
    
    def _analyze_user_behavior(self, context: UserContext) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        analysis = {
            'purchase_frequency': len(context.previous_purchases),
            'browsing_depth': len(context.browsing_history),
            'cart_engagement': len(context.cart_items),
            'user_type': 'new' if not context.previous_purchases else 'returning'
        }
        return analysis
    
    def _evaluate_recommendation_fit(self, product: Dict[str, Any], context: UserContext, user_behavior: Dict[str, Any]) -> float:
        """Evaluate how well a product fits the user"""
        fit_score = 0.0
        
        # Price fit
        if product['price'] < 100 and user_behavior['user_type'] == 'new':
            fit_score += 0.3
        elif product['price'] > 100 and user_behavior['user_type'] == 'returning':
            fit_score += 0.3
        else:
            fit_score += 0.15
        
        # Category fit
        if product['category'] in ['Electronics', 'Accessories']:
            fit_score += 0.2
        
        # Engagement fit
        if user_behavior['browsing_depth'] > 5:
            fit_score += 0.25
        else:
            fit_score += 0.1
        
        # Upsell opportunity
        if user_behavior['purchase_frequency'] > 0:
            fit_score += 0.15
        
        return min(fit_score, 1.0)
    
    def _create_recommendation_reason(self, product: Dict[str, Any], context: UserContext) -> str:
        """Create contextual reason for recommendation"""
        reasons = [
            f"Based on your interest in {context.browsing_history[0] if context.browsing_history else 'similar products'}",
            f"Popular in your browsing category",
            f"Frequently purchased with items in your cart",
            f"Complementary to your recent searches",
            f"Trending among users like you"
        ]
        import random
        return random.choice(reasons)
    
    def execute(self, request: RecommendationRequest) -> AgentRecommendation:
        """
        Execute recommendation agent with multi-step reasoning
        
        Args:
            request: Recommendation request
            
        Returns:
            AgentRecommendation with reasoning and recommendations
        """
        self.thoughts = []  # Reset thoughts for this execution
        
        try:
            # Step 1: Analyze user context
            self._think(
                reasoning=f"Analyzing user {request.user_id} behavior and context",
                confidence=0.95,
                next_step="Evaluate available products"
            )
            
            user_behavior = self._analyze_user_behavior(request.context)
            
            # Step 2: Get product catalog
            self._think(
                reasoning=f"Retrieved {len(self._get_product_catalog())} products from catalog",
                confidence=0.9,
                next_step="Score products against user profile"
            )
            
            products = self._get_product_catalog()
            
            # Step 3: Score and evaluate products
            self._think(
                reasoning="Evaluating product fit using behavioral analysis",
                confidence=0.85,
                next_step="Apply business rules and promotions"
            )
            
            product_scores = []
            for product in products:
                fit_score = self._evaluate_recommendation_fit(product, request.context, user_behavior)
                product_scores.append({
                    'product': product,
                    'fit_score': fit_score
                })
            
            # Sort by fit score
            product_scores.sort(key=lambda x: x['fit_score'], reverse=True)
            
            # Step 4: Apply promotions
            self._think(
                reasoning="Checking for applicable promotions and discounts",
                confidence=0.8,
                next_step="Create final recommendations"
            )
            
            promotions_resp = promotion_service.calculate_promotions(
                user_id=request.user_id,
                cart_items=request.context.cart_items,
                total_value=sum(1 for _ in request.context.cart_items) * 100  # Placeholder
            )
            
            # Step 5: Create recommendations
            self._think(
                reasoning=f"Created {request.num_recommendations} personalized recommendations",
                confidence=0.9,
                next_step="Return agent recommendations"
            )
            
            recommendations = []
            for item in product_scores[:request.num_recommendations]:
                product = item['product']
                fit_score = item['fit_score']
                
                recommendation = Recommendation(
                    product_id=product['id'],
                    product_name=product['name'],
                    score=fit_score,
                    reason=self._create_recommendation_reason(product, request.context),
                    price=product['price'],
                    category=product['category'],
                    discount_available=None
                )
                recommendations.append(recommendation)
            
            # Create summary
            summary = f"Recommended {len(recommendations)} products based on user behavior analysis. " \
                     f"User segment: {user_behavior['user_type']}. Engagement level: " \
                     f"{'High' if user_behavior['browsing_depth'] > 5 else 'Medium' if user_behavior['browsing_depth'] > 2 else 'Low'}"
            
            return AgentRecommendation(
                recommendations=recommendations,
                agent_reasoning=self.thoughts,
                summary=summary
            )
        
        except Exception as e:
            logger.error(f"Error executing recommendation agent: {e}")
            self._think(
                reasoning=f"Error during execution: {str(e)}",
                confidence=0.0,
                next_step="Return empty recommendations"
            )
            return AgentRecommendation(
                recommendations=[],
                agent_reasoning=self.thoughts,
                summary="Error during recommendation generation"
            )


recommendation_agent = RecommendationAgent()
