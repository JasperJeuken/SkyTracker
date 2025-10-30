"""Authentication functionality"""
import secrets

from fastapi import Header, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from skytracker.settings import settings
from skytracker.utils import log_and_raise_http


http_basic_scheme = HTTPBasic()


async def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(http_basic_scheme)) -> None:
    """Verity the HTTP basic authentication credentials

    Args:
        credentials (HTTPBasicCredentials, optional): creds. Defaults to Depends(http_basic_scheme).
    """
    current_username_bytes = credentials.username.encode('utf8')
    correct_username_bytes = settings.http_user.encode('utf8')
    is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
    
    current_password_bytes = credentials.password.encode('utf8')
    correct_password_bytes = settings.http_password.encode('utf8')
    is_correct_password = secrets.compare_digest(current_password_bytes, correct_password_bytes)

    if not (is_correct_username and is_correct_password):
        log_and_raise_http('Incorrect username and/or password', 401,
                           headers={'WWW-Authenticate': 'Basic'})
    return None


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    """Verify the request contains a valid API key

    Args:
        x_api_key (str, optional): API key. Defaults to Header(...).
    """
    if not settings.api_key:
        log_and_raise_http('Server API key not configured correctly', 500)
    
    if x_api_key != settings.api_key:
        log_and_raise_http('Invalid or missing API key (X-API-Key header)', 401)
