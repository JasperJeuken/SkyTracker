"""Airline table manager"""
from typing import Any

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.services.api.aviation_edge import AviationEdgeAPI
from skytracker.models.airline import Airline
from skytracker.utils import logger, log_and_raise
from skytracker.settings import settings
from skytracker.utils.analysis import search_object_list


class AirlineTableManager(TableManager[Airline]):
    """Async airline table manager"""

    TABLE_NAME = 'airline'
    """str: name of airline table"""

    def __init__(self, database: DatabaseManager) -> None:
        """Initialize table manager by storing database manager

        Args:
            database (DatabaseManager): ClickHouse database manager
        """
        super().__init__(database, Cache[Airline]())

    async def ensure_exists(self) -> None:
        """Ensure airline table exists"""
        # If table already exists, load into cache
        if await self._database.table_exists(self.TABLE_NAME):
            logger.debug(f'Table "{self.TABLE_NAME}" exists, loading into cache...')
            await self._load_from_database()
            return

        # Fields for airline table
        fields = [
            'iata FixedString(3)',
            'icao FixedString(4)',
            'name String',
            'callsign String',
            'founding UInt16',
            'fleet_age Float',
            'fleet_size UInt16',
            "status Enum('MERGED', 'HISTORICAL', 'DISABLED', 'NOT_READY', 'UNKNOWN', " + \
                "'START_UP', 'RESTARTING', 'ACTIVE', 'RENAMED')",
            "types Array(Enum('SCHEDULED', 'CHARTER', 'CARGO', 'VIRTUAL', 'LEISURE', " + \
                "'GOVERNMENT', 'PRIVATE', 'MANUFACTURER', 'SUPPLIED', 'DIVISION'))",
            'country_iso2 FixedString(2)',
            'hub_icao Nullable(FixedString(4))'
        ]

        # Create table
        airlines = self._collect_airlines()
        logger.info(f'Table "{self.TABLE_NAME}" does not exist, creating...')
        await self._cache.set(airlines)
        await self._database.create_table(self.TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          'ORDER BY tuple()',
                                          'SETTINGS index_granularity=1024')
        await self._insert_airlines(airlines)
    
    async def _load_from_database(self) -> None:
        """Load cache from database"""
        # Get rows from database
        query = f'SELECT * FROM {self.TABLE_NAME}'
        rows = await self._database.sql_query(query)
        logger.info(f'Retrieved {len(rows)} airlines from server')

        # Parse into airline list
        field_names = Airline.model_fields.keys()
        airlines = [Airline(**dict(zip(field_names, row))) for row in rows]
        await self._cache.set(airlines)
    
    def _collect_airlines(self) -> list[Airline]:
        """Collect airline database from Aviation Edge API

        Returns:
            list[Airline]: airline database
        """
        api = AviationEdgeAPI(settings.aviation_edge_api_key)
        airlines = api.get_airline_database()
        logger.debug(f'Retrieved {len(airlines)} airlines.')
        return airlines
    
    async def _insert_airlines(self, airlines: list[Airline]) -> None:
        """Insert airlines into database

        Args:
            airlines (list[Airline]): list of airlines to insert
        """
        logger.debug(f'Inserting {len(airlines)} airlines into database...')
        rows = [list(airline.model_dump().values()) for airline in airlines]
        columns = list(airlines[0].model_dump().keys())
        logger.debug(f'Inserting {len(airlines)} airlines into database')
        await self._database.insert(self.TABLE_NAME, rows, columns)
    
    async def get_airline(self, icao: str) -> Airline:
        """Get an airline by ICAO code

        Args:
            icao (str): airline ICAO code

        Returns:
            Airline: airline with specified ICAO code
        """
        airlines = await self._cache.get()
        for airline in airlines:
            if airline.icao is None:
                continue
            if airline.icao.lower() == icao.lower():
                return airline
        log_and_raise(KeyError, f'No airline with ICAO code "{icao}"')
    
    async def search_airline(self, fields: dict[str, Any], limit: int = 0) -> list[Airline]:
        """Search for airlines matching specific information

        Args:
            fields (dict[str, Any]): field-value pairs to search for
            limit (int, optional): maximum number of airlines to retrieve (0=all). Defaults to 0.

        Returns:
            list[Airline]: list of airlines matching fields
        """
        airlines = await self._cache.get()
        return search_object_list(airlines, fields, limit)
