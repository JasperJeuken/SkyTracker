"""Abstract table query"""
from abc import ABC, abstractmethod

from skytracker.models.state import State
from skytracker.storage.database_manager import DatabaseManager


class TableQuery(ABC):
    """Abstract table query"""

    @abstractmethod
    async def from_cache(self, states: list[State]) -> list[State]: ...
    """Query a list of states from cache
    
    Args:
        states (list[State]): unfiltered list of states

    Returns:
        list[State]: filtered list of states
    """

    @abstractmethod
    async def from_server(self, table: str, db: DatabaseManager) -> list[State]: ...
    """Query a list of states from server database
    
    Args:
        table (str): name of database table
        db (DatabaseManager): database manager instance
    
    Returns:
        list[State]: selected list of states
    """
