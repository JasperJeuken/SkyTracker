"""External API service"""
import time
import asyncio
from typing import Type

from skytracker.storage import Storage
from skytracker.models.state import State, StateGeography
from skytracker.services.api import OpenskyNetworkAPI, AviationEdgeAPI
from skytracker.models.api import API
from skytracker.utils import logger
from skytracker.settings import settings


async def collection_service(storage: Storage, repeat: int = 90) -> None:
    """Service which periodically collects aircraft states from an external API

    Args:
        storage (Storage): database storage instance
        repeat (int, optional): period with which to collect states (sec). Defaults to 90 sec.
    """
    logger.debug('Starting collection service...')
    
    # Start APIs
    api_types: list[Type[API]] = [OpenskyNetworkAPI, AviationEdgeAPI]
    apis: list[API] = []
    for api_type in api_types:
        try:
            api = api_type(settings)
        except Exception as exc:
            logger.error(f'Startup error ({api_type.__name__}): "{exc}"')
            api = None
        finally:
            apis.append(api)
    
    # Start collection loop
    running = True
    while running:
        start_time = time.time()

        # Collect states from all APIs
        all_states = []
        for api in apis:
            if api is None:
                all_states.append([])
                continue
            try:
                states = api.get_states()
            except Exception as exc:
                logger.error(f'Collection error ({type(api).__name__}): "{exc}"')
                states = []
            finally:
                all_states.append(states)
        
        # Combine states and write to database
        try:
            states = merge_states(*all_states)
            await storage['state'].insert_states(states)
            logger.info(f'Inserted {len(states)} aircraft states into database.')
        except Exception as exc:
            logger.error(f'Database insertion error: "{exc}"')

        # Repeat
        elapsed_time = time.time() - start_time
        await asyncio.sleep(max(0, repeat - elapsed_time))


def merge_states(states_opensky_network: list[State],
                 states_aviation_edge: list[State]) -> list[State]:
    """Merge states from different sources

    Aviation Edge API provides more details on the flight and aircraft, but only refreshes geography
    information about every 5 minutes. OpenSky Network API provides less details, but does update 
    the geography information each call. Aviation Edge API geography information is replaced by 
    OpenSky Network API geography information where matches are found by ICAO 24-bit address.

    Args:
        states_opensky_network (list[State]): states from OpenSky Network API
        states_aviation_edge (list[State]): states from Aviation Edge API

    Returns:
        list[State]: merged states
    """
    # Get geography data by ICAO 24-bit address
    geographies: dict[str, StateGeography] = {}
    for state in states_opensky_network:
        if state.aircraft.icao24 is not None:
            geographies[state.aircraft.icao24] = state.geography

    # Look up ICAO 24-bit address
    updates = {'position': 0, 'baro_altitude': 0, 'geo_altitude': 0, 'heading': 0,
               'speed_horizontal': 0, 'speed_vertical': 0}
    for state in states_aviation_edge:
        geography: StateGeography | None = geographies.get(state.aircraft.icao24, None)
        if geography is None:
            continue

        # Replace if data is available
        if geography.position != (0.0, 0.0):
            state.geography.position = geography.position
            updates['position'] += 1
        if geography.baro_altitude is not None:
            state.geography.baro_altitude = geography.baro_altitude
            updates['baro_altitude'] += 1
        if geography.geo_altitude is not None:
            state.geography.geo_altitude = geography.geo_altitude
            updates['geo_altitude'] += 1
        if geography.heading is not None:
            state.geography.heading = geography.heading
            updates['heading'] += 1
        if geography.speed_horizontal is not None:
            state.geography.speed_horizontal = geography.speed_horizontal
            updates['speed_horizontal'] += 1
        if geography.speed_vertical is not None:
            state.geography.speed_vertical = geography.speed_vertical
            updates['speed_vertical'] += 1
        state.geography.is_on_ground = geography.is_on_ground

    logger.info(f'Merged state info: {updates}')
    return states_aviation_edge
