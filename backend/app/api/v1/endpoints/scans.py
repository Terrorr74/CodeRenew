"""
Scans endpoints
WordPress compatibility scanning operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os
from pathlib import Path
import zipfile

from app.core.config import settings
from app.db.session import get_db
from app.api.dependencies import get_current_user, check_scan_limits
from app.schemas.scan import (
    ScanCreate, ScanResponse, AsyncScanJobResponse, ScanJobStatus
)
from app.models.user import User
from app.tasks.scan_tasks import run_wordpress_scan
from celery.result import AsyncResult
from app.models.site import Site
from app.models.scan import Scan, ScanStatus
from app.models.scan_result import ScanResult
from app.services.wordpress.scanner import WordPressScanner
from app.services.reporting.pdf_generator import PDFReportGenerator
from app.services.email import send_scan_complete_email

router = APIRouter()


async def process_scan(scan_id: int, db: Session):
    """
    Background task to process a scan
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return

    try:
        # Update status to processing
        scan.status = ScanStatus.PROCESSING
        db.commit()

        # Define paths
        upload_dir = Path(settings.UPLOAD_DIR)
        scan_dir = upload_dir / str(scan.user_id) / str(scan.id)
        extract_dir = scan_dir / "extracted"
        
        # Find the uploaded zip file
        zip_files = list(scan_dir.glob("*.zip"))
        if not zip_files:
            raise Exception("No zip file found")
            
        zip_path = zip_files[0]
        
        # Extract files
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # Find all PHP files
        php_files = list(extract_dir.rglob("*.php"))
        
        # Initialize scanner
        scanner = WordPressScanner(
            version_from=scan.wordpress_version_from,
            version_to=scan.wordpress_version_to
        )
        
        # Scan files
        issues = await scanner.scan_files(php_files)
        
        # Save results
        for issue in issues:
            scan_result = ScanResult(
                scan_id=scan.id,
                issue_type=issue.get('issue_type', 'compatibility'),
                severity=issue.get('severity', 'info'),
                file_path=issue.get('file', ''),
                line_number=issue.get('line'),
                description=issue.get('description', ''),
                recommendation=issue.get('recommendation', ''),
                code_snippet=issue.get('code_snippet'),
                evidence_url=issue.get('evidence')
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
            print(f"Failed to send email: {e}")
        
        # Cleanup
        # shutil.rmtree(scan_dir)
        
    except Exception as e:
        print(f"Scan processing error: {e}")
        scan.status = ScanStatus.FAILED
        db.commit()


@router.post("/upload", response_model=ScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    site_id: int = Form(...),
    wordpress_version_from: str = Form(...),
    wordpress_version_to: str = Form(...),
    current_user: User = Depends(check_scan_limits),
    db: Session = Depends(get_db)
):
    """
    Upload a file and start a scan
    """
    # Verify site belongs to user
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Create scan record
    db_scan = Scan(
        site_id=site_id,
        user_id=current_user.id,
        wordpress_version_from=wordpress_version_from,
        wordpress_version_to=wordpress_version_to,
        status=ScanStatus.PENDING
    )

    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    # Save uploaded file
    upload_dir = Path(settings.UPLOAD_DIR)
    scan_dir = upload_dir / str(current_user.id) / str(db_scan.id)
    scan_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = scan_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Start background task
    background_tasks.add_task(process_scan, db_scan.id, db)

    return db_scan


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new WordPress compatibility scan (Metadata only)
    """


@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all scans for the current user

    Args:
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of scan objects
    """
    scans = db.query(Scan).filter(
        Scan.user_id == current_user.id
    ).order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()

    return scans


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific scan with results

    Args:
        scan_id: Scan ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Scan object with results
    """
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    return scan
 

@router.post("/estimate", status_code=status.HTTP_200_OK)
async def estimate_scan_tokens(
    file: UploadFile = File(...),
    wordpress_version_from: str = Form(...),
    wordpress_version_to: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    """
    Estimate tokens and cost for a scan without actually running it
    
    This endpoint helps users understand:
    - How many tokens the scan will use
    - Estimated API cost
    - Number of batches needed
    - Context overflow risk
    
    Args:
        file: ZIP file to analyze
        wordpress_version_from: Starting WordPress version
        wordpress_version_to: Target WordPress version
        current_user: Current authenticated user
        
    Returns:
        Token estimation details
    """
    import tempfile
    
    try:
        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded file
            zip_path = temp_path / file.filename
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract files
            extract_dir = temp_path / "extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find all PHP files
            php_files = list(extract_dir.rglob("*.php"))
            
            # Initialize scanner
            scanner = WordPressScanner(
                version_from=wordpress_version_from,
                version_to=wordpress_version_to
            )
            
            # Get token estimate
            estimate = scanner.estimate_total_tokens(php_files)
            
            return {
                "success": True,
                "estimate": estimate,
                "message": f"Found {estimate['total_files']} PHP files requiring ~{estimate['total_tokens']} tokens across {estimate['estimated_batches']} batches"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error estimating tokens: {str(e)}"
        )


# ============== Async Celery-based scan endpoints ==============

@router.post("/async/start", response_model=AsyncScanJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_async_scan(
    file: UploadFile = File(...),
    site_id: int = Form(...),
    wordpress_version_from: str = Form(...),
    wordpress_version_to: str = Form(...),
    current_user: User = Depends(check_scan_limits),
    db: Session = Depends(get_db)
):
    """
    Start an async WordPress scan using Celery.
    Returns job ID immediately for status polling.
    """
    # Verify site belongs to user
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Create scan record
    db_scan = Scan(
        site_id=site_id,
        user_id=current_user.id,
        wordpress_version_from=wordpress_version_from,
        wordpress_version_to=wordpress_version_to,
        status=ScanStatus.PENDING
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    # Save uploaded file
    upload_dir = Path(settings.UPLOAD_DIR)
    scan_dir = upload_dir / str(current_user.id) / str(db_scan.id)
    scan_dir.mkdir(parents=True, exist_ok=True)

    file_path = scan_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Queue Celery task
    task = run_wordpress_scan.delay(db_scan.id)

    return AsyncScanJobResponse(
        job_id=task.id,
        scan_id=db_scan.id,
        status="queued",
        message="Scan job queued successfully"
    )


@router.get("/async/status/{job_id}", response_model=ScanJobStatus)
async def get_async_scan_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check the status of an async scan job.
    """
    task_result = AsyncResult(job_id)

    # Map Celery states to friendly status
    status_map = {
        "PENDING": "queued",
        "STARTED": "running",
        "SUCCESS": "completed",
        "FAILURE": "failed",
        "RETRY": "retrying",
        "REVOKED": "cancelled",
    }

    status_str = status_map.get(task_result.state, task_result.state.lower())

    result = None
    error = None
    scan_id = None

    if task_result.successful():
        result = task_result.result
        scan_id = result.get("scan_id") if result else None
    elif task_result.failed():
        error = str(task_result.result)

    # Try to get scan_id from result or find matching scan
    if not scan_id and result:
        scan_id = result.get("scan_id")

    return ScanJobStatus(
        job_id=job_id,
        scan_id=scan_id or 0,
        status=status_str,
        result=result if task_result.successful() else None,
        error=error
    )


@router.get("/async/results/{scan_id}", response_model=ScanResponse)
async def get_async_scan_results(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the results of a completed async scan.
    """
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    return scan
