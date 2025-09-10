"""Abstract table manager"""
from abc import ABC, abstractmethod


class TableManager(ABC):
    """Abstract table manager class"""

    @abstractmethod
    async def ensure_exists(self) -> None:
        """Function which ensures the table being managed exists, creating it if not"""
