"""Abstract table manager"""
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar, Optional

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.cache import Cache
from skytracker.storage.table_query import TableQuery


EntryType = TypeVar('EntryType')


class TableManager(Generic[EntryType], metaclass=ABCMeta):
    """Abstract table manager"""

    def __init__(self, database: DatabaseManager, cache: Optional[Cache[EntryType]] = None) -> None:
        """Initialize table manager with database manager and optional cache

        Args:
            database (DatabaseManager): ClickHouse database manager
            cache (Cache[EntryType], optional): cache for quick access. Default is None.
        """
        self._database: DatabaseManager = database
        self._cache: Optional[Cache[EntryType]] = cache

    @abstractmethod
    async def ensure_exists(self) -> None:
        """Function which ensures the table being managed exists, creating it if not"""

    async def _run_query(self, query: TableQuery[EntryType], table: str) -> list[EntryType]:
        """Run a table query

        Args:
            query (TableQuery): table query to run
            table (str): name of server table to get from

        Returns:
            list[State]: queried list of states
        """
        if query.allows_cache and not await self._cache.empty():
            return await query.from_cache(await self._cache.get())
        return await query.from_server(table, self._database)
