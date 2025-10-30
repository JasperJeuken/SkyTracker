"""Airport table manager"""
from typing import Any

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.services.api.aviation_edge import AviationEdgeAPI
from skytracker.models.airport import Airport
from skytracker.utils import logger, log_and_raise
from skytracker.utils.analysis import search_object_list
from skytracker.settings import settings


class AirportTableManager(TableManager[Airport]):
    """Async airport table manager"""

    TABLE_NAME = 'airport'
    """str: name of airport table"""

    def __init__(self, database: DatabaseManager) -> None:
        """Initialize table manager by storing database manager

        Args:
            database (DatabaseManager): ClickHouse database manager
        """
        super().__init__(database, Cache[Airport]())

    async def ensure_exists(self) -> None:
        """Ensure airport table exists"""
        # If table already exists, load into cache
        if await self._database.table_exists(self.TABLE_NAME):
            logger.debug(f'Table "{self.TABLE_NAME}" exists, loading into cache...')
            await self._load_from_database()
            return

        # Fields for airport table
        fields = [
            'iata FixedString(3)',
            'icao Nullable(FixedString(4))',
            'name Nullable(String)',
            'latitude Nullable(Float)',
            'longitude Nullable(Float)',
            'geoname_id Nullable(UInt32)',
            'phone Nullable(String)',
            'timezone Nullable(String)',
            'gmt Nullable(FixedString(5))',
            'city_iata Nullable(FixedString(3))',
            'country_iso2 FixedString(2)',
            'country_name String'
        ]

        # Create table
        airports = self._collect_airports()
        logger.info(f'Table "{self.TABLE_NAME}" does not exist, creating...')
        await self._cache.set(airports)
        await self._database.create_table(self.TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          'ORDER BY (iata)',
                                          'SETTINGS index_granularity=1024')
        await self._insert_airports(airports)
    
    async def _load_from_database(self) -> None:
        """Load cache from database"""
        # Get rows from database
        query = f'SELECT * FROM {self.TABLE_NAME}'
        rows = await self._database.sql_query(query)
        logger.info(f'Retrieved {len(rows)} airports from server')

        # Parse into airport list
        field_names = Airport.model_fields.keys()
        airports = [Airport(**dict(zip(field_names, row))) for row in rows]
        await self._cache.set(airports)
    
    def _collect_airports(self) -> list[Airport]:
        """Collect airport database from Aviation Edge API

        Returns:
            list[Airport]: airport database
        """
        api = AviationEdgeAPI(settings)
        airports = api.get_airport_database()
        logger.debug(f'Retrieved {len(airports)} airports.')
        return airports
    
    async def _insert_airports(self, airports: list[Airport]) -> None:
        """Insert airports into database

        Args:
            airports (list[Airport]): list of airports to insert
        """
        logger.debug(f'Inserting {len(airports)} airports into database...')
        rows = [list(airport.model_dump().values()) for airport in airports]
        columns = list(airports[0].model_dump().keys())
        logger.debug(f'Inserting {len(airports)} airports into database')
        await self._database.insert(self.TABLE_NAME, rows, columns)
    
    async def get_airport(self, iata: str) -> Airport:
        """Get an airport by IATA code

        Args:
            iata (str): airport IATA code

        Returns:
            Airport: airport with specified IATA code
        """
        airports = await self._cache.get()
        for airport in airports:
            if airport.iata is None:
                continue
            if airport.iata.lower() == iata.lower():
                return airport
        log_and_raise(KeyError, f'No airport with IATA code "{iata}"')
    
    async def search_airport(self, fields: dict[str, Any], limit: int = 0) -> list[Airport]:
        """Search for airports matching specific information

        Args:
            fields (dict[str, Any]): field-value pairs to search for
            limit (int, optional): maximum number of airports to retrieve (0=all). Defaults to 0.

        Returns:
            list[Airport]: list of airports matching fields
        """
        airports = await self._cache.get()
        return search_object_list(airports, fields, limit)
