# Cart API Documentation

## Overview

The Cart API provides comprehensive cart management functionality for the e-commerce platform. It includes operations for adding/removing items, applying promotions, cart validation, and advanced features like cart merging and batch operations.

## Base URL

```
/api/v1/cart
```

## Endpoints

### 1. Get Cart

**Endpoint:** `GET /{user_id}`

**Description:** Retrieve a user's cart with all items and totals.

**Parameters:**
- `user_id` (path, required): User identifier

**Response:**
```json
{
  "success": true,
  "cart": {
    "user_id": "user123",
    "items": [
      {
        "product_id": "prod001",
        "product_name": "Laptop",
        "quantity": 1,
        "price": 999.99,
        "discount_percentage": 0,
        "total": 999.99,
        "added_at": "2024-01-15T10:30:00"
      }
    ],
    "subtotal": 999.99,
    "discount_amount": 0,
    "total_price": 999.99,
    "item_count": 1,
    "coupon_code": null,
    "last_updated": "2024-01-15T10:30:00"
  },
  "message": "Cart retrieved successfully",
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Cart not found
- `500`: Server error

---

### 2. Add Item to Cart

**Endpoint:** `POST /{user_id}/items`

**Description:** Add a single item to the user's cart.

**Parameters:**
- `user_id` (path, required): User identifier

**Request Body:**
```json
{
  "product_id": "prod001",
  "quantity": 2,
  "price": 99.99
}
```

**Response:** Updated cart (same format as Get Cart)

**Status Codes:**
- `200`: Item added successfully
- `400`: Invalid request or operation failed
- `500`: Server error

---

### 3. Update Item Quantity

**Endpoint:** `PUT /{user_id}/items/{product_id}`

**Description:** Update the quantity of an item in the cart.

**Parameters:**
- `user_id` (path, required): User identifier
- `product_id` (path, required): Product identifier

**Request Body:**
```json
{
  "quantity": 5
}
```

**Response:** Updated cart

**Status Codes:**
- `200`: Quantity updated successfully
- `400`: Invalid quantity or operation failed
- `500`: Server error

**Notes:** If quantity is 0 or less, the item will be removed.

---

### 4. Remove Item from Cart

**Endpoint:** `DELETE /{user_id}/items/{product_id}`

**Description:** Remove a specific item from the user's cart.

**Parameters:**
- `user_id` (path, required): User identifier
- `product_id` (path, required): Product identifier to remove

**Response:**
```json
{
  "success": true,
  "cart": {...},
  "message": "Product prod001 removed from cart",
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Item removed successfully
- `400`: Operation failed
- `500`: Server error

---

### 5. Clear Cart

**Endpoint:** `DELETE /{user_id}`

**Description:** Remove all items from the user's cart.

**Parameters:**
- `user_id` (path, required): User identifier

**Response:**
```json
{
  "success": true,
  "message": "Cart cleared successfully",
  "user_id": "user123",
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Cart cleared successfully
- `400`: Operation failed
- `500`: Server error

---

### 6. Get Cart Summary

**Endpoint:** `GET /{user_id}/summary`

**Description:** Get a detailed summary of the cart with item breakdown.

**Parameters:**
- `user_id` (path, required): User identifier

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "item_count": 2,
  "items": [
    {
      "product_id": "prod001",
      "product_name": "Laptop",
      "quantity": 1,
      "unit_price": 999.99,
      "total": 999.99,
      "discount": 0
    },
    {
      "product_id": "prod002",
      "product_name": "Mouse",
      "quantity": 2,
      "unit_price": 29.99,
      "total": 59.98,
      "discount": 10
    }
  ],
  "subtotal": 1059.97,
  "discount_amount": 106,
  "total": 953.97,
  "coupon": "SAVE10",
  "coupon_discount": 106,
  "last_updated": "2024-01-15T10:30:00",
  "abandoned": false,
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Cart not found
- `500`: Server error

---

### 7. Validate Cart

**Endpoint:** `POST /{user_id}/validate`

**Description:** Validate the cart for errors, warnings, and suggestions.

**Parameters:**
- `user_id` (path, required): User identifier

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Cart has many items (25) - consider splitting order"
  ],
  "suggestions": [
    "Large order detected - verify shipping address and timeline"
  ]
}
```

**Status Codes:**
- `200`: Validation completed
- `404`: Cart not found
- `500`: Server error

**Validation Checks:**
- Cart existence
- Item availability
- Price validity
- Duplicate items
- Cart size warnings
- Order value suggestions
- Abandoned cart warnings

---

### 8. Apply Coupon/Promotion

**Endpoint:** `POST /{user_id}/apply-coupon`

**Description:** Apply a coupon or promotion code to the cart.

**Parameters:**
- `user_id` (path, required): User identifier
- `coupon_code` (query, required): Promotion code

**Example:**
```
POST /api/v1/cart/user123/apply-coupon?coupon_code=SAVE10
```

**Response:**
```json
{
  "success": true,
  "coupon_code": "SAVE10",
  "discount_amount": 50.00,
  "new_total": 949.97,
  "message": "Coupon applied successfully",
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Coupon applied successfully
- `400`: Invalid coupon or operation failed
- `500`: Server error

---

### 9. Merge Carts

**Endpoint:** `POST /{user_id}/merge`

**Description:** Merge another user's cart into this user's cart. Useful for guest-to-registered user conversion.

**Parameters:**
- `user_id` (path, required): Target user ID (receives items)
- `source_user_id` (query, required): Source user ID (items will be moved)

**Example:**
```
POST /api/v1/cart/user123/merge?source_user_id=guest456
```

**Response:**
```json
{
  "success": true,
  "merged_items": 3,
  "target_user": "user123",
  "source_user": "guest456",
  "message": "Carts merged successfully",
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Carts merged successfully
- `400`: Invalid request or operation failed
- `500`: Server error

**Notes:**
- Source cart will be cleared after merge
- Duplicate products will have quantities combined

---

### 10. Estimate Delivery

**Endpoint:** `GET /{user_id}/delivery-estimate`

**Description:** Get estimated delivery date for the cart.

**Parameters:**
- `user_id` (path, required): User identifier
- `days` (query, optional): Delivery days (1-30, default: 3)

**Example:**
```
GET /api/v1/cart/user123/delivery-estimate?days=5
```

**Response:**
```json
{
  "success": true,
  "estimated_delivery": "2024-01-20T10:35:00",
  "days": 5,
  "item_count": 2,
  "total_value": 953.97,
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Cart not found
- `500`: Server error

---

### 11. Batch Add Items

**Endpoint:** `POST /{user_id}/batch-add`

**Description:** Add multiple items to cart in a single operation.

**Parameters:**
- `user_id` (path, required): User identifier

**Request Body:**
```json
[
  {
    "product_id": "prod001",
    "quantity": 1,
    "price": 99.99
  },
  {
    "product_id": "prod002",
    "quantity": 2,
    "price": 29.99
  }
]
```

**Response:**
```json
{
  "total": 2,
  "success": 2,
  "failed": 0,
  "errors": [],
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Batch operation completed
- `400`: Invalid request
- `500`: Server error

---

### 12. Recalculate Totals

**Endpoint:** `POST /{user_id}/recalculate`

**Description:** Recalculate cart totals after price changes or updates.

**Parameters:**
- `user_id` (path, required): User identifier

**Response:**
```json
{
  "success": true,
  "message": "Cart totals recalculated",
  "user_id": "user123",
  "new_total": 953.97,
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Totals recalculated successfully
- `400`: Operation failed
- `500`: Server error

---

### 13. Get Cart Items

**Endpoint:** `GET /{user_id}/items`

**Description:** Get all items in cart with optional filtering.

**Parameters:**
- `user_id` (path, required): User identifier
- `product_id` (query, optional): Filter by product ID

**Example:**
```
GET /api/v1/cart/user123/items?product_id=prod001
```

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "item_count": 2,
  "items": [
    {
      "product_id": "prod001",
      "product_name": "Laptop",
      "quantity": 1,
      "price": 999.99,
      "discount_percentage": 0,
      "total": 999.99,
      "added_at": "2024-01-15T10:30:00"
    }
  ],
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Cart not found
- `500`: Server error

---

### 14. Get Cart Total

**Endpoint:** `GET /{user_id}/total`

**Description:** Get the total amount for the cart with breakdown.

**Parameters:**
- `user_id` (path, required): User identifier

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "subtotal": 1059.97,
  "discount": 106.00,
  "total": 953.97,
  "item_count": 2,
  "currency": "USD",
  "timestamp": "2024-01-15T10:35:00"
}
```

**Status Codes:**
- `200`: Success
- `404`: Cart not found
- `500`: Server error

---

## Error Responses

All errors are returned in the following format:

```json
{
  "detail": "Error description"
}
```

**Common Error Codes:**
- `400 Bad Request`: Invalid input or operation failed
- `404 Not Found`: Cart or resource not found
- `500 Internal Server Error`: Server-side error

---

## Best Practices

1. **Validation**: Always validate cart before checkout using the `/validate` endpoint
2. **Batch Operations**: Use batch-add for multiple items to reduce API calls
3. **Cart Summary**: Get summary before displaying to user to ensure up-to-date totals
4. **Error Handling**: Check response success flag and handle errors appropriately
5. **Caching**: Cache cart data client-side and refresh on user actions

---

## Examples

### Example 1: Add Item and Get Summary
```bash
# Add item
curl -X POST http://localhost:8000/api/v1/cart/user123/items \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod001", "quantity": 1, "price": 99.99}'

# Get summary
curl http://localhost:8000/api/v1/cart/user123/summary
```

### Example 2: Apply Coupon and Get Total
```bash
# Apply coupon
curl -X POST http://localhost:8000/api/v1/cart/user123/apply-coupon?coupon_code=SAVE10

# Get total
curl http://localhost:8000/api/v1/cart/user123/total
```

### Example 3: Batch Add and Validate
```bash
# Batch add items
curl -X POST http://localhost:8000/api/v1/cart/user123/batch-add \
  -H "Content-Type: application/json" \
  -d '[
    {"product_id": "prod001", "quantity": 1, "price": 99.99},
    {"product_id": "prod002", "quantity": 2, "price": 29.99}
  ]'

# Validate cart
curl -X POST http://localhost:8000/api/v1/cart/user123/validate
```

### Example 4: Merge Guest Cart
```bash
# Merge guest cart to user cart
curl -X POST http://localhost:8000/api/v1/cart/user123/merge?source_user_id=guest456
```

---

## Data Models

### CartItem
```python
{
  "product_id": str,              # Product identifier
  "product_name": str,            # Product name (optional)
  "quantity": int,                # Item quantity (minimum 1)
  "price": float,                 # Unit price
  "discount_percentage": float,   # Discount percentage (0-100)
  "total": float,                 # Total for this item
  "added_at": datetime            # When item was added
}
```

### Cart
```python
{
  "user_id": str,                    # User identifier
  "items": List[CartItem],           # List of cart items
  "subtotal": float,                 # Subtotal before discounts
  "discount_amount": float,          # Total discount amount
  "total_price": float,              # Final total
  "item_count": int,                 # Number of items
  "coupon_code": str,                # Applied coupon code
  "coupon_discount": float,          # Coupon discount amount
  "estimated_delivery": datetime,    # Estimated delivery date
  "last_updated": datetime,          # Last update timestamp
  "abandoned": bool,                 # Whether cart is abandoned
  "abandoned_at": datetime           # When cart was abandoned
}
```

### CartValidationResult
```python
{
  "valid": bool,                 # Overall validation status
  "errors": List[str],           # List of errors
  "warnings": List[str],         # List of warnings
  "suggestions": List[str]       # List of suggestions
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Future versions may include:
- Per-user request limits
- Global request throttling
- IP-based rate limiting

---

## Versioning

Current API Version: `v1`

Future versions will maintain backward compatibility where possible.
