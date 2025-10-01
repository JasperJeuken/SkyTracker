"""Airport endpoint services"""
from fastapi import HTTPException

from skytracker.models.airport import Airport
from skytracker.storage import Storage
from skytracker.utils import logger


async def get_specific_airport(storage: Storage, iata: str) -> Airport:
    """Get the details of a specific airport

    Args:
        storage (Storage): backend storage manager
        iata (str): airport IATA code

    Returns:
        Airoprt: airport details
    """
    try:
        airport = await storage['airport'].get_airport(iata)
        if airport is None:
            logger.error(f'Airport not found ({iata})')
            raise HTTPException(status_code=400, detail=f'Airport not found')
        return airport
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err
