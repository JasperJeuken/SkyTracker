"""Abstract table query"""
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar, Any

from skytracker.models.state import State
from skytracker.storage.database_manager import DatabaseManager


EntryType = TypeVar('EntryType')


class TableQuery(Generic[EntryType], metaclass=ABCMeta):
    """Abstract table query"""

    @abstractmethod
    async def from_cache(self, states: list[State]) -> list[EntryType]:
        """Query a list of states from cache
        
        Args:
            states (list[State]): unfiltered list of states

        Returns:
            list[State]: filtered list of states
        """

    @abstractmethod
    async def from_server(self, table: str, db: DatabaseManager) -> list[EntryType]:
        """Query a list of states from server database
        
        Args:
            table (str): name of database table
            db (DatabaseManager): database manager instance
        
        Returns:
            list[State]: selected list of states
        """

    @abstractmethod
    def parse_table_row(self, raw_entry: Any) -> EntryType:
        """Parse the raw table format into an entry

        Args:
            raw_entry (Any): raw table row data

        Returns:
            EntryType: corresponding entry instance
        """
