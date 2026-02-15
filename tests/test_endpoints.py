import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Tatarana OCR Engine" in data["message"]


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "dependencies" in data


def test_show_config_endpoint():
    """Test configuration display endpoint."""
    response = client.get("/api/v1/show-config")
    assert response.status_code == 200
    data = response.json()
    assert "app_config" in data
    assert "llm_config" in data
    assert "google_drive_config" in data


def test_identify_file_endpoint_missing_config():
    """Test identify file endpoint without proper configuration."""
    response = client.post(
        "/api/v1/identify-file",
        json={"file_id": "test_file_id"}
    )
    # Should return 500 due to missing API keys
    assert response.status_code == 500


def test_ocr_file_endpoint_missing_config():
    """Test OCR file endpoint without proper configuration."""
    response = client.post(
        "/api/v1/ocr-file",
        json={"file_id": "test_file_id"}
    )
    # Should return 500 due to missing API keys
    assert response.status_code == 500


def test_bank_statement_endpoints_missing_config():
    """Test bank statement endpoints without proper configuration."""
    endpoints = [
        "/api/v1/ocr-bank-statement-picpay",
        "/api/v1/ocr-bank-statement-itau"
    ]
    
    for endpoint in endpoints:
        response = client.post(
            endpoint,
            json={"file_id": "test_file_id"}
        )
        # Should return 500 due to missing API keys
        assert response.status_code == 500


def test_credit_card_endpoints_missing_config():
    """Test credit card endpoints without proper configuration."""
    endpoints = [
        "/api/v1/ocr-cc-statement-picpay",
        "/api/v1/ocr-cc-statement-itau",
        "/api/v1/ocr-cc-statement-xp"
    ]
    
    for endpoint in endpoints:
        response = client.post(
            endpoint,
            json={"file_id": "test_file_id"}
        )
        # Should return 500 due to missing API keys
        assert response.status_code == 500
