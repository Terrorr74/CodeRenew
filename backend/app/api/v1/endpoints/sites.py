"""
Sites endpoints
CRUD operations for WordPress sites
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.models.user import User
from app.models.site import Site

router = APIRouter()


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new site

    Args:
        site_data: Site creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created site object
    """
    db_site = Site(
        user_id=current_user.id,
        name=site_data.name,
        url=site_data.url,
        description=site_data.description
    )

    db.add(db_site)
    db.commit()
    db.refresh(db_site)

    return db_site


@router.get("/", response_model=List[SiteResponse])
async def list_sites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all sites for the current user

    Args:
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of site objects
    """
    sites = db.query(Site).filter(
        Site.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return sites


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific site by ID

    Args:
        site_id: Site ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Site object
    """
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    return site


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a site

    Args:
        site_id: Site ID
        site_data: Site update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated site object
    """
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Update fields
    update_data = site_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)

    db.commit()
    db.refresh(site)

    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a site

    Args:
        site_id: Site ID
        current_user: Current authenticated user
        db: Database session
    """
    site = db.query(Site).filter(
        Site.id == site_id,
        Site.user_id == current_user.id
    ).first()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    db.delete(site)
    db.commit()

    return None
