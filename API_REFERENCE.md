# API Reference

Complete API documentation for the E-commerce Personalization Platform.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses environment-based authentication. In production, implement:
- JWT tokens
- API keys
- OAuth 2.0

## Response Format

All responses follow standard format:

```json
{
  "data": {},
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123"
}
```

## Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Endpoints

### Health & Status

#### Health Check
```http
GET /health
```

Returns API health status and service availability.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "services": {
    "api": "running",
    "vector_db": "running",
    "elasticsearch": "running",
    "stripe": "connected"
  }
}
```

#### Readiness Check
```http
GET /ready
```

Check if API is ready to serve requests.

**Response 200:**
```json
{
  "ready": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

#### Configuration
```http
GET /config
```

Get non-sensitive configuration.

---

### Recommendations API

#### Get Recommendations
```http
POST /api/v1/recommendations
Content-Type: application/json

{
  "user_id": "user_123",
  "session_id": "session_456",
  "context": {
    "user_id": "user_123",
    "session_id": "session_456",
    "device_type": "web",
    "location": "US",
    "previous_purchases": ["prod_001"],
    "cart_items": ["prod_002"],
    "browsing_history": ["electronics"]
  },
  "num_recommendations": 5,
  "include_reasons": true
}
```

**Response 200:**
```json
{
  "recommendations": [
    {
      "product_id": "prod_003",
      "product_name": "Wireless Mouse",
      "score": 0.85,
      "reason": "Based on your interest in electronics",
      "price": 49.99,
      "category": "Accessories",
      "discount_available": 0.05
    }
  ],
  "generated_at": "2024-01-15T10:30:00",
  "user_segment": "VIP"
}
```

#### Get Detailed Recommendations with Agent Reasoning
```http
POST /api/v1/recommendations/detailed
```

Same request format, includes agent reasoning process.

**Response 200:**
```json
{
  "recommendations": [...],
  "agent_reasoning": [
    {
      "reasoning": "Analyzing user behavior and context",
      "confidence": 0.95,
      "next_step": "Evaluate available products"
    }
  ],
  "summary": "Recommended 5 products based on user behavior analysis..."
}
```

#### Get User Recommendations (Simplified)
```http
GET /api/v1/recommendations/user/{user_id}?num_recommendations=5&session_id=session_456
```

**Parameters:**
- `user_id` (string, required): User identifier
- `num_recommendations` (integer, optional, default=5): Number of recommendations
- `session_id` (string, optional): Session identifier

---

### Search API

#### Search Products
```http
GET /api/v1/search/products?q=laptop&search_type=hybrid&limit=10&category=Electronics&min_price=500&max_price=2000
```

**Parameters:**
- `q` (string, required): Search query
- `search_type` (string, optional): `keyword`, `vector`, or `hybrid` (default: `hybrid`)
- `limit` (integer, optional): Max results (default: 10, max: 100)
- `category` (string, optional): Filter by category
- `min_price` (number, optional): Minimum price
- `max_price` (number, optional): Maximum price

**Response 200:**
```json
{
  "items": [
    {
      "id": "prod_001",
      "name": "Premium Laptop",
      "description": "High-performance laptop",
      "price": 1299.99,
      "category": "Electronics"
    }
  ],
  "total_count": 42,
  "search_time_ms": 45.3
}
```

#### Advanced Search
```http
POST /api/v1/search/advanced
Content-Type: application/json

{
  "query": "gaming laptop",
  "filters": {
    "category": "Electronics",
    "min_price": 800,
    "max_price": 2000
  },
  "search_type": "hybrid",
  "limit": 10
}
```

#### Trending Products
```http
GET /api/v1/search/trending?limit=10
```

#### Category Recommendations
```http
GET /api/v1/search/recommendations/{category}?limit=5
```

---

### Payment API

#### Create Payment Intent
```http
POST /api/v1/payments/intent
Content-Type: application/json

{
  "user_id": "user_123",
  "amount": 199.99,
  "currency": "USD",
  "items": [
    {
      "product_id": "prod_001",
      "quantity": 1,
      "price": 199.99
    }
  ],
  "metadata": {
    "order_id": "order_123"
  }
}
```

**Response 200:**
```json
{
  "client_secret": "pi_1234..._secret_5678...",
  "payment_intent_id": "pi_1234...",
  "amount": 199.99,
  "currency": "USD",
  "status": "requires_payment_method"
}
```

#### Process Payment
```http
POST /api/v1/payments/process
Content-Type: application/json

{
  "user_id": "user_123",
  "amount": 199.99,
  "currency": "USD",
  "items": [...]
}
```

**Response 200:**
```json
{
  "transaction_id": "txn_1234567890",
  "status": "completed",
  "amount": 199.99,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Payment Webhook
```http
POST /api/v1/payments/webhook
Stripe-Signature: t=1234567...,v1=abcdef...
Content-Type: application/json

{
  "id": "evt_1234...",
  "type": "payment_intent.succeeded",
  "data": {...}
}
```

#### Get Payment Status
```http
GET /api/v1/payments/status/{transaction_id}
```

**Response 200:**
```json
{
  "transaction_id": "txn_1234567890",
  "status": "completed",
  "message": "Payment processed successfully"
}
```

#### Refund Payment
```http
POST /api/v1/payments/refund?transaction_id=txn_1234567890&amount=199.99
```

**Response 200:**
```json
{
  "transaction_id": "txn_1234567890",
  "refund_amount": 199.99,
  "status": "refunded"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid parameters",
  "validation_errors": [
    {
      "field": "user_id",
      "message": "Required field"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found",
  "resource": "user_123"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_id": "err_1234567890"
}
```

---

## Rate Limiting

The API implements rate limiting:

- **Recommendations**: 100 requests/minute per user
- **Search**: 300 requests/minute per user
- **Payments**: 50 requests/minute per user

Rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705316400
```

---

## Pagination

For endpoints returning lists:

```json
{
  "items": [...],
  "total": 1000,
  "limit": 10,
  "offset": 0,
  "pages": 100
}
```

Query parameters:
- `limit`: Items per page (default: 10, max: 100)
- `offset`: Number of items to skip (default: 0)

---

## Request/Response Examples

### cURL

```bash
# Get recommendations
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d @recommendations_request.json

# Search products
curl "http://localhost:8000/api/v1/search/products?q=laptop&limit=10"

# Create payment intent
curl -X POST http://localhost:8000/api/v1/payments/intent \
  -H "Content-Type: application/json" \
  -d @payment_request.json
```

### Python

```python
import requests

client = requests.Client()

# Recommendations
response = client.post(
    "http://localhost:8000/api/v1/recommendations",
    json=recommendation_payload
)

# Search
response = client.get(
    "http://localhost:8000/api/v1/search/products",
    params={"q": "laptop", "limit": 10}
)
```

### JavaScript/TypeScript

```typescript
const response = await fetch(
  'http://localhost:8000/api/v1/recommendations',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  }
);

const data = await response.json();
```

---

## WebSocket Support

Currently not implemented. Planned for real-time updates:

```
ws://localhost:8000/ws/recommendations/{user_id}
```

---

## API Versioning

API version specified in URL: `/api/v1/`

Future versions: `/api/v2/`, `/api/v3/`, etc.

---

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Recommendations API
- Search API
- Payment integration
- Agent-based personalization

---

## Support

For API issues:
1. Check status at `/health`
2. Review request format
3. Check error response code
4. Submit issue with request ID
