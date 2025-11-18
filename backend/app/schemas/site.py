"""
Site Pydantic schemas
Request and response models for site operations
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class SiteBase(BaseModel):
    """Base site schema with common fields"""
    name: str = Field(..., min_length=1, max_length=200)
    url: Optional[str] = None
    description: Optional[str] = None


class SiteCreate(SiteBase):
    """Schema for creating a new site"""
    pass


class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = None
    description: Optional[str] = None


class SiteResponse(SiteBase):
    """Schema for site response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
