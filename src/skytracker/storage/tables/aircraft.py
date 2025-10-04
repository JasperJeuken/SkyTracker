"""Aircraft table manager"""
from typing import Any

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.services.api.aviation_edge import AviationEdgeAPI
from skytracker.models.aircraft import Aircraft
from skytracker.models import flatten_model, unflatten_model
from skytracker.utils import logger, log_and_raise
from skytracker.utils.analysis import search_object_list
from skytracker.settings import settings


class AircraftTableManager(TableManager[Aircraft]):
    """Async aircraft table manager"""

    TABLE_NAME = 'aircraft'
    """str: name of aircraft table"""
    TABLE_FIELDS: dict[str, str] = {
        'identity__icao24': 'FixedString(6)',
        'identity__registration': 'FixedString(10)',
        'identity__test_registration': 'Nullable(FixedString(10))',
        'identity__owner': 'Nullable(String)',
        'identity__airline_iata': 'Nullable(FixedString(2))',
        'identity__airline_icao': 'Nullable(FixedString(3))',
        'model__type_iata': 'Nullable(String)',
        'model__type_iata_code_short': 'FixedString(3)',
        'model__type_iata_code_long': 'FixedString(4)',
        'model__engine_count': 'Nullable(UInt8)',
        'model__engine_type': "Enum('JET', 'TURBOFAN', 'TURBOPROP', 'UNKNOWN')",
        'model__model_code': 'Nullable(String)',
        'model__line_number': 'Nullable(String)',
        'model__serial_number': 'Nullable(String)',
        'model__family': 'Nullable(String)',
        'model__sub_family': 'Nullable(String)',
        'model__series': 'Nullable(String)',
        'model__classification': "Enum('UNKNOWN')",
        'lifecycle__date_delivery': 'FixedString(20)',
        'lifecycle__date_first_flight': 'FixedString(20)',
        'lifecycle__date_registration': 'FixedString(20)',
        'lifecycle__date_rollout': 'FixedString(20)',
        'lifecycle__age': 'Nullable(Int16)',
        'status': "Enum('ACTIVE', 'INACTIVE', 'UNKNOWN')",
    }
    """dict[str, str]: column_name - column_type pairs"""
    TABLE_KEYS: tuple[str] = ('identity__icao24', 'identity__registration')
    """tuple[str]: keys used in database table"""

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

        # Create table
        fields = [f'{name} {data_type}' for name, data_type in self.TABLE_FIELDS.items()] 
        aircraft = self._collect_aircraft()
        logger.info(f'Table "{self.TABLE_NAME}" does not exist, creating...')
        await self._cache.set(aircraft)
        await self._database.create_table(self.TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          f'ORDER BY ({", ".join(self.TABLE_KEYS)})',
                                          'SETTINGS index_granularity=1024')
        await self._insert_aircraft(aircraft)
    
    async def _load_from_database(self) -> None:
        """Load cache from database"""
        # Get rows from database
        query = f'SELECT * FROM {self.TABLE_NAME}'
        rows = await self._database.sql_query(query)
        logger.info(f'Retrieved {len(rows)} aircraft from server')

        # Parse into aircraft list
        aircraft = [unflatten_model(dict(zip(self.TABLE_FIELDS.keys(), row)),
                                    Aircraft) for row in rows]
        for ac in aircraft:
            if ac.identity.icao24 == '':
                ac.identity.icao24 = None
            if ac.identity.registration == '':
                ac.identity.registration = None
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

        # Get columns and values (set keys to empty string if None)
        flattened = [flatten_model(ac) for ac in aircraft]
        for flat in flattened:
            if flat['identity__icao24'] is None:
                flat['identity__icao24'] = ''
            if flat['identity__registration'] is None:
                flat['identity__registration'] = ''
        rows = [list(flat.values()) for flat in flattened]
        columns = list(flattened[0].keys())

        # Insert into table
        logger.debug(f'Inserting {len(aircraft)} aircraft into database')
        await self._database.insert(self.TABLE_NAME, rows, columns)
    
    async def get_aircraft(self, registration: str) -> Aircraft:
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
        log_and_raise(KeyError, f'No aircraft with registration {registration}')

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
