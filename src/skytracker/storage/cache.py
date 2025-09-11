"""Data cache module"""
from copy import deepcopy
from typing import Generic, TypeVar, List, Optional

from asyncio import Lock


T = TypeVar('T')


class Cache(Generic(T)):
    """Generic async-safe cache for storing batch of items"""

    def __init__(self):
        """Initialize cache data storage and async lock"""
        self._data: List[T] = []
        self._lock: Lock = Lock()
    
    async def set(self, items: List[T]) -> None:
        """Replace cache contents with new batch of items

        Args:
            items (List[T]): new batch of items to cache
        """
        async with self._lock:
            self._data = items
    
    async def get(self, limit: Optional[int] = None) -> List[T]:
        """Get the cached items

        Args:
            limit (int, optional): maximum number of states to get (None = all)
        
        Returns:
            List[T]: copy of cached items
        """
        async with self._lock:
            if limit is not None:
                return deepcopy(self._data[:min(limit, len(self._data))])
            return deepcopy(self._data)
    
    async def clear(self) -> None:
        """Clear the cache"""
        async with self._lock:
            self._data = []
    
    async def length(self) -> int:
        """Get the number of items stored in the cache

        Returns:
            int: number of items in cache
        """
        async with self._lock:
            return len(self._data)

    async def empty(self) -> bool:
        """Check if the cache is empty

        Returns:
            bool: whether cache is empty
        """
        return (await self.length()) == 0
