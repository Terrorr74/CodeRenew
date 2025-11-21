"""add performance indexes

Revision ID: 005
Revises: 004
Create Date: 2025-01-20

This migration adds database indexes to improve query performance:
1. Foreign key indexes for faster JOIN operations
2. Composite indexes for common query patterns
3. Status and timestamp indexes for filtering and sorting

These indexes are critical for production performance as the dataset grows.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add performance indexes to database tables
    """
    # ==========================================
    # Sites table indexes
    # ==========================================
    # Foreign key index - critical for JOIN performance
    # Query pattern: SELECT * FROM sites WHERE user_id = ?
    op.create_index(
        'ix_sites_user_id',
        'sites',
        ['user_id'],
        unique=False
    )

    # Composite index for user's sites sorted by creation date
    # Query pattern: SELECT * FROM sites WHERE user_id = ? ORDER BY created_at DESC
    op.create_index(
        'ix_sites_user_id_created_at',
        'sites',
        ['user_id', 'created_at'],
        unique=False
    )

    # ==========================================
    # Scans table indexes
    # ==========================================
    # Foreign key indexes - critical for JOIN performance
    # Query pattern: SELECT * FROM scans WHERE site_id = ?
    op.create_index(
        'ix_scans_site_id',
        'scans',
        ['site_id'],
        unique=False
    )

    # Query pattern: SELECT * FROM scans WHERE user_id = ?
    op.create_index(
        'ix_scans_user_id',
        'scans',
        ['user_id'],
        unique=False
    )

    # Status index for filtering by scan status
    # Query pattern: SELECT * FROM scans WHERE status = 'pending'
    op.create_index(
        'ix_scans_status',
        'scans',
        ['status'],
        unique=False
    )

    # Composite index for user's scans sorted by creation date
    # Query pattern: SELECT * FROM scans WHERE user_id = ? ORDER BY created_at DESC
    op.create_index(
        'ix_scans_user_id_created_at',
        'scans',
        ['user_id', 'created_at'],
        unique=False
    )

    # Composite index for filtering and sorting by status and date
    # Query pattern: SELECT * FROM scans WHERE status = ? ORDER BY created_at DESC
    op.create_index(
        'ix_scans_status_created_at',
        'scans',
        ['status', 'created_at'],
        unique=False
    )

    # ==========================================
    # Scan Results table indexes
    # ==========================================
    # Foreign key index - critical for JOIN performance
    # Query pattern: SELECT * FROM scan_results WHERE scan_id = ?
    op.create_index(
        'ix_scan_results_scan_id',
        'scan_results',
        ['scan_id'],
        unique=False
    )

    # Severity index for filtering by severity
    # Query pattern: SELECT * FROM scan_results WHERE severity = 'critical'
    op.create_index(
        'ix_scan_results_severity',
        'scan_results',
        ['severity'],
        unique=False
    )

    # Composite index for scan results filtered by severity
    # Query pattern: SELECT * FROM scan_results WHERE scan_id = ? AND severity = ?
    op.create_index(
        'ix_scan_results_scan_id_severity',
        'scan_results',
        ['scan_id', 'severity'],
        unique=False
    )

    # Issue type index for analytics queries
    # Query pattern: SELECT COUNT(*) FROM scan_results GROUP BY issue_type
    op.create_index(
        'ix_scan_results_issue_type',
        'scan_results',
        ['issue_type'],
        unique=False
    )

    # ==========================================
    # Orders table indexes
    # ==========================================
    # Stripe payment ID and session ID are already unique indexed
    # Add composite index for filtering orders by status and date
    # Query pattern: SELECT * FROM orders WHERE analysis_status = ? ORDER BY created_at DESC
    op.create_index(
        'ix_orders_analysis_status_created_at',
        'orders',
        ['analysis_status', 'created_at'],
        unique=False
    )

    # ==========================================
    # Users table indexes
    # ==========================================
    # Email and reset_token are already indexed in the model
    # Add index for account lockout queries
    # Query pattern: SELECT * FROM users WHERE locked_until > NOW()
    op.create_index(
        'ix_users_locked_until',
        'users',
        ['locked_until'],
        unique=False,
        postgresql_where=sa.text('locked_until IS NOT NULL')  # Partial index
    )

    # Index for verification status queries
    # Query pattern: SELECT * FROM users WHERE is_verified = false
    op.create_index(
        'ix_users_is_verified',
        'users',
        ['is_verified'],
        unique=False
    )


def downgrade() -> None:
    """
    Remove performance indexes
    """
    # Users table indexes
    op.drop_index('ix_users_is_verified', table_name='users')
    op.drop_index('ix_users_locked_until', table_name='users')

    # Orders table indexes
    op.drop_index('ix_orders_analysis_status_created_at', table_name='orders')

    # Scan Results table indexes
    op.drop_index('ix_scan_results_issue_type', table_name='scan_results')
    op.drop_index('ix_scan_results_scan_id_severity', table_name='scan_results')
    op.drop_index('ix_scan_results_severity', table_name='scan_results')
    op.drop_index('ix_scan_results_scan_id', table_name='scan_results')

    # Scans table indexes
    op.drop_index('ix_scans_status_created_at', table_name='scans')
    op.drop_index('ix_scans_user_id_created_at', table_name='scans')
    op.drop_index('ix_scans_status', table_name='scans')
    op.drop_index('ix_scans_user_id', table_name='scans')
    op.drop_index('ix_scans_site_id', table_name='scans')

    # Sites table indexes
    op.drop_index('ix_sites_user_id_created_at', table_name='sites')
    op.drop_index('ix_sites_user_id', table_name='sites')
