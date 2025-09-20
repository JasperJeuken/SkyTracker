"""General storage interaction class"""
from typing import TypedDict, Literal, overload

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.tables.state import StateTableManager


class TableManagers(TypedDict):
    """Table manager dictionary"""
    state: StateTableManager
    """StateTableManager: aircraft state table manager"""


class Storage:
    """Central access point for all tables"""

    def __init__(self, username: str, password: str,
                 host: str = 'localhost', port: int = 8123, database: str = '__default__') -> None:
        """Initialize storage by creating database and table managers

        Args:
            username (str): server username
            password (str): server password
            host (str, optional): server host. Defaults to 'localhost'.
            port (int, optional): server port. Defaults to 8123.
            database (str, optional): server database name. Defaults to '__default__'.
        """
        self._database: DatabaseManager = DatabaseManager(username, password, host, port, database)
        self._tables: TableManagers = {
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


if __name__ == '__main__':
    import json
    import time

    async def _main():
        # Get database credentials
        with open('credentials.json', 'r', encoding='utf-8') as file:
            credentials = json.load(file)
        username, password = credentials['clickhouseUser'], credentials['clickhouseSecret']

        # Create storage manager
        storage = Storage(username, password)
        await storage.connect()

        # Run queries
        start = time.time()
        history = await storage['state'].get_aircraft_history('0081ef', limit=5)
        last = await storage['state'].get_last_aircraft_state('0081ef')
        batch = await storage['state'].get_latest_batch()
        end = time.time()
        print((end - start) * 1000, 'ms')

        # Print result
        for state in history:
            print(state.time, state.icao24, state.callsign, state.longitude, state.latitude)
        print(last)
        print(len(batch))

        # Close manager
        await storage.close()

    # Run main
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
