"""Order repository with embedded database persistence."""
from sqlalchemy.orm import Session
from app.models import OrderCreateRequest, Order, OrderItem as OrderItemSchema
from app.models.db_models import Order as OrderModel, OrderItem as OrderItemModel, UserProfile
from datetime import datetime
import uuid


class OrderRepository:
    def create_order(self, db: Session, request: OrderCreateRequest) -> OrderModel:
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        order = OrderModel(
            order_id=order_id,
            user_id=request.user_id,
            total_amount=request.total_amount,
            status="pending",
            shipping_address=request.shipping_address,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        for item in request.items:
            order_item = OrderItemModel(
                order_id=order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            order.items.append(order_item)

        # ensure user exists (idempotent)
        if not db.get(UserProfile, request.user_id):
            db.add(UserProfile(user_id=request.user_id, created_at=datetime.utcnow(), updated_at=datetime.utcnow()))

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def get_order(self, db: Session, order_id: str) -> OrderModel | None:
        return db.get(OrderModel, order_id)

    def list_orders_by_user(self, db: Session, user_id: str):
        return db.query(OrderModel).filter(OrderModel.user_id == user_id).all()

    def update_order_status(self, db: Session, order_id: str, status: str):
        order = db.get(OrderModel, order_id)
        if not order:
            return None
        order.status = status
        order.updated_at = datetime.utcnow()
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def cancel_order(self, db: Session, order_id: str):
        return self.update_order_status(db, order_id, "canceled")


order_repository = OrderRepository()