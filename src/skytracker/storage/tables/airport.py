"""Airport table manager"""
from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.services.api.aviation_edge import AviationEdgeAPI
from skytracker.models.airport import Airport
from skytracker.utils import logger
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
            'icao FixedString(4)',
            'name String',
            'latitude Nullable(Float)',
            'longitude Nullable(Float)',
            'geoname_id Nullable(UInt32)',
            'phone String',
            'timezone String',
            'gmt FixedString(5)',
            'city_iata FixedString(3)',
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
        api = AviationEdgeAPI(settings.aviation_edge_api_key)
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
