"""Product API Routes"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional
from app.models import Product, ProductUpdate, ProductSearchResponse, ProductSearchRequest
from app.db import SessionLocal
from app.repositories.product_repository import product_repository

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post("", response_model=Product)
async def create_product(product: Product):
    with SessionLocal() as db:
        created = product_repository.create_or_update(db, product.dict())
        return Product.from_orm(created)


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str = Path(..., description="Product ID")):
    with SessionLocal() as db:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return Product.from_orm(product)


@router.get("", response_model=ProductSearchResponse)
async def list_products(q: Optional[str] = None, category: Optional[str] = None, limit: int = 20):
    filters = {}
    if category:
        filters["category"] = category
    request = ProductSearchRequest(query=q or "", filters=filters if filters else None, limit=limit)
    with SessionLocal() as db:
        products = product_repository.search(db, request.query, request.filters or {}, request.limit)
        return ProductSearchResponse(
            products=[Product.from_orm(p) for p in products],
            total=len(products),
            limit=limit,
            offset=0,
        )


@router.patch("/{product_id}", response_model=Product)
async def update_product(product_id: str, update: ProductUpdate):
    with SessionLocal() as db:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        for field, value in update.dict(exclude_none=True).items():
            setattr(product, field, value)

        product.updated_at = __import__("datetime").datetime.utcnow()
        db.add(product)
        db.commit()
        db.refresh(product)
        return Product.from_orm(product)


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    with SessionLocal() as db:
        product = product_repository.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        db.delete(product)
        db.commit()
        return {"success": True, "product_id": product_id}
