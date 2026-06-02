"""SQLAlchemy models for persistence."""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    category = Column(String(128), nullable=False)
    embedding = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True, default=list)
    inventory = Column(Integer, default=0)
    image_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "users"

    user_id = Column(String(64), primary_key=True, index=True)
    email = Column(String(256), nullable=True)
    name = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    preferences = Column(JSON, nullable=True, default=dict)


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    device_type = Column(String(50), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    user = relationship("UserProfile")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    shipping_address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(String(64), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(256), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")


class Promotion(Base):
    __tablename__ = "promotions"

    promotion_id = Column(String(64), primary_key=True, index=True)
    product_id = Column(String(64), ForeignKey("products.id"), nullable=False)
    discount_percentage = Column(Float, nullable=False)
    discount_type = Column(String(50), nullable=False)
    discount_value = Column(Float, nullable=False)
    upsell_product_ids = Column(JSON, default=list)
    conditions = Column(JSON, default=dict)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
