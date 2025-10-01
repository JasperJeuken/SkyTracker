"""Airline API endpoints"""
from typing import Annotated

from fastapi import APIRouter, Query, Depends

from skytracker.models.airline import Airline
from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.utils import logger
from skytracker.services.airline import get_specific_airline


router = APIRouter(prefix='/airline', tags=['airline'])


@router.get('', response_model=Airline)
async def get_airport(storage: Storage = Depends(get_storage),
                      iata: Annotated[str | None, Query()] = None,
                      icao: Annotated[str | None, Query()] = None) -> Airline:
    """Get the details of a specific airline

    Args:
        storage (Storage, optional): database storage instance. Defaults to Depends(get_storage).
        iata (str, optional): airline IATA code. Defaults to Path().
        icao (str, optional): airline icao code. Defaults to Path().

    Returns:
        Airline: details of the chosen airline
    """
    logger.info(f'API (get_airline): iata={iata} icao={icao}')
    return await get_specific_airline(storage, iata, icao)
