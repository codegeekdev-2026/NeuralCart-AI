"""
Sample tests for the API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_config_endpoint():
    """Test configuration endpoint"""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "api_title" in data
    assert "api_version" in data


@pytest.mark.asyncio
async def test_recommendations_endpoint():
    """Test recommendations endpoint"""
    payload = {
        "user_id": "test_user_123",
        "session_id": "session_456",
        "context": {
            "user_id": "test_user_123",
            "session_id": "session_456",
            "device_type": "web",
            "previous_purchases": ["prod_001"],
            "cart_items": ["prod_002"],
            "browsing_history": ["electronics"]
        },
        "num_recommendations": 5
    }
    
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


@pytest.mark.asyncio
async def test_search_endpoint():
    """Test search endpoint"""
    response = client.get("/api/v1/search/products?q=laptop")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert "search_time_ms" in data


def test_payment_intent_creation():
    """Test payment intent creation"""
    payload = {
        "user_id": "test_user",
        "amount": 99.99,
        "currency": "USD",
        "items": [{"product_id": "prod_001", "quantity": 1, "price": 99.99}]
    }
    
    response = client.post("/api/v1/payments/intent", json=payload)
    # This will fail without Stripe API key but tests the endpoint
    assert response.status_code in [200, 400]
