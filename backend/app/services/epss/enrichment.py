"""
EPSS Enrichment Helper Functions

Utilities for enriching scan results with EPSS scores during the scan workflow.
"""
from typing import List, Dict
from datetime import datetime, timedelta
import logging

from app.models.scan_result import ScanResult
from app.services.epss import get_epss_service, EPSSData
from app.tasks.epss_tasks import enrich_scan_results_with_epss

logger = logging.getLogger(__name__)


async def enrich_results_with_epss(results: List[ScanResult]) -> Dict[str, EPSSData]:
    """
    Enrich scan results with EPSS scores (async function for use in endpoints)

    This function:
    1. Extracts CVE IDs from scan results
    2. Fetches EPSS scores from API
    3. Updates result objects (does NOT commit to database)

    Args:
        results: List of ScanResult objects

    Returns:
        Dictionary mapping CVE ID -> EPSSData

    Usage in scan workflow:
        results = [...]  # Create scan result objects
        epss_data = await enrich_results_with_epss(results)
        # Now results have epss_score, epss_percentile populated
        db.add_all(results)
        db.commit()
    """
    # Extract unique CVE IDs
    cve_ids = [r.cve_id for r in results if r.cve_id]
    if not cve_ids:
        logger.info("No CVE IDs found, skipping EPSS enrichment")
        return {}

    unique_cves = list(set(cve_ids))
    logger.info(f"Fetching EPSS scores for {len(unique_cves)} unique CVEs")

    # Fetch EPSS scores
    epss_service = get_epss_service()
    epss_data = await epss_service.get_epss_scores(unique_cves)

    # Update result objects
    for result in results:
        if not result.cve_id:
            continue

        epss_info = epss_data.get(result.cve_id)
        if epss_info:
            result.epss_score = epss_info.epss_score
            result.epss_percentile = epss_info.percentile
            result.epss_updated_at = datetime.utcnow()
        else:
            logger.warning(f"CVE {result.cve_id} not found in EPSS database")

    return epss_data


def trigger_epss_enrichment_task(scan_id: int) -> str:
    """
    Trigger background task to enrich scan results with EPSS scores

    Use this for async enrichment after scan completion.

    Args:
        scan_id: Database ID of the scan

    Returns:
        Celery task ID

    Usage after scan completes:
        task_id = trigger_epss_enrichment_task(scan_id)
        # Task runs in background, enriching results
    """
    task = enrich_scan_results_with_epss.delay(scan_id)
    logger.info(f"Triggered EPSS enrichment task {task.id} for scan {scan_id}")
    return task.id


def extract_cve_from_description(description: str) -> str | None:
    """
    Extract CVE identifier from vulnerability description

    Looks for patterns like CVE-YYYY-NNNNN in the description text.

    Args:
        description: Vulnerability description text

    Returns:
        CVE identifier if found, None otherwise

    Example:
        >>> extract_cve_from_description("WordPress Plugin XSS (CVE-2024-1234)")
        "CVE-2024-1234"
    """
    import re

    # Pattern: CVE-YYYY-NNNNN (year must be 1999-2099, ID is 4-7 digits)
    pattern = r'CVE-(\d{4})-(\d{4,7})'
    match = re.search(pattern, description, re.IGNORECASE)

    if match:
        cve_id = f"CVE-{match.group(1)}-{match.group(2)}"
        return cve_id.upper()

    return None


def should_refresh_epss(result: ScanResult, max_age_hours: int = 24) -> bool:
    """
    Check if a scan result's EPSS data should be refreshed

    Args:
        result: ScanResult object
        max_age_hours: Maximum age of EPSS data in hours

    Returns:
        True if EPSS data should be refreshed
    """
    if not result.cve_id:
        return False

    if not result.epss_updated_at:
        return True  # Never fetched

    age = datetime.utcnow() - result.epss_updated_at
    max_age = timedelta(hours=max_age_hours)

    return age >= max_age


# Example integration into WordPress scanner:
"""
# In backend/app/services/wordpress/scanner.py:

from app.services.epss.enrichment import enrich_results_with_epss, extract_cve_from_description

async def analyze_plugin(self, plugin_code: str) -> List[ScanResult]:
    results = []

    # ... existing vulnerability detection logic ...

    for vulnerability in detected_vulnerabilities:
        result = ScanResult(
            issue_type=vulnerability.type,
            severity=vulnerability.severity,
            description=vulnerability.description,
            # Extract CVE from description if present
            cve_id=extract_cve_from_description(vulnerability.description)
        )
        results.append(result)

    # Enrich with EPSS scores
    await enrich_results_with_epss(results)

    return results
"""
