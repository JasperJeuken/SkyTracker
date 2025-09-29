"""External API service"""
import time
import asyncio

from skytracker.storage import Storage
from skytracker.models.api import APIType, API
from skytracker.services.api import OpenskyNetworkAPI, AviationEdgeAPI
from skytracker.utils import logger, log_and_raise
from skytracker.settings import settings


async def collection_service(storage: Storage, api_type: APIType, repeat: int = 90) -> None:
    """Service which periodically collects aircraft states from an external API

    Args:
        storage (Storage): database storage instance
        api_type (APIType): external API type
        repeat (int, optional): period with which to collect states (sec). Defaults to 90 sec.
    """
    logger.debug(f'Starting collection service (api={api_type.name})')
    
    # Start API
    api: API = None
    if api_type == APIType.OPENSKY_NETWORK:
        api = OpenskyNetworkAPI(settings.opensky_network_client_id,
                                settings.opensky_network_client_secret)
    elif api_type == APIType.AVIATION_EDGE:
        api = AviationEdgeAPI(settings.aviation_edge_api_key)
    else:
        log_and_raise(ValueError, f'Unknown API type ({api_type})')
    
    # Start collection loop
    running = True
    while running:
        start_time = time.time()

        # Collect states and write to database
        try:
            states = api.get_states()
            await storage['state'].insert_states(states)
            logger.info(f'Collected {len(states)} aircraft states.')
        except Exception as exc:
            logger.error(f'Aircraft state collection error: "{exc}"')

        # Repeat
        elapsed_time = time.time() - start_time
        await asyncio.sleep(max(0, repeat - elapsed_time))
