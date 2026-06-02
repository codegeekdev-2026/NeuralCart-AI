"""Product repository (DB-backed)."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.db_models import Product as ProductModel
from app.models import Product as ProductSchema
from datetime import datetime


class ProductRepository:
    def get_by_id(self, db: Session, product_id: str) -> Optional[ProductModel]:
        return db.get(ProductModel, product_id)

    def create_or_update(self, db: Session, product_data: dict) -> ProductModel:
        product = db.get(ProductModel, product_data.get("id"))
        if not product:
            product = ProductModel(id=product_data["id"])

        for key, value in product_data.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        if not product.created_at:
            product.created_at = datetime.utcnow()

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def search(self, db: Session, query: str, filters: dict = None, limit: int = 10):
        stmt = db.query(ProductModel)
        if query:
            q = f"%{query.lower()}%"
            stmt = stmt.filter(
                ProductModel.name.ilike(q) |
                ProductModel.description.ilike(q) |
                ProductModel.category.ilike(q)
            )
        if filters:
            if filters.get("category"):
                stmt = stmt.filter(ProductModel.category == filters["category"])
            if filters.get("min_price") is not None:
                stmt = stmt.filter(ProductModel.price >= filters["min_price"])
            if filters.get("max_price") is not None:
                stmt = stmt.filter(ProductModel.price <= filters["max_price"])

        return stmt.limit(limit).all()


product_repository = ProductRepository()