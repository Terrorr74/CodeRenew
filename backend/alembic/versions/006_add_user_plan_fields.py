"""add user plan fields

Revision ID: 006
Revises: 005
Create Date: 2025-11-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    # Note: We use checkfirst=True to avoid errors if types already exist (e.g. from previous failed runs)
    userplan = postgresql.ENUM('free', 'pro', name='userplan')
    userplan.create(op.get_bind(), checkfirst=True)
    
    subscriptionstatus = postgresql.ENUM('active', 'canceled', 'past_due', name='subscriptionstatus')
    subscriptionstatus.create(op.get_bind(), checkfirst=True)

    op.add_column('users', sa.Column('plan', sa.Enum('free', 'pro', name='userplan'), server_default='free', nullable=False))
    op.add_column('users', sa.Column('subscription_status', sa.Enum('active', 'canceled', 'past_due', name='subscriptionstatus'), nullable=True))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'plan')
    
    # Drop enum types
    subscriptionstatus = postgresql.ENUM('active', 'canceled', 'past_due', name='subscriptionstatus')
    subscriptionstatus.drop(op.get_bind(), checkfirst=True)
    
    userplan = postgresql.ENUM('free', 'pro', name='userplan')
    userplan.drop(op.get_bind(), checkfirst=True)
