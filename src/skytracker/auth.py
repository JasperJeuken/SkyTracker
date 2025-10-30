"""Authentication functionality"""
from fastapi import Header

from skytracker.settings import settings
from skytracker.utils import log_and_raise_http


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    """Verify the request contains a valid API key

    Args:
        x_api_key (str, optional): API key. Defaults to Header(...).
    """
    if not settings.api_key:
        log_and_raise_http('Server API key not configured correctly', 500)
    
    if x_api_key != settings.api_key:
        log_and_raise_http('Invalid or missing API key (X-API-Key header)', 401)
