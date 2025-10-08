"""External API service"""
import time
import asyncio

from skytracker.storage import Storage
from skytracker.models.state import State, StateGeography
from skytracker.services.api import OpenskyNetworkAPI, AviationEdgeAPI
from skytracker.utils import logger, log_and_raise
from skytracker.settings import settings


async def collection_service(storage: Storage, repeat: int = 90) -> None:
    """Service which periodically collects aircraft states from an external API

    Args:
        storage (Storage): database storage instance
        repeat (int, optional): period with which to collect states (sec). Defaults to 90 sec.
    """
    logger.debug('Starting collection service...')
    
    # Start APIs
    api_opensky_network = OpenskyNetworkAPI(settings.opensky_network_client_id,
                                            settings.opensky_network_client_secret)
    api_aviation_edge = AviationEdgeAPI(settings.aviation_edge_api_key)
    
    # Start collection loop
    running = True
    while running:
        start_time = time.time()

        # Collect states and write to database
        try:
            states_opensky_network = api_opensky_network.get_states()
            states_aviation_edge = api_aviation_edge.get_states()
            states = merge_states(states_opensky_network, states_aviation_edge)
            await storage['state'].insert_states(states)
            logger.info(f'Collected {len(states)} aircraft states.')
        except Exception as exc:
            logger.error(f'Aircraft state collection error: "{exc}"')

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
