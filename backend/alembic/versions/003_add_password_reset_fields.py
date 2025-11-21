"""Add password reset fields

Revision ID: 003_password_reset
Revises: 002_onboarding
Create Date: 2025-11-19 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_password_reset'
down_revision = '002_onboarding'
branch_labels = None
depends_on = None


def upgrade():
    # Add password reset fields to users table
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))
    
    # Create index for faster token lookups
    op.create_index('idx_users_reset_token', 'users', ['reset_token'])


def downgrade():
    # Remove index
    op.drop_index('idx_users_reset_token', table_name='users')
    
    # Remove password reset fields
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
