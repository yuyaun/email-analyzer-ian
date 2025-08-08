"""Rate limiting utilities for the FastAPI application."""

import os

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import jwt

from app.core.config import settings


def _rate_limit_key(request: Request) -> str:
    """Build a rate-limit key from IP address and optional JWT user info."""
    ip = get_remote_address(request)
    auth = request.headers.get("authorization", "")
    token = ""
    if auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
    user_id = ""
    if token:
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("userSn") or payload.get("email") or ""
        except jwt.PyJWTError:
            pass
    return f"{user_id}:{ip}" if user_id else ip


limiter = Limiter(
    key_func=_rate_limit_key, storage_uri=os.getenv("RATE_LIMIT_REDIS_URL")
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Return a JSON response for rate limit exceed events."""
    return JSONResponse(
        status_code=429,
        content={"message": "Too many requests, please try again later."},
    )
