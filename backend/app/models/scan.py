"""
Scan model
Represents a WordPress compatibility scan
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.base import Base


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScanStatus(str, enum.Enum):
    """Scan status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    wordpress_version_from = Column(String, nullable=False)
    wordpress_version_to = Column(String, nullable=False)

    status = Column(
        Enum(ScanStatus),
        default=ScanStatus.PENDING,
        nullable=False
    )
    risk_level = Column(Enum(RiskLevel), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    site = relationship("Site", back_populates="scans")
    user = relationship("User", back_populates="scans")
    results = relationship("ScanResult", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan(id={self.id}, status={self.status})>"
