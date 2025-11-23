"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock environment variables before importing main
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock all required environment variables"""
    monkeypatch.setenv("SPREADSHEET_ID", "test_spreadsheet_id")
    monkeypatch.setenv("GOOGLE_CREDENTIALS", '{"type":"service_account","project_id":"test","private_key_id":"test","private_key":"-----BEGIN PRIVATE KEY-----\\ntest\\n-----END PRIVATE KEY-----\\n","client_email":"test@test.iam.gserviceaccount.com","client_id":"123","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"test"}')
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "test_sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test_token")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+15551234567")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("API_KEY", "test_api_key")
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")


@pytest.fixture
def client(mock_env_vars):
    """Create a test client"""
    # Clear any cached settings
    from config import get_settings
    get_settings.cache_clear()

    from main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    @patch('main.get_worksheet')
    def test_health_check_healthy(self, mock_worksheet, client):
        """Test health check returns healthy status"""
        mock_worksheet.return_value = MagicMock()

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert data["service"] == "MOWOC SMS Intake API"
        assert "checks" in data

    def test_health_check_structure(self, client):
        """Test health check response structure"""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "version" in data


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""

    def test_create_client_no_auth(self, client):
        """Test create client without API key returns 401"""
        response = client.post("/api/clients/create", json={
            "full_name": "Doe, John",
            "age": 65,
            "phone_number": "5551234567",
            "email": "john@example.com",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "referral_source": "Friend",
            "request_reason": "Need meals",
            "has_pets": "No",
            "has_weapons": "No",
            "emergency_contact_name": "Smith, Jane",
            "emergency_contact_phone": "5559876543"
        })
        assert response.status_code == 401

    def test_get_client_no_auth(self, client):
        """Test get client without API key returns 401"""
        response = client.get("/api/clients/test@example.com")
        assert response.status_code == 401

    def test_update_client_no_auth(self, client):
        """Test update client without API key returns 401"""
        response = client.put("/api/clients/update", json={
            "email": "test@example.com",
            "phone_number": "5551234567",
            "updates": {"age": 66}
        })
        assert response.status_code == 401

    def test_invalid_api_key(self, client):
        """Test invalid API key returns 403"""
        response = client.get(
            "/api/clients/test@example.com",
            headers={"X-API-Key": "wrong_key"}
        )
        assert response.status_code == 403


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_html_or_json(self, client):
        """Test root endpoint returns content"""
        response = client.get("/")
        assert response.status_code == 200


class TestInputValidation:
    """Test input validation on endpoints"""

    def test_create_client_missing_fields(self, client):
        """Test create client with missing required fields"""
        response = client.post(
            "/api/clients/create",
            json={"full_name": "Test"},
            headers={"X-API-Key": "test_api_key"}
        )
        assert response.status_code == 422  # Validation error

    def test_create_client_invalid_data(self, client):
        """Test create client with invalid data types"""
        response = client.post(
            "/api/clients/create",
            json={
                "full_name": "Doe, John",
                "age": "not_a_number",  # Should be int
                "phone_number": "5551234567",
                "email": "john@example.com",
                "street_address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "referral_source": "Friend",
                "request_reason": "Need meals",
                "has_pets": "No",
                "has_weapons": "No",
                "emergency_contact_name": "Smith, Jane",
                "emergency_contact_phone": "5559876543"
            },
            headers={"X-API-Key": "test_api_key"}
        )
        assert response.status_code == 422


class TestSMSWebhook:
    """Test SMS webhook endpoint"""

    @patch('main.twilio_service')
    @patch('main.session_manager')
    def test_sms_webhook_start_command(self, mock_session, mock_twilio, client):
        """Test SMS webhook with START command"""
        mock_session.get_session.return_value = None
        mock_session.create_session.return_value = {
            "answers": {},
            "current_question_index": 0
        }

        response = client.post(
            "/sms-webhook",
            data={"From": "+15551234567", "Body": "START"}
        )
        assert response.status_code == 200
        assert "xml" in response.headers["content-type"]

    @patch('main.twilio_service')
    @patch('main.session_manager')
    def test_sms_webhook_empty_body(self, mock_session, mock_twilio, client):
        """Test SMS webhook with empty body"""
        response = client.post(
            "/sms-webhook",
            data={"From": "+15551234567", "Body": ""}
        )
        # Should return valid TwiML even with empty body
        assert response.status_code == 200


class TestSecurityHeaders:
    """Test security headers are present"""

    def test_security_headers_present(self, client):
        """Test that security headers are added to responses"""
        response = client.get("/health")

        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers


class TestRateLimiting:
    """Test rate limiting"""

    def test_rate_limit_headers(self, client):
        """Test rate limit headers are present"""
        response = client.get("/health")

        assert "x-ratelimit-remaining" in response.headers
        assert "x-ratelimit-limit" in response.headers
