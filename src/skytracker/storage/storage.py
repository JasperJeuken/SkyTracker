"""General storage interaction class"""
from typing import Literal, overload

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.tables.state import StateTableManager


class Storage:
    """Central access point for all tables"""

    def __init__(self, username: str, password: str,
                 host: str = 'localhost', port: int = 8123, database: str = '__default__',
                 secure: bool = False) -> None:
        """Initialize storage by creating database and table managers

        Args:
            username (str): server username
            password (str): server password
            host (str, optional): server host. Defaults to 'localhost'.
            port (int, optional): server port. Defaults to 8123.
            database (str, optional): server database name. Defaults to '__default__'.
            secure (bool, optional): whether to use secure connection. Defaults to False.
        """
        self._database: DatabaseManager = DatabaseManager(username, password, host, port,
                                                          database, secure)
        self._tables: dict[Literal['state'], TableManager] = {
            'state': StateTableManager(self._database)
        }

    async def connect(self) -> None:
        """Connect to the database and ensure all tables exist"""
        await self._database.connect()
        for manager in self._tables.values():
            await manager.ensure_exists()

    async def close(self) -> None:
        """Close connection to the database"""
        await self._database.close()

    def tables(self) -> list[str]:
        """Get the names of the available tables

        Returns:
            list[str]: list of table names
        """
        return list(self._tables.keys())

    @overload
    def __getitem__(self, table_name: Literal['state']) -> StateTableManager: ...
    def __getitem__(self, table_name: str) -> TableManager:
        """Get the table manager associated with a specific table

        Args:
            table_name (str): name of table to get manager for

        Returns:
            TableManager: manager of specified table
        """
        return self._tables[table_name]
