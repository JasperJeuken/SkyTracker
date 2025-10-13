"""API dependencies"""
from typing import Optional

from skytracker.services.browser import WebBrowser
from skytracker.storage import Storage


storage: Optional[Storage] = None
browser: Optional[WebBrowser] = None


async def get_storage() -> Storage:
    """Get instance of database storage

    Returns:
        Storage: database storage instance
    """
    if storage is None:
        raise RuntimeError('Database storage was not initialized')
    return storage


async def get_browser() -> WebBrowser:
    """Get instance of web browser

    Returns:
        WebBrowser: web browser instance
    """
    if browser is None:
        raise RuntimeError('Web browser was not initialized')
    return browser
