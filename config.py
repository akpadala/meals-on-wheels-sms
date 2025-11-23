"""
Configuration management with environment variable validation
"""
import os
import sys
import json
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with validation"""

    # Google Sheets
    SPREADSHEET_ID: str
    GOOGLE_CREDENTIALS: str

    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    # OpenAI
    OPENAI_API_KEY: str

    # CORS - with secure default
    CORS_ORIGINS: str = "https://yourdomain.com"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # API Authentication
    API_KEY: Optional[str] = None

    # Application
    ENV: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000

    @field_validator('GOOGLE_CREDENTIALS')
    @classmethod
    def validate_google_credentials(cls, v):
        """Validate that GOOGLE_CREDENTIALS is valid JSON"""
        try:
            creds = json.loads(v)
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            for field in required_fields:
                if field not in creds:
                    raise ValueError(f"Missing required field in GOOGLE_CREDENTIALS: {field}")
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f"GOOGLE_CREDENTIALS must be valid JSON: {e}")

    @field_validator('TWILIO_PHONE_NUMBER')
    @classmethod
    def validate_twilio_phone(cls, v):
        """Validate Twilio phone number format"""
        if not v.startswith('+'):
            raise ValueError("TWILIO_PHONE_NUMBER must be in E.164 format (e.g., +14155551234)")
        return v

    @field_validator('CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v):
        """Warn if CORS is set to wildcard in production"""
        if v == "*":
            logger.warning(
                "⚠️  CORS_ORIGINS is set to '*' which allows all origins. "
                "This is insecure for production. Set specific origins instead."
            )
        return v

    @property
    def cors_origins_list(self) -> list:
        """Return CORS origins as a list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def google_credentials_dict(self) -> dict:
        """Return Google credentials as a dictionary"""
        return json.loads(self.GOOGLE_CREDENTIALS)

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENV.lower() == "production"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings

    Validates all environment variables on first call.
    Raises SystemExit if validation fails.
    """
    try:
        return Settings()
    except ValidationError as e:
        logger.error("❌ Configuration validation failed!")
        logger.error("Please check your environment variables:")
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            logger.error(f"  - {field}: {msg}")
        sys.exit(1)


def validate_config_on_startup():
    """
    Validate configuration at application startup

    Call this in your application's startup to ensure all
    required environment variables are set and valid.
    """
    logger.info("🔍 Validating configuration...")
    settings = get_settings()

    # Log configuration status (without sensitive values)
    logger.info("✅ Configuration validated successfully")
    logger.info(f"  - Environment: {settings.ENV}")
    logger.info(f"  - Debug mode: {settings.DEBUG}")
    logger.info(f"  - Log level: {settings.LOG_LEVEL}")
    logger.info(f"  - CORS origins: {len(settings.cors_origins_list)} origin(s) configured")
    logger.info(f"  - Rate limiting: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW}s")
    logger.info(f"  - API key authentication: {'enabled' if settings.API_KEY else 'disabled'}")

    if not settings.API_KEY:
        logger.warning("⚠️  API_KEY is not set. API endpoints are unprotected!")

    return settings
