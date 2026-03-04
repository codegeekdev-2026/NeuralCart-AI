"""
Pydantic schemas for request/response models
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Product Models
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    embedding: Optional[List[float]] = None
    tags: List[str] = []
    inventory: int = 0
    image_url: Optional[str] = None
    
    class Config:
        extra = "allow"


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    inventory: Optional[int] = None


class ProductSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(default=10, le=100)
    offset: int = Field(default=0, ge=0)


class ProductSearchResponse(BaseModel):
    products: List[Product]
    total: int
    limit: int
    offset: int


# User Models
class UserPreference(BaseModel):
    user_id: str
    browsing_history: List[str] = []
    purchase_history: List[str] = []
    preferences: Dict[str, Any] = {}
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class UserContext(BaseModel):
    user_id: str
    session_id: str
    device_type: str
    location: Optional[str] = None
    previous_purchases: List[str] = []
    cart_items: List[str] = []
    browsing_history: List[str] = []


# Recommendation Models
class RecommendationRequest(BaseModel):
    user_id: str
    session_id: str
    context: UserContext
    num_recommendations: int = Field(default=5, le=20)
    include_reasons: bool = True


class Recommendation(BaseModel):
    product_id: str
    product_name: str
    score: float
    reason: str
    price: float
    category: str
    discount_available: Optional[float] = None


class RecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    user_segment: Optional[str] = None


# Promotion Models
class Promotion(BaseModel):
    product_id: str
    discount_percentage: float = Field(le=100, ge=0)
    discount_type: str  # fixed or percentage
    discount_value: float
    upsell_product_ids: List[str] = []
    conditions: Dict[str, Any] = {}


class PromotionResponse(BaseModel):
    promotions: List[Promotion]
    total_potential_savings: float
    recommendation_confidence: float


# Payment Models
class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "USD"
    items: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Cart Models
class CartItem(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)
    discount_percentage: Optional[float] = Field(default=0, ge=0, le=100)
    total: Optional[float] = None
    added_at: datetime = Field(default_factory=datetime.utcnow)


class CartAddRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1)
    price: Optional[float] = None


class CartUpdateRequest(BaseModel):
    quantity: int = Field(ge=1)


class Cart(BaseModel):
    user_id: str
    items: List[CartItem] = []
    subtotal: float = Field(default=0.0, ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    total_price: float = Field(default=0.0, ge=0)
    item_count: int = Field(default=0, ge=0)
    coupon_code: Optional[str] = None
    coupon_discount: Optional[float] = None
    estimated_delivery: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    abandoned: bool = False
    abandoned_at: Optional[datetime] = None


class CartResponse(BaseModel):
    success: bool
    cart: Optional[Cart] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CartValidationResult(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []


# Agent Recommendation Models
class AgentThought(BaseModel):
    reasoning: str
    confidence: float
    next_step: str


class AgentRecommendation(BaseModel):
    recommendations: List[Recommendation]
    agent_reasoning: List[AgentThought]
    summary: str


# Search Models
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    search_type: str = "hybrid"  # vector, keyword, hybrid
    limit: int = Field(default=10, le=100)


class SearchResult(BaseModel):
    items: List[Dict[str, Any]]
    total_count: int
    search_time_ms: float


# Health Check Models
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str]
