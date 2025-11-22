"""add epss fields to scan_results

Revision ID: 007
Revises: 006
Create Date: 2025-11-22

This migration adds EPSS (Exploit Prediction Scoring System) fields to scan_results table:
- epss_score: Float (0-1) indicating exploitation probability
- epss_percentile: Float (0-1) showing relative ranking among all CVEs
- epss_updated_at: DateTime tracking when EPSS data was last fetched
- cve_id: String field to store CVE identifier for EPSS lookups

These fields enable risk-based prioritization of vulnerabilities.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add EPSS fields to scan_results table
    """
    # Add CVE identifier column
    # This links WordPress vulnerabilities to CVE database
    op.add_column(
        'scan_results',
        sa.Column('cve_id', sa.String, nullable=True)
    )

    # Add EPSS score column (0-1 scale)
    # Higher score = higher exploitation probability
    op.add_column(
        'scan_results',
        sa.Column('epss_score', sa.Float, nullable=True)
    )

    # Add EPSS percentile column (0-1 scale)
    # Shows relative ranking (e.g., 0.99 = top 1% most exploited)
    op.add_column(
        'scan_results',
        sa.Column('epss_percentile', sa.Float, nullable=True)
    )

    # Add timestamp for EPSS data freshness tracking
    # Used for cache invalidation (EPSS updates daily)
    op.add_column(
        'scan_results',
        sa.Column('epss_updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # ==========================================
    # Performance Indexes
    # ==========================================

    # Index on epss_score for sorting by exploitation risk
    # Query pattern: SELECT * FROM scan_results ORDER BY epss_score DESC
    op.create_index(
        'ix_scan_results_epss_score',
        'scan_results',
        ['epss_score'],
        unique=False
    )

    # Composite index for filtering high-risk vulnerabilities by scan
    # Query pattern: SELECT * FROM scan_results
    #                WHERE scan_id = ? AND epss_score > 0.5
    #                ORDER BY epss_score DESC
    op.create_index(
        'ix_scan_results_scan_id_epss_score',
        'scan_results',
        ['scan_id', 'epss_score'],
        unique=False
    )

    # Index on CVE ID for efficient lookups
    # Query pattern: SELECT * FROM scan_results WHERE cve_id = ?
    op.create_index(
        'ix_scan_results_cve_id',
        'scan_results',
        ['cve_id'],
        unique=False
    )


def downgrade() -> None:
    """
    Remove EPSS fields from scan_results table
    """
    # Drop indexes first (required before dropping columns)
    op.drop_index('ix_scan_results_cve_id', table_name='scan_results')
    op.drop_index('ix_scan_results_scan_id_epss_score', table_name='scan_results')
    op.drop_index('ix_scan_results_epss_score', table_name='scan_results')

    # Drop columns
    op.drop_column('scan_results', 'epss_updated_at')
    op.drop_column('scan_results', 'epss_percentile')
    op.drop_column('scan_results', 'epss_score')
    op.drop_column('scan_results', 'cve_id')
