import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.models.user import User, UserPlan
from app.models.site import Site
from app.models.scan import Scan, ScanStatus
from app.core.security import create_access_token

# Setup in-memory SQLite DB
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def free_user(db):
    user = User(
        email="free@example.com",
        hashed_password="hashed_password",
        name="Free User",
        plan=UserPlan.FREE,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def pro_user(db):
    user = User(
        email="pro@example.com",
        hashed_password="hashed_password",
        name="Pro User",
        plan=UserPlan.PRO,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def user_token(free_user):
    return create_access_token(data={"user_id": free_user.id})

@pytest.fixture
def pro_token(pro_user):
    return create_access_token(data={"user_id": pro_user.id})

def test_pdf_download_endpoint(db, pro_user, pro_token):
    # Create a site first
    site = Site(user_id=pro_user.id, url="http://pdf-test.com", name="PDF Test Site")
    db.add(site)
    db.commit()

    # Create a completed scan
    scan = Scan(
        user_id=pro_user.id,
        site_id=site.id,
        status=ScanStatus.COMPLETED,
        wordpress_version_from="5.0",
        wordpress_version_to="6.0",
        created_at=datetime.utcnow()
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Mock PDF generation to avoid reportlab dependency issues in test env if missing
    with patch("app.api.v1.endpoints.scans.PDFReportGenerator") as MockGenerator:
        mock_instance = MockGenerator.return_value
        mock_instance.generate.return_value = b"%PDF-1.4 mock content"
        
        print(f"DEBUG: Scan ID: {scan.id}, User ID: {scan.user_id}, Pro User ID: {pro_user.id}")
        
        response = client.get(
            f"/api/v1/scans/{scan.id}/report",
            headers={"Authorization": f"Bearer {pro_token}"}
        )
        
        print(f"DEBUG: Response: {response.status_code} {response.text}")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content == b"%PDF-1.4 mock content"

def test_scan_limit_enforcement(db, free_user, user_token):
    # Create a site
    site = Site(user_id=free_user.id, url="http://example.com", name="Test Site")
    db.add(site)
    db.commit()
    
    # 1. First scan should succeed (limit is 1/day)
    # We mock the upload to avoid file system ops
    with patch("app.api.v1.endpoints.scans.shutil.copyfileobj"), \
         patch("app.api.v1.endpoints.scans.BackgroundTasks.add_task"):
        
        files = {'file': ('test.zip', b'test content', 'application/zip')}
        data = {
            'site_id': site.id,
            'wordpress_version_from': '5.0',
            'wordpress_version_to': '6.0'
        }
        
        response = client.post(
            "/api/v1/scans/upload",
            headers={"Authorization": f"Bearer {user_token}"},
            files=files,
            data=data
        )
        assert response.status_code == 202
        
        # 2. Second scan should fail
        response = client.post(
            "/api/v1/scans/upload",
            headers={"Authorization": f"Bearer {user_token}"},
            files=files,
            data=data
        )
        assert response.status_code == 403
        assert "Daily scan limit reached" in response.json()["detail"]

def test_pro_user_unlimited_scans(db, pro_user, pro_token):
    # Create a site
    site = Site(user_id=pro_user.id, url="http://pro.example.com", name="Pro Site")
    db.add(site)
    db.commit()
    
    with patch("app.api.v1.endpoints.scans.shutil.copyfileobj"), \
         patch("app.api.v1.endpoints.scans.BackgroundTasks.add_task"):
        
        files = {'file': ('test.zip', b'test content', 'application/zip')}
        data = {
            'site_id': site.id,
            'wordpress_version_from': '5.0',
            'wordpress_version_to': '6.0'
        }
        
        # Run multiple scans
        for _ in range(3):
            response = client.post(
                "/api/v1/scans/upload",
                headers={"Authorization": f"Bearer {pro_token}"},
                files=files,
                data=data
            )
            assert response.status_code == 202

