"""API routes module"""

from .recommendations import router as recommendations_router
from .search import router as search_router
from .payments import router as payments_router
from .health import router as health_router
from .cart import router as cart_router
from .orders import router as orders_router

__all__ = [
    "recommendations_router",
    "search_router",
    "payments_router",
    "health_router",
    "cart_router",
    "orders_router"
]
