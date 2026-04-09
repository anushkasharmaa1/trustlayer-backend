"""
auth.py
-------
FastAPI dependency that validates the X-API-KEY header on every request.
Inject `verify_api_key` as a dependency on any route that requires auth.
"""

from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import get_settings

# Declare the header scheme — OpenAPI will expose this in /docs
API_KEY_HEADER = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Raises HTTP 401 if the key is missing or incorrect.
    Returns the validated key string on success.
    """
    settings = get_settings()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-KEY header.",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return api_key
