"""
EPSS (Exploit Prediction Scoring System) Service
Integrates with FIRST.org EPSS API to prioritize vulnerabilities
"""

from .epss_service import EPSSService, EPSSData, get_epss_service
from .enrichment import (
    enrich_results_with_epss,
    trigger_epss_enrichment_task,
    extract_cve_from_description,
    should_refresh_epss
)

__all__ = [
    "EPSSService",
    "EPSSData",
    "get_epss_service",
    "enrich_results_with_epss",
    "trigger_epss_enrichment_task",
    "extract_cve_from_description",
    "should_refresh_epss",
]
