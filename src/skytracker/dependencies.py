"""API dependencies"""
from typing import Optional
from skytracker.storage import Storage


storage: Optional[Storage] = None


async def get_storage() -> Storage:
    """Get instance of database storage

    Returns:
        Storage: database storage instance
    """
    if storage is None:
        raise RuntimeError('Database storage was not initialized')
    return storage
