"""Aircraft table manager"""
from typing import Any

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.services.api.aviation_edge import AviationEdgeAPI
from skytracker.models.aircraft import Aircraft
from skytracker.utils import logger
from skytracker.utils.analysis import search_object_list
from skytracker.settings import settings


class AircraftTableManager(TableManager[Aircraft]):
    """Async aircraft table manager"""

    TABLE_NAME = 'aircraft'
    """str: name of aircraft table"""

    def __init__(self, database: DatabaseManager) -> None:
        """Initialize table manager by storing database manager

        Args:
            database (DatabaseManager): ClickHouse database manager
        """
        super().__init__(database, Cache[Aircraft]())

    async def ensure_exists(self) -> None:
        """Ensure aircraft table exists"""
        # If table already exists, load into cache
        if await self._database.table_exists(self.TABLE_NAME):
            logger.debug(f'Table "{self.TABLE_NAME}" exists, loading into cache...')
            await self._load_from_database()
            return

        # Fields for aircraft table
        fields = [
            'identity_icao24 FixedString(6)',
            'identity_registration FixedString(10)',
            'identity_test_registration Nullable(FixedString(10))',
            'identity_owner Nullable(String)',
            'identity_airline_iata Nullable(FixedString(2))',
            'identity_airline_icao Nullable(FixedString(3))',
            'model_type_iata Nullable(String)',
            'model_type_iata_code_short FixedString(3)',
            'model_type_iata_code_long FixedString(4)',
            'model_engine_count Nullable(UInt8)',
            "model_engine_type Enum('JET', 'TURBOFAN', 'TURBOPROP', 'UNKNOWN')",
            'model_model_code Nullable(String)',
            'model_line_number Nullable(String)',
            'model_serial_number Nullable(String)',
            'model_family Nullable(String)',
            'model_sub_family Nullable(String)',
            'model_series Nullable(String)',
            "model_classification Enum('UNKNOWN')",
            "lifecycle_date_delivery FixedString(20)",
            "lifecycle_date_first_flight FixedString(20)",
            "lifecycle_date_registration FixedString(20)",
            "lifecycle_date_rollout FixedString(20)",
            'lifecycle_age Nullable(Int16)',
            "status Enum('ACTIVE', 'INACTIVE', 'UNKNOWN')",
        ]

        # Create table
        aircraft = self._collect_aircraft()
        logger.info(f'Table "{self.TABLE_NAME}" does not exist, creating...')
        await self._cache.set(aircraft)
        await self._database.create_table(self.TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          'ORDER BY (identity_icao24, identity_registration)',
                                          'SETTINGS index_granularity=1024')
        await self._insert_aircraft(aircraft)
    
    async def _load_from_database(self) -> None:
        """Load cache from database"""
        # Get rows from database
        query = f'SELECT * FROM {self.TABLE_NAME}'
        rows = await self._database.sql_query(query)
        logger.info(f'Retrieved {len(rows)} aircraft from server')

        # Parse into aircraft list
        field_names = Aircraft.flat_keys()
        aircraft = [Aircraft.unflatten(dict(zip(field_names, row))) for row in rows]
        await self._cache.set(aircraft)
    
    def _collect_aircraft(self) -> list[Aircraft]:
        """Collect aircraft database from Aviation Edge API

        Returns:
            list[Aircraft]: aircraft database
        """
        api = AviationEdgeAPI(settings.aviation_edge_api_key)
        aircraft = api.get_aircraft_database()
        logger.debug(f'Retrieved {len(aircraft)} aircraft.')
        return aircraft
    
    async def _insert_aircraft(self, aircraft: list[Aircraft]) -> None:
        """Insert aircraft into database

        Args:
            aircraft (list[Aircraft]): list of aircraft to insert
        """
        logger.debug(f'Inserting {len(aircraft)} aircraft into database...')
        rows = [list(ac.flatten().values()) for ac in aircraft]
        with open('var\\testrows.txt', 'w', encoding='utf-8') as file:
            file.writelines([str(row[18]) + '\n' for row in rows])
        columns = list(aircraft[0].flatten().keys())
        logger.debug(f'Inserting {len(aircraft)} aircraft into database')
        await self._database.insert(self.TABLE_NAME, rows, columns)
    
    async def get_aircraft(self, registration: str) -> Aircraft | None:
        """Get an aircraft by registration

        Args:
            registration (str): aircraft registration (tail number)

        Returns:
            Aircraft: aircraft with specified registration
        """
        aircraft = await self._cache.get()
        for ac in aircraft:
            ac_reg = ac.identity.registration
            if ac_reg is None:
                continue
            if ac_reg.replace('-', '').lower() == registration.replace('-', '').lower():
                return ac
        raise KeyError(f'No aircraft with registration "{registration}"')

    async def search_aircraft(self, fields: dict[str, Any], limit: int = 0) -> list[Aircraft]:
        """Search for aircraft matching specific information

        Args:
            fields (dict[str, Any]): field-value pairs to search for
            limit (int, optional): maximum number of aircraft to retrieve (0=all). Defaults to 0.

        Returns:
            list[Aircraft]: list of aircraft matching fields
        """
        aircraft = await self._cache.get()
        return search_object_list(aircraft, fields, limit)
