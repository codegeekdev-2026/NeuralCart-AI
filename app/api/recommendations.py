"""
Recommendation API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from app.models import (
    RecommendationRequest,
    RecommendationResponse,
    UserContext
)
from app.agents import recommendation_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get product recommendations for a user
    
    Args:
        request: Recommendation request with user context
        
    Returns:
        Personalized product recommendations
    """
    try:
        # Execute recommendation agent
        agent_result = recommendation_agent.execute(request)
        
        # Convert agent result to API response
        response = RecommendationResponse(
            recommendations=agent_result.recommendations,
            user_segment=agent_result.summary.split(':')[0] if agent_result.summary else None
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detailed")
async def get_detailed_recommendations(request: RecommendationRequest):
    """
    Get detailed recommendations with agent reasoning
    
    Args:
        request: Recommendation request
        
    Returns:
        Agent recommendations with reasoning
    """
    try:
        agent_result = recommendation_agent.execute(request)
        return agent_result.dict()
    
    except Exception as e:
        logger.error(f"Error getting detailed recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_recommendations(
    user_id: str,
    num_recommendations: int = Query(default=5, le=20, ge=1),
    session_id: Optional[str] = None
):
    """
    Get recommendations for a specific user (simplified)
    
    Args:
        user_id: User identifier
        num_recommendations: Number of recommendations
        session_id: Session identifier
        
    Returns:
        Recommendations
    """
    try:
        # Create basic request
        context = UserContext(
            user_id=user_id,
            session_id=session_id or user_id,
            device_type="web",
            previous_purchases=[],
            cart_items=[],
            browsing_history=[]
        )
        
        request = RecommendationRequest(
            user_id=user_id,
            session_id=session_id or user_id,
            context=context,
            num_recommendations=num_recommendations
        )
        
        agent_result = recommendation_agent.execute(request)
        
        return {
            "recommendations": [rec.dict() for rec in agent_result.recommendations],
            "summary": agent_result.summary
        }
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
