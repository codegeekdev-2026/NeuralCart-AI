"""
Order Service with DB-backed repository.
"""
import logging
from app.db import SessionLocal
from app.repositories.order_repository import order_repository
from app.models import OrderCreateRequest
from app.models.db_models import Order as OrderModel

logger = logging.getLogger(__name__)


class OrderService:
    """Order management service using repository pattern."""

    def create_order(self, request: OrderCreateRequest) -> OrderModel:
        with SessionLocal() as db:
            return order_repository.create_order(db, request)

    def get_order(self, order_id: str) -> OrderModel | None:
        with SessionLocal() as db:
            return order_repository.get_order(db, order_id)

    def list_orders_by_user(self, user_id: str):
        with SessionLocal() as db:
            return order_repository.list_orders_by_user(db, user_id)

    def update_order_status(self, order_id: str, status: str):
        with SessionLocal() as db:
            return order_repository.update_order_status(db, order_id, status)

    def cancel_order(self, order_id: str):
        with SessionLocal() as db:
            return order_repository.cancel_order(db, order_id)


order_service = OrderService()
