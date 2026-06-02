"""Promotion repository (DB-backed)."""
from sqlalchemy.orm import Session
from typing import List
from app.models.db_models import Promotion as PromotionModel
from datetime import datetime


class PromotionRepository:
    def list_active_promotions(self, db: Session) -> List[PromotionModel]:
        return db.query(PromotionModel).filter(PromotionModel.active == True).all()

    def get_for_product(self, db: Session, product_id: str):
        return db.query(PromotionModel).filter(
            PromotionModel.product_id == product_id,
            PromotionModel.active == True
        ).all()

    def add_or_update(self, db: Session, promo_data: dict):
        promo = db.get(PromotionModel, promo_data.get("promotion_id"))
        if not promo:
            promo = PromotionModel(promotion_id=promo_data.get("promotion_id"))

        for k, v in promo_data.items():
            if hasattr(promo, k):
                setattr(promo, k, v)

        promo.updated_at = datetime.utcnow()
        db.add(promo)
        db.commit()
        db.refresh(promo)
        return promo


promotion_repository = PromotionRepository()