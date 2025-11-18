"""
ScanResult model
Represents individual findings from a scan
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class Severity(str, enum.Enum):
    """Severity level enumeration"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, enum.Enum):
    """Issue type enumeration"""
    DEPRECATED_FUNCTION = "deprecated_function"
    DEPRECATED_HOOK = "deprecated_hook"
    REMOVED_FUNCTION = "removed_function"
    BREAKING_CHANGE = "breaking_change"
    SECURITY_ISSUE = "security_issue"
    COMPATIBILITY_WARNING = "compatibility_warning"


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)

    issue_type = Column(Enum(IssueType), nullable=False)
    severity = Column(Enum(Severity), nullable=False)

    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)

    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="results")

    def __repr__(self):
        return f"<ScanResult(id={self.id}, severity={self.severity})>"
