"""Add user onboarding fields

Revision ID: 002_onboarding
Revises: 001_orders
Create Date: 2025-11-19 23:12:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_onboarding'
down_revision = '001_orders'
branch_labels = None
depends_on = None


def upgrade():
    # Add onboarding fields to users table
    op.add_column('users', sa.Column('name', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('users', sa.Column('company', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))
    
    # Remove server defaults after adding columns (they're only for existing rows)
    op.alter_column('users', 'name', server_default=None)
    op.alter_column('users', 'onboarding_completed', server_default=None)


def downgrade():
    # Remove onboarding fields
    op.drop_column('users', 'onboarding_completed')
    op.drop_column('users', 'company')
    op.drop_column('users', 'name')
