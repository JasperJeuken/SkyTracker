"""Aircraft state table manager"""
from typing import Optional

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.tables.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.models.state import State


class StateTableManager(TableManager):
    """Async aircraft state table manager"""

    TABLE_NAME = 'aircraft_states'
    """str: name of aircraft state table"""

    def __init__(self, database: DatabaseManager) -> None:
        """Initialize table manager by storing database manager

        Args:
            database (DatabaseManager): ClickHouse database manager
        """
        self._database: DatabaseManager = database
        self._cache: Cache[State] = Cache[State]()

    async def ensure_exists(self) -> None:
        """Ensure aircraft state table exists"""
        # Skip if table already exists
        if await self.exists():
            return
        
        # Fields for state table
        fields = [
            'time UInt32 NOT NULL',
            'icao24 FixedString(6) NOT NULL',
            'callsign Nullable(FixedString(8))',
            'origin_country String NOT NULL',
            'time_position Nullable(UInt32)',
            'last_contact UInt32 NOT NULL',
            'longitude Nullable(Float64)',
            'latitude Nullable(Float64)',
            'baro_altitude Nullable(Float64)',
            'on_ground Bool NOT NULL',
            'velocity Nullable(Float64)',
            'true_track Nullable(Float64)',
            'vertical_rate Nullable(Float64)',
            'sensors Array(UInt32)',
            'geo_altitude Nullable(Float64)',
            'squawk Nullable(String)',
            'spi Bool NOT NULL',
            'position_source UInt8 NOT NULL',
            'category UInt8 NOT NULL'
        ]

        # Create table
        await self._database.create_table(self.STATE_TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          'ORDER BY (icao24, time)',
                                          'SETTINGS index_granularity=8192')
    
    async def exists(self) -> bool:
        """Check if the aircraft state table exists

        Returns:
            bool: whether the aircraft state table exists
        """
        return await self._database.table_exists(self.TABLE_NAME)

    async def insert_states(self, states: list[State]) -> None:
        """Insert a list of states in the table

        Args:
            states (list[State]): list of states to insert
        """
        await self._cache.set(states)
        rows = [list(state.to_json().values()) for state in states]
        columns = State.FIELDS
        await self._database.insert(self.TABLE_NAME, rows, columns)

    async def insert_state(self, state: State) -> None:
        """Insert a state in the table

        Args:
            state (State): state to insert
        """
        await self.insert_states([state])

    async def query(self, sql_query: str) -> list[State]:
        """Select rows from the aircraft state table with an SQL query

        Args:
            sql_query (str): SQL query

        Returns:
            list[State]: list of matching states (if any)
        """
        if not isinstance(sql_query, str) or len(sql_query) < 1:
            raise ValueError(f'Invalid SQL query: "{sql_query}"')
        if not sql_query.endswith(';'):
            sql_query += ';'
        rows = await self._database.query(sql_query)
        return [State.from_raw(row) for row in rows]

    async def get_aircraft_history(self, icao24: str, limit: int = 0) -> list[State]:
        """Get the state history of a specific aircraft

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex)
            limit (int): maximum number of states to get (latest first, 0=all)

        Returns:
            list[State]: list of aircraft states
        """
        # Catch incorrect arguments
        if not isinstance(icao24, str) or len(icao24) != 6:
            raise ValueError(f'ICAO 24-bit address must be a 6-character string, got "{icao24}"')
        if not isinstance(limit, int) or limit < 0:
            raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}"')
        
        # Run select query
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE icao24='{icao24}' ORDER BY time DESC"
        if limit > 0:
            query += f' LIMIT {limit}'
        result = await self.query(query)
        return result
    
    async def get_last_aircraft_state(self, icao24: str) -> Optional[State]:
        """Get the last known state of a specific aircraft

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex)

        Returns:
            Optional[State]: last known aircraft state, or None if not found
        """
        result = await self.get_aircraft_history(icao24, limit=1)
        if len(result) == 0:
            return None
        return result[0]
    
    async def get_latest_batch(self, limit: int = 0) -> list[State]:
        """Get the latest batch of states in the table

        Args:
            limit (int):  maximum number of states to get (0=all)

        Returns:
            list[State]: list of aircraft states in last batch
        """
        # Catch incorrect argument
        if not isinstance(limit, int) or limit < 0:
            raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}"')
        
        # Use cached data if available
        if not await self._cache.empty():
            return await self._cache.get(limit)

        # Run select query
        query = f'SELECT * FROM {self.TABLE_NAME} WHERE time=(SELECT MAX(time) ' + \
                f'FROM {self.TABLE_NAME})'
        if limit:
            query += f' LIMIT {limit}'
        result = await self.query(query)
        return result
    
    async def count(self) -> int:
        """Get the number of states stored in the table

        Returns:
            int: number of states stored in table
        """
        result = await self.query(f'SELECT COUNT(*) FROM {self.TABLE_NAME}')
        return result[0][0]
