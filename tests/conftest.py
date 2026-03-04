"""Tests package"""
import pytest


@pytest.fixture
def sample_user_context():
    """Create sample user context for testing"""
    return {
        "user_id": "test_user_123",
        "session_id": "session_456",
        "device_type": "web",
        "location": "US",
        "previous_purchases": ["prod_001", "prod_002"],
        "cart_items": ["prod_003"],
        "browsing_history": ["electronics", "accessories"]
    }


@pytest.fixture
def sample_product():
    """Create sample product for testing"""
    return {
        "id": "prod_001",
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "category": "Electronics"
    }
