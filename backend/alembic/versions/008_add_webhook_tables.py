"""Add webhook tables

Revision ID: 008_add_webhook_tables
Revises: 007_add_epss_fields
Create Date: 2025-11-22 14:24:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_add_webhook_tables'
down_revision = '007_add_epss_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create webhook_configs and webhook_deliveries tables"""
    
    # Create webhook_configs table
    op.create_table(
        'webhook_configs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # 'slack', 'teams', 'email', 'http'
        sa.Column('url', sa.Text(), nullable=True),  # Encrypted, nullable for email type
        sa.Column('enabled', sa.Boolean(), default=True, nullable=False),
        sa.Column('events', sa.JSON(), nullable=False),  # ['scan_completed', 'vulnerability_found']
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # Create indexes for webhook_configs
    op.create_index('ix_webhook_configs_user_id', 'webhook_configs', ['user_id'])
    op.create_index('ix_webhook_configs_type', 'webhook_configs', ['type'])
    op.create_index('ix_webhook_configs_enabled', 'webhook_configs', ['enabled'])
    
    # Create webhook_deliveries table
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('webhook_config_id', sa.String(36), sa.ForeignKey('webhook_configs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),  # 'pending', 'delivered', 'failed'
        sa.Column('attempts', sa.Integer(), default=0, nullable=False),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    
    # Create indexes for webhook_deliveries
    op.create_index('ix_webhook_deliveries_webhook_config_id', 'webhook_deliveries', ['webhook_config_id'])
    op.create_index('ix_webhook_deliveries_status', 'webhook_deliveries', ['status'])
    op.create_index('ix_webhook_deliveries_event_type', 'webhook_deliveries', ['event_type'])
    op.create_index('ix_webhook_deliveries_created_at', 'webhook_deliveries', ['created_at'])


def downgrade() -> None:
    """Drop webhook tables"""
    op.drop_index('ix_webhook_deliveries_created_at', 'webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_event_type', 'webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_status', 'webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_webhook_config_id', 'webhook_deliveries')
    op.drop_table('webhook_deliveries')
    
    op.drop_index('ix_webhook_configs_enabled', 'webhook_configs')
    op.drop_index('ix_webhook_configs_type', 'webhook_configs')
    op.drop_index('ix_webhook_configs_user_id', 'webhook_configs')
    op.drop_table('webhook_configs')
