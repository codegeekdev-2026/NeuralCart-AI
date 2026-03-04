"""
AWS Lambda handler for serverless recommendations
"""
import json
import logging
from app.models import RecommendationRequest, UserContext
from app.agents import recommendation_agent

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Lambda handler for recommendation requests
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        API Gateway formatted response
    """
    try:
        # Parse request
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        user_context = UserContext(
            user_id=body.get('user_id'),
            session_id=body.get('session_id'),
            device_type=body.get('device_type', 'web'),
            location=body.get('location'),
            previous_purchases=body.get('previous_purchases', []),
            cart_items=body.get('cart_items', []),
            browsing_history=body.get('browsing_history', [])
        )
        
        request = RecommendationRequest(
            user_id=body.get('user_id'),
            session_id=body.get('session_id'),
            context=user_context,
            num_recommendations=body.get('num_recommendations', 5)
        )
        
        # Execute recommendation agent
        result = recommendation_agent.execute(request)
        
        # Format response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'recommendations': [rec.dict() for rec in result.recommendations],
                'summary': result.summary,
                'user_segment': body.get('user_id')
            })
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
