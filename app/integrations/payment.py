"""
Payment Service Integration
"""
import logging
from typing import Dict, Any, Optional, List
import stripe
from app.config import settings
from app.models import PaymentRequest, PaymentResponse
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment processing integration"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.PAYMENT_WEBHOOK_SECRET
    
    def create_payment_intent(self, request: PaymentRequest) -> Dict[str, Any]:
        """
        Create a Stripe payment intent
        
        Args:
            request: Payment request
            
        Returns:
            Payment intent details
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.lower(),
                metadata={
                    'user_id': request.user_id,
                    'items': str(request.items),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Created payment intent {intent.id} for user {request.user_id}")
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': request.amount,
                'currency': request.currency,
                'status': intent.status
            }
        
        except stripe.error.CardError as e:
            logger.error(f"Card error: {e.user_message}")
            raise
        except stripe.error.RateLimitError:
            logger.error("Too many requests to Stripe API")
            raise
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid Stripe request: {e}")
            raise
        except stripe.error.AuthenticationError:
            logger.error("Authentication error with Stripe")
            raise
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment
        
        Args:
            request: Payment request
            
        Returns:
            Payment response
        """
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(request.amount * 100),
                currency=request.currency.lower(),
                metadata={
                    'user_id': request.user_id,
                    'items': str(request.items)
                }
            )
            
            if intent.status == 'succeeded':
                transaction_id = intent.id
                status = 'completed'
            elif intent.status == 'requires_payment_method':
                transaction_id = intent.id
                status = 'pending'
            else:
                transaction_id = intent.id
                status = intent.status
            
            return PaymentResponse(
                transaction_id=transaction_id,
                status=status,
                amount=request.amount
            )
        
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return PaymentResponse(
                transaction_id=str(uuid.uuid4()),
                status='failed',
                amount=request.amount
            )
    
    def verify_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Webhook payload
            sig_header: Signature header
            
        Returns:
            Event data
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError:
            logger.error("Invalid webhook payload")
            raise
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise
    
    def handle_payment_webhook(self, event: Dict[str, Any]) -> None:
        """
        Handle Stripe webhook event
        
        Args:
            event: Stripe event
        """
        event_type = event['type']
        
        if event_type == 'payment_intent.succeeded':
            intent = event['data']['object']
            logger.info(f"Payment succeeded: {intent['id']}")
            # Update order status in database
        
        elif event_type == 'payment_intent.payment_failed':
            intent = event['data']['object']
            logger.error(f"Payment failed: {intent['id']}")
            # Send notification to user
        
        elif event_type == 'charge.refunded':
            charge = event['data']['object']
            logger.info(f"Charge refunded: {charge['id']}")
            # Update refund status


payment_service = PaymentService()
