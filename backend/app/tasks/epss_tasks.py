"""
Celery tasks for EPSS (Exploit Prediction Scoring System) integration
"""
import asyncio
from datetime import datetime, timedelta
from typing import List
from celery import Task
from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.scan_result import ScanResult
from app.services.epss import get_epss_service

logger = get_task_logger(__name__)


class EPSSTask(Task):
    """Base task for EPSS operations with error handling"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failures"""
        logger.error(f"EPSS task {task_id} failed: {exc}")


@celery_app.task(bind=True, base=EPSSTask)
def enrich_scan_results_with_epss(self, scan_id: int) -> dict:
    """
    Enrich scan results with EPSS scores for a specific scan

    This task:
    1. Finds all scan results with CVE IDs
    2. Fetches EPSS scores from FIRST.org API
    3. Updates database with EPSS data

    Args:
        scan_id: Database ID of the scan

    Returns:
        dict with enrichment summary
    """
    db = SessionLocal()
    try:
        # Get all scan results with CVE IDs for this scan
        results = db.query(ScanResult).filter(
            ScanResult.scan_id == scan_id,
            ScanResult.cve_id.isnot(None)
        ).all()

        if not results:
            logger.info(f"Scan {scan_id}: No CVE IDs found, skipping EPSS enrichment")
            return {"scan_id": scan_id, "enriched": 0, "skipped": 0}

        # Extract unique CVE IDs
        cve_ids = list(set(r.cve_id for r in results if r.cve_id))
        logger.info(f"Scan {scan_id}: Fetching EPSS scores for {len(cve_ids)} unique CVEs")

        # Fetch EPSS scores
        epss_service = get_epss_service()
        epss_data = asyncio.run(epss_service.get_epss_scores(cve_ids))

        # Update scan results with EPSS data
        enriched_count = 0
        skipped_count = 0

        for result in results:
            if not result.cve_id:
                continue

            epss_info = epss_data.get(result.cve_id)
            if epss_info:
                result.epss_score = epss_info.epss_score
                result.epss_percentile = epss_info.percentile
                result.epss_updated_at = datetime.utcnow()
                enriched_count += 1
            else:
                skipped_count += 1
                logger.warning(f"CVE {result.cve_id} not found in EPSS database")

        db.commit()

        logger.info(f"Scan {scan_id}: Enriched {enriched_count} results, skipped {skipped_count}")
        return {
            "scan_id": scan_id,
            "enriched": enriched_count,
            "skipped": skipped_count
        }

    except Exception as e:
        logger.error(f"Error enriching scan {scan_id} with EPSS data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, base=EPSSTask)
def refresh_stale_epss_scores(self, max_age_hours: int = 24) -> dict:
    """
    Refresh EPSS scores that are older than max_age_hours

    EPSS scores are updated daily by FIRST.org, so we refresh our cached
    scores once per day to stay current.

    Args:
        max_age_hours: Maximum age of EPSS data in hours (default: 24)

    Returns:
        dict with refresh summary
    """
    db = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        # Find all scan results with stale EPSS data
        stale_results = db.query(ScanResult).filter(
            ScanResult.cve_id.isnot(None),
            ScanResult.epss_updated_at.isnot(None),
            ScanResult.epss_updated_at < cutoff_time
        ).all()

        if not stale_results:
            logger.info("No stale EPSS scores found")
            return {"refreshed": 0, "skipped": 0}

        # Extract unique CVE IDs
        cve_ids = list(set(r.cve_id for r in stale_results if r.cve_id))
        logger.info(f"Refreshing EPSS scores for {len(cve_ids)} unique CVEs")

        # Fetch fresh EPSS scores
        epss_service = get_epss_service()
        epss_data = asyncio.run(epss_service.get_epss_scores(cve_ids))

        # Update scan results
        refreshed_count = 0
        skipped_count = 0

        for result in stale_results:
            if not result.cve_id:
                continue

            epss_info = epss_data.get(result.cve_id)
            if epss_info:
                result.epss_score = epss_info.epss_score
                result.epss_percentile = epss_info.percentile
                result.epss_updated_at = datetime.utcnow()
                refreshed_count += 1
            else:
                skipped_count += 1

        db.commit()

        logger.info(f"Refreshed {refreshed_count} EPSS scores, skipped {skipped_count}")
        return {
            "refreshed": refreshed_count,
            "skipped": skipped_count
        }

    except Exception as e:
        logger.error(f"Error refreshing EPSS scores: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, base=EPSSTask)
def refresh_all_epss_scores_daily():
    """
    Daily scheduled task to refresh all EPSS scores

    This task should be scheduled to run once per day (e.g., at 2:00 AM UTC)
    to keep EPSS data fresh.

    Configure in celery_app.py with:
        app.conf.beat_schedule = {
            'refresh-epss-daily': {
                'task': 'app.tasks.epss_tasks.refresh_all_epss_scores_daily',
                'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC
            },
        }
    """
    logger.info("Starting daily EPSS refresh")
    result = refresh_stale_epss_scores.delay(max_age_hours=24)
    return {"task_id": result.id}
