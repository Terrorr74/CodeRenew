# Import all models here for Alembic auto-generation
from app.models.base import Base
from app.models.user import User
from app.models.site import Site
from app.models.scan import Scan
from app.models.scan_result import ScanResult

__all__ = ["Base", "User", "Site", "Scan", "ScanResult"]
