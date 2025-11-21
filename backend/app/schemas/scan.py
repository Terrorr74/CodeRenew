"""
Scan Pydantic schemas
Request and response models for scan operations
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.scan import RiskLevel, ScanStatus
from app.models.scan_result import Severity, IssueType


class ScanCreate(BaseModel):
    """Schema for creating a new scan"""
    site_id: int
    wordpress_version_from: str = Field(..., min_length=1, max_length=20)
    wordpress_version_to: str = Field(..., min_length=1, max_length=20)


class ScanResultResponse(BaseModel):
    """Schema for scan result response"""
    id: int
    scan_id: int
    issue_type: IssueType
    severity: Severity
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    description: str
    recommendation: Optional[str] = None
    code_snippet: Optional[str] = None

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    """Schema for scan response"""
    id: int
    site_id: int
    user_id: int
    wordpress_version_from: str
    wordpress_version_to: str
    status: ScanStatus
    risk_level: Optional[RiskLevel] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[List[ScanResultResponse]] = []

    class Config:
        from_attributes = True


# Async job schemas
class AsyncScanCreate(BaseModel):
    """Schema for starting an async scan job"""
    site_id: int
    wordpress_version_from: str = Field(..., min_length=1, max_length=20)
    wordpress_version_to: str = Field(..., min_length=1, max_length=20)


class AsyncScanJobResponse(BaseModel):
    """Response when starting an async scan"""
    job_id: str
    scan_id: int
    status: str = "queued"
    message: str = "Scan job queued successfully"


class ScanJobStatus(BaseModel):
    """Schema for scan job status response"""
    job_id: str
    scan_id: int
    status: str
    progress: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
