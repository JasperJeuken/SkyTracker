"""Airport API endpoints"""
from fastapi import APIRouter, Path, Depends

from skytracker.models.airport import Airport
from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.utils import logger
from skytracker.services.airport import get_specific_airport


router = APIRouter(prefix='/airport', tags=['airport'])


@router.get('/{iata}', response_model=Airport)
async def get_airport(storage: Storage = Depends(get_storage),
                      iata: str = Path()) -> Airport:
    """Get the details of a specific airport

    Args:
        storage (Storage, optional): database storage instance. Defaults to Depends(get_storage).
        iata (str, optional): airport IATA code. Defaults to Path().

    Returns:
        Airport: details of the chosen airport
    """
    logger.info(f'API (get_airport): iata={iata}')
    return await get_specific_airport(storage, iata)
