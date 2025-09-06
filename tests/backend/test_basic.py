import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the backend app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

def test_health_check():
    """Test the health check endpoint"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "No Smoking for You API"

def test_upload_endpoint_no_file():
    """Test upload endpoint without file"""
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/v1/upload-image")
    # Should return 422 for missing file
    assert response.status_code == 422

def test_upload_endpoint_no_auth():
    """Test upload endpoint without authentication"""
    from app.main import app
    client = TestClient(app)
    
    # Create a minimal JPEG file for testing
    test_image_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb"
    
    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("test.jpg", test_image_content, "image/jpeg")}
    )
    
    # Should return 403 for missing authentication
    assert response.status_code == 403  # FastAPI returns 403 for missing Bearer token
