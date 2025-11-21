import requests
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Configuration
API_URL = "http://localhost:8000/api/v1"
# Use dummy credentials or assume no auth for this specific endpoint test if possible, 
# but the endpoint requires auth. 
# For this test script to work without running the full server, we might need to mock or 
# just rely on the fact that we implemented the code correctly and the previous verification passed.
# However, to be thorough, we should try to hit the endpoint if the server was running.
# Since I can't easily start the full server and keep it running in background while running this script 
# (I can, but it's complex with tool limitations), I will create a unit-test style script 
# that imports the app and uses TestClient.

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_upload_endpoint():
    print("Testing upload endpoint...")
    
    # We need a user and token first, or mock the dependency.
    # For simplicity, let's try to mock the dependency override.
    from app.api.dependencies import get_current_user
    from app.models.user import User
    
    mock_user = User(id=1, email="test@example.com")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    # Mock DB
    from app.db.session import get_db
    from unittest.mock import MagicMock
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # Mock Site query
    mock_site = MagicMock()
    mock_site.id = 1
    mock_site.user_id = mock_user.id
    mock_db.query.return_value.filter.return_value.first.return_value = mock_site
    
    # Mock db.refresh to set ID and created_at
    def mock_refresh(obj):
        obj.id = 123
        from datetime import datetime
        obj.created_at = datetime.now()
        
    mock_db.refresh.side_effect = mock_refresh
    
    # Create dummy zip
    with open("test.zip", "wb") as f:
        f.write(b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00") # Empty zip signature
        
    try:
        files = {'file': ('test.zip', open('test.zip', 'rb'), 'application/zip')}
        data = {
            'site_id': str(mock_site.id),
            'wordpress_version_from': '5.9',
            'wordpress_version_to': '6.4'
        }
        
        # We expect this to fail with 500 because we didn't mock everything (like BackgroundTasks or DB add),
        # or succeed if we mocked enough.
        # Actually, BackgroundTasks might need handling.
        
        response = client.post("/api/v1/scans/upload", files=files, data=data)
        
        print(f"Response status: {response.status_code}")
        if response.status_code != 202:
            print(f"Response body: {response.text}")
            
    finally:
        if os.path.exists("test.zip"):
            os.remove("test.zip")

if __name__ == "__main__":
    # Set dummy env vars for config
    os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
    os.environ["SECRET_KEY"] = "dummy"
    os.environ["ANTHROPIC_API_KEY"] = "dummy"
    
    try:
        test_upload_endpoint()
    except Exception as e:
        print(f"Test failed: {e}")
