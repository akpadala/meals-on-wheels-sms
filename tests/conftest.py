"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_env_vars():
    """Provide test environment variable values"""
    return {
        "SPREADSHEET_ID": "test_spreadsheet_id",
        "GOOGLE_CREDENTIALS": '{"type":"service_account","project_id":"test","private_key_id":"test","private_key":"-----BEGIN PRIVATE KEY-----\\ntest\\n-----END PRIVATE KEY-----\\n","client_email":"test@test.iam.gserviceaccount.com","client_id":"123","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"test"}',
        "TWILIO_ACCOUNT_SID": "test_sid",
        "TWILIO_AUTH_TOKEN": "test_token",
        "TWILIO_PHONE_NUMBER": "+15551234567",
        "OPENAI_API_KEY": "test_key",
        "API_KEY": "test_api_key",
        "ENV": "development",
        "CORS_ORIGINS": "http://localhost:3000"
    }


@pytest.fixture
def sample_client_data():
    """Provide sample client data for tests"""
    return {
        "full_name": "Doe, John",
        "age": 65,
        "phone_number": "5551234567",
        "email": "john@example.com",
        "street_address": "123 Main St",
        "apt_unit": None,
        "city": "Anytown",
        "state": "CA",
        "zip_code": "12345",
        "referral_source": "Friend",
        "request_reason": "Need meals",
        "has_pets": "No",
        "pet_details": None,
        "has_weapons": "No",
        "emergency_contact_name": "Smith, Jane",
        "emergency_contact_phone": "5559876543"
    }


@pytest.fixture
def sample_session_data():
    """Provide sample session data for tests"""
    return {
        "phone_number": "+15551234567",
        "stage": "collecting_info",
        "started_at": "2024-01-01T00:00:00",
        "last_activity": "2024-01-01T00:00:00",
        "messages": [],
        "collected_data": {},
        "current_question_index": 0,
        "questions_asked": [],
        "answers": {}
    }
