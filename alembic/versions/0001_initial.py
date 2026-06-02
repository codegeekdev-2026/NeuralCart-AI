"""Initial database schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=256), nullable=True),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
    )

    op.create_table(
        'products',
        sa.Column('id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('category', sa.String(length=128), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('inventory', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'sessions',
        sa.Column('session_id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('last_active_at', sa.DateTime(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
    )

    op.create_table(
        'orders',
        sa.Column('order_id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('user_id', sa.String(length=64), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('shipping_address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('order_id', sa.String(length=64), sa.ForeignKey('orders.order_id'), nullable=False),
        sa.Column('product_id', sa.String(length=64), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('product_name', sa.String(length=256), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
    )

    op.create_table(
        'promotions',
        sa.Column('promotion_id', sa.String(length=64), primary_key=True, nullable=False),
        sa.Column('product_id', sa.String(length=64), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('discount_percentage', sa.Float(), nullable=False),
        sa.Column('discount_type', sa.String(length=50), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('upsell_product_ids', sa.JSON(), nullable=True),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('promotions')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('sessions')
    op.drop_table('products')
    op.drop_table('users')
