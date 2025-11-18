"""
Scans endpoints
WordPress compatibility scanning operations
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.schemas.scan import ScanCreate, ScanResponse
from app.models.user import User
from app.models.site import Site
from app.models.scan import Scan, ScanStatus
from app.services.wordpress.scanner import WordPressScanner

router = APIRouter()


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new WordPress compatibility scan

    Args:
        scan_data: Scan creation data
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created scan object
    """
    # Verify site belongs to user
    site = db.query(Site).filter(
        Site.id == scan_data.site_id,
        Site.user_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Create scan record
    db_scan = Scan(
        site_id=scan_data.site_id,
        user_id=current_user.id,
        wordpress_version_from=scan_data.wordpress_version_from,
        wordpress_version_to=scan_data.wordpress_version_to,
        status=ScanStatus.PENDING
    )

    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    # TODO: Add background task to process scan
    # background_tasks.add_task(process_scan, db_scan.id)

    return db_scan


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
