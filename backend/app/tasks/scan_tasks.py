"""
Celery tasks for WordPress scanning
"""
import asyncio
from datetime import datetime
from pathlib import Path
import zipfile
from celery import Task
from celery.exceptions import MaxRetriesExceededError

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.scan_result import ScanResult
from app.models.user import User
from app.services.wordpress.scanner import WordPressScanner
from app.services.email import send_scan_complete_email


class ScanTask(Task):
    """Base task with error handling"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        scan_id = args[0] if args else kwargs.get("scan_id")
        if scan_id:
            db = SessionLocal()
            try:
                scan = db.query(Scan).filter(Scan.id == scan_id).first()
                if scan and scan.status != ScanStatus.FAILED:
                    scan.status = ScanStatus.FAILED
                    db.commit()
            finally:
                db.close()


@celery_app.task(bind=True, base=ScanTask, max_retries=3, default_retry_delay=60)
def run_wordpress_scan(self, scan_id: int) -> dict:
    """
    Run WordPress compatibility scan as a background task

    Args:
        scan_id: Database ID of the scan to process

    Returns:
        dict with scan results summary
    """
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return {"error": "Scan not found"}

        # Update status to processing
        scan.status = ScanStatus.PROCESSING
        db.commit()

        # Set up paths
        upload_dir = Path(settings.UPLOAD_DIR)
        scan_dir = upload_dir / str(scan.user_id) / str(scan.id)
        extract_dir = scan_dir / "extracted"

        # Find and extract zip
        zip_files = list(scan_dir.glob("*.zip"))
        if not zip_files:
            raise Exception("No zip file found for scan")

        zip_path = zip_files[0]
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # Find PHP files
        php_files = list(extract_dir.rglob("*.php"))

        # Initialize scanner
        scanner = WordPressScanner(
            version_from=scan.wordpress_version_from,
            version_to=scan.wordpress_version_to
        )

        # Run async scan in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            issues = loop.run_until_complete(scanner.scan_files(php_files))
        finally:
            loop.close()

        # Save results
        for issue in issues:
            scan_result = ScanResult(
                scan_id=scan.id,
                issue_type=issue.get("issue_type", "compatibility"),
                severity=issue.get("severity", "info"),
                file_path=issue.get("file", ""),
                line_number=issue.get("line"),
                description=issue.get("description", ""),
                recommendation=issue.get("recommendation", ""),
                code_snippet=issue.get("code_snippet"),
                evidence_url=issue.get("evidence")
            )
            db.add(scan_result)

        # Update scan status
        scan.status = ScanStatus.COMPLETED
        scan.risk_level = scanner.calculate_risk_level(issues)
        scan.completed_at = datetime.utcnow()
        db.commit()

        # Send email notification
        try:
            user = db.query(User).filter(User.id == scan.user_id).first()
            if user:
                send_scan_complete_email(
                    email_to=user.email,
                    scan_id=scan.id,
                    risk_level=scan.risk_level.value if scan.risk_level else "unknown",
                    issue_count=len(issues)
                )
        except Exception as e:
            print(f"Email notification failed: {e}")

        return {
            "scan_id": scan_id,
            "status": "completed",
            "issues_found": len(issues),
            "risk_level": scan.risk_level.value if scan.risk_level else None,
            "stats": scanner.get_stats()
        }

    except Exception as exc:
        db.rollback()
        # Update status to failed if max retries exceeded
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = ScanStatus.FAILED
                db.commit()
            raise
    finally:
        db.close()
