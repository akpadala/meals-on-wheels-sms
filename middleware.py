"""
Security middleware for FastAPI application
"""
import time
import hmac
import hashlib
import logging
from typing import Callable, Dict
from collections import defaultdict
from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, requests_per_window: int = 100, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key"""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]

        # Check if under limit
        if len(self.requests[key]) >= self.requests_per_window:
            return False

        # Record this request
        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key"""
        now = time.time()
        window_start = now - self.window_seconds
        current_requests = len([
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ])
        return max(0, self.requests_per_window - current_requests)


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting"""

    def __init__(self, app, requests_per_window: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_window, window_seconds)

    async def dispatch(self, request: Request, call_next: Callable):
        # Get client identifier (IP or API key)
        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key", "")
        client_id = api_key if api_key else client_ip

        # Check rate limit
        if not self.limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self.limiter.window_seconds
                },
                headers={"Retry-After": str(self.limiter.window_seconds)}
            )

        # Add rate limit headers to response
        response = await call_next(request)
        remaining = self.limiter.get_remaining(client_id)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_window)

        return response


def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Verify API key for protected endpoints

    Usage:
        @app.get("/protected", dependencies=[Depends(verify_api_key)])
        async def protected_endpoint():
            ...
    """
    from config import get_settings
    settings = get_settings()

    # If no API key is configured, allow all requests (but warn)
    if not settings.API_KEY:
        return "no-auth"

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return api_key


def verify_twilio_signature(request: Request, body: bytes) -> bool:
    """
    Verify that a request came from Twilio

    This uses Twilio's request validation to ensure webhooks
    are actually from Twilio and not spoofed.

    Args:
        request: The FastAPI request object
        body: The raw request body

    Returns:
        True if signature is valid, False otherwise
    """
    from twilio.request_validator import RequestValidator
    from config import get_settings

    settings = get_settings()
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

    # Get the signature from headers
    signature = request.headers.get("X-Twilio-Signature", "")

    if not signature:
        logger.warning("Missing X-Twilio-Signature header")
        return False

    # Build the full URL that Twilio used
    # Note: In production behind a proxy, you may need to use X-Forwarded-Proto
    scheme = request.headers.get("X-Forwarded-Proto", request.url.scheme)
    url = f"{scheme}://{request.url.netloc}{request.url.path}"

    # Parse form data for validation
    try:
        # Decode body and parse as form data
        body_str = body.decode('utf-8')
        params = {}
        for pair in body_str.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                # URL decode
                from urllib.parse import unquote_plus
                params[unquote_plus(key)] = unquote_plus(value)
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        return False

    # Validate the request
    is_valid = validator.validate(url, params, signature)

    if not is_valid:
        logger.warning(f"Invalid Twilio signature for request to {url}")

    return is_valid


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"

        return response
