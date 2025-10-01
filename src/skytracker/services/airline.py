"""Airline endpoint services"""
from fastapi import HTTPException

from skytracker.models.airline import Airline
from skytracker.storage import Storage
from skytracker.utils import logger


async def get_specific_airline(storage: Storage, iata: str | None = None,
                               icao: str | None = None) -> Airline:
    """Get the details of a specific airline

    Args:
        storage (Storage): backend storage manager
        iata (str): airline IATA code
        icao (str): airline ICAO code

    Returns:
        Airline: airline details
    """
    if iata is None and icao is None:
        logger.error('Neither IATA or ICAO code specified')
        raise HTTPException(status_code=400, detail='IATA or ICAO code must be specified')
    try:
        airline = await storage['airline'].get_airline(iata, icao)
        if airline is None:
            logger.error(f'Airline not found ({iata}, {icao})')
            raise HTTPException(status_code=400, detail=f'Airline not found')
        return airline
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err
