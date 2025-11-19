"""Add orders table for landing page purchases

Revision ID: 001_orders
Revises:
Create Date: 2025-11-19 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_orders'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_payment_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_session_id', sa.String(length=255), nullable=False),
        sa.Column('payment_status', sa.String(length=50), nullable=False),
        sa.Column('amount_paid', sa.Integer(), nullable=False),
        sa.Column('agency_name', sa.String(length=255), nullable=False),
        sa.Column('contact_email', sa.String(length=255), nullable=False),
        sa.Column('site_name', sa.String(length=255), nullable=False),
        sa.Column('site_url', sa.String(length=500), nullable=True),
        sa.Column('wp_current_version', sa.String(length=50), nullable=False),
        sa.Column('wp_target_version', sa.String(length=50), nullable=False),
        sa.Column('plugin_list', sa.Text(), nullable=False),
        sa.Column('theme_name', sa.String(length=255), nullable=True),
        sa.Column('theme_version', sa.String(length=50), nullable=True),
        sa.Column('custom_notes', sa.Text(), nullable=True),
        sa.Column('analysis_status', sa.String(length=50), nullable=False),
        sa.Column('report_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_payment_id'),
        sa.UniqueConstraint('stripe_session_id')
    )

    # Create indexes
    op.create_index('idx_orders_email', 'orders', ['contact_email'])
    op.create_index('idx_orders_payment_status', 'orders', ['payment_status'])
    op.create_index('idx_orders_analysis_status', 'orders', ['analysis_status'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_orders_analysis_status', table_name='orders')
    op.drop_index('idx_orders_payment_status', table_name='orders')
    op.drop_index('idx_orders_email', table_name='orders')

    # Drop table
    op.drop_table('orders')
