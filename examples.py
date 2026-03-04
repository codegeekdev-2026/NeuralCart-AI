"""
API Integration Examples
Shows how to use the E-commerce Personalization Platform API
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


class EcommercePlatformClient:
    """Client for E-commerce Personalization Platform"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
    
    def get_recommendations(self, user_id: str, num_recommendations: int = 5) -> Dict[str, Any]:
        """Get personalized recommendations"""
        payload = {
            "user_id": user_id,
            "session_id": f"session_{user_id}",
            "context": {
                "user_id": user_id,
                "session_id": f"session_{user_id}",
                "device_type": "web",
                "previous_purchases": [],
                "cart_items": [],
                "browsing_history": ["electronics"]
            },
            "num_recommendations": num_recommendations
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/recommendations",
            json=payload
        )
        return response.json()
    
    def search_products(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for products"""
        response = self.session.get(
            f"{self.base_url}/api/v1/search/products",
            params={"q": query, "limit": limit}
        )
        return response.json()
    
    def create_payment_intent(self, user_id: str, amount: float) -> Dict[str, Any]:
        """Create payment intent"""
        payload = {
            "user_id": user_id,
            "amount": amount,
            "currency": "USD",
            "items": [{"product_id": "prod_001", "quantity": 1, "price": amount}]
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/payments/intent",
            json=payload
        )
        return response.json()


def main():
    """Example usage"""
    
    # Initialize client
    client = EcommercePlatformClient()
    
    print("=" * 60)
    print("E-commerce Personalization Platform - API Examples")
    print("=" * 60)
    
    # 1. Health check
    print("\n1. Health Check")
    print("-" * 60)
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # 2. Get recommendations
    print("\n2. Get Recommendations")
    print("-" * 60)
    recommendations = client.get_recommendations("user_123", num_recommendations=5)
    print(json.dumps(recommendations, indent=2, default=str))
    
    # 3. Search products
    print("\n3. Search Products")
    print("-" * 60)
    search_results = client.search_products("laptop", limit=5)
    print(json.dumps(search_results, indent=2, default=str))
    
    # 4. Create payment intent
    print("\n4. Create Payment Intent")
    print("-" * 60)
    payment = client.create_payment_intent("user_123", 99.99)
    print(json.dumps(payment, indent=2, default=str))
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
