# Cart API Quick Reference

## Base URL
```
/api/v1/cart/{user_id}
```

## Quick Endpoints Reference

### Cart Operations (5)
```
GET    /{user_id}                         - Get cart
POST   /{user_id}/items                   - Add item
PUT    /{user_id}/items/{product_id}     - Update quantity
DELETE /{user_id}/items/{product_id}     - Remove item
DELETE /{user_id}                         - Clear cart
```

### Info & Analysis (4)
```
GET    /{user_id}/summary                 - Get summary
GET    /{user_id}/total                   - Get total
GET    /{user_id}/items                   - List items
POST   /{user_id}/validate                - Validate cart
```

### Advanced Features (5)
```
POST   /{user_id}/apply-coupon            - Apply promotion
POST   /{user_id}/merge                   - Merge carts
GET    /{user_id}/delivery-estimate       - Estimate delivery
POST   /{user_id}/batch-add               - Bulk add items
POST   /{user_id}/recalculate             - Recalculate totals
```

## Common Request Examples

### Add Single Item
```bash
curl -X POST http://localhost:8000/api/v1/cart/user123/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod123",
    "quantity": 1,
    "price": 99.99
  }'
```

### Update Quantity
```bash
curl -X PUT http://localhost:8000/api/v1/cart/user123/items/prod123 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 5}'
```

### Apply Coupon
```bash
curl -X POST "http://localhost:8000/api/v1/cart/user123/apply-coupon?coupon_code=SAVE10"
```

### Batch Add Items
```bash
curl -X POST http://localhost:8000/api/v1/cart/user123/batch-add \
  -H "Content-Type: application/json" \
  -d '[
    {"product_id": "prod1", "quantity": 1, "price": 29.99},
    {"product_id": "prod2", "quantity": 2, "price": 49.99}
  ]'
```

### Get Cart Summary
```bash
curl http://localhost:8000/api/v1/cart/user123/summary
```

### Validate Cart
```bash
curl -X POST http://localhost:8000/api/v1/cart/user123/validate
```

### Estimate Delivery
```bash
curl "http://localhost:8000/api/v1/cart/user123/delivery-estimate?days=3"
```

### Merge Carts (Guest to User)
```bash
curl -X POST "http://localhost:8000/api/v1/cart/user123/merge?source_user_id=guest456"
```

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request / Operation failed |
| 404 | Cart not found |
| 500 | Server error |

## Data Models

### CartItem
```python
{
  "product_id": "string",          # Required
  "product_name": "string",        # Optional
  "quantity": 1,                   # Required: >= 1
  "price": 99.99,                  # Required: >= 0
  "discount_percentage": 10,       # Optional: 0-100
  "total": 99.99,                  # Calculated
  "added_at": "2024-01-15T10:00Z"  # Timestamp
}
```

### Cart
```python
{
  "user_id": "string",
  "items": [...],                  # List of CartItem
  "subtotal": 199.98,
  "discount_amount": 20,
  "total_price": 179.98,
  "item_count": 2,
  "coupon_code": "SAVE10",
  "coupon_discount": 20,
  "estimated_delivery": "2024-01-18T00:00Z",
  "last_updated": "2024-01-15T10:00Z",
  "abandoned": false,
  "abandoned_at": null
}
```

### Validation Result
```python
{
  "valid": true,
  "errors": [],
  "warnings": ["Cart has many items (25)"],
  "suggestions": ["Consider splitting large order"]
}
```

## Validation Rules

- **Quantity:** Minimum 1, maximum 999
- **Price:** Non-negative, no currency specified (USD assumed)
- **Discount:** 0-100%, percentage values
- **Delivery:** 1-30 days
- **Cart:** Cannot merge with itself

## Key Features

✅ **Core Operations**
- Add/remove/update items
- Clear cart
- Track item timestamps

✅ **Discounts & Promotions**
- Apply coupon codes
- Track discount amounts
- Per-item discounts

✅ **Validation & Analytics**
- Comprehensive cart validation
- Error detection (duplicates, invalid prices)
- Warnings for large orders

✅ **Advanced Features**
- Batch add multiple items
- Merge guest/user carts
- Delivery estimation
- Cart total recalculation

✅ **Data Integrity**
- Type validation
- Range validation
- Duplicate detection
- Abandoned cart tracking

## Error Examples

### Invalid Quantity
```json
{
  "detail": "Failed to update item quantity"
}
```

### Cart Not Found
```json
{
  "detail": "Cart not found for user user123"
}
```

### Invalid Coupon
```json
{
  "success": false,
  "error": "Coupon not found or expired"
}
```

### Merge Error
```json
{
  "detail": "Cannot merge cart with itself"
}
```

## Performance Tips

1. **Use batch-add** for multiple items instead of individual requests
2. **Cache cart summary** on client side when possible
3. **Validate before checkout** to catch issues early
4. **Merge carts** when converting guest to registered user
5. **Recalculate totals** after price updates

## Integration Notes

- All operations are **async** for performance
- **CORS enabled** for frontend integration
- **Gzip compression** enabled for responses
- **Error logging** on all operations
- **Full type hints** for IDE support

## Documentation Files

- **CART_API.md** - Complete endpoint documentation
- **CART_IMPROVEMENTS.md** - Feature breakdown
- **CART_SYSTEM_SUMMARY.md** - High-level overview
- **This file** - Quick reference guide

## Testing with Python

```python
import httpx
import asyncio

async def test_cart():
    async with httpx.AsyncClient() as client:
        # Add item
        response = await client.post(
            "http://localhost:8000/api/v1/cart/user123/items",
            json={
                "product_id": "prod001",
                "quantity": 1,
                "price": 99.99
            }
        )
        print(response.json())
        
        # Get summary
        response = await client.get(
            "http://localhost:8000/api/v1/cart/user123/summary"
        )
        print(response.json())

asyncio.run(test_cart())
```

## Next Steps

1. Review full documentation in CART_API.md
2. Test endpoints with provided examples
3. Integrate with frontend/client application
4. Consider implementing inventory checks
5. Set up cart abandonment notifications

---

**Quick Links:**
- [Full API Documentation](CART_API.md)
- [Improvements Summary](CART_IMPROVEMENTS.md)
- [System Overview](CART_SYSTEM_SUMMARY.md)
- [GitHub Repo](https://github.com/codegeekdev/llm-e-commerce)

**Version:** 1.0  
**Last Updated:** January 15, 2024
