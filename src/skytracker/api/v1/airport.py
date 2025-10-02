"""Airport API endpoints"""
from fastapi import APIRouter, Path, Query, Depends

from skytracker.models.airport import Airport
from skytracker.models.errors import Errors
from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.utils import logger
from skytracker.services.airport import get_specific_airport


router = APIRouter(prefix='/airport', tags=['airport'])


@router.get('/{iata}',
            response_model=Airport,
            summary='Get details of specific airport',
            description='Use the IATA code of an airport to retrieve details of that airport',
            responses=Errors.not_found)
async def api_get_airport(
        storage: Storage = Depends(get_storage),
        iata: str = Path(regex='^[a-zA-Z]{3}$',
                         title='Airport IATA code',
                         description='Airport IATA code (3 characters)',
                         example='AMS')
    ) -> Airport:
    """Get details of a specific airport by IATA code

    Args:
        storage (Storage): backend storage manager
        iata (str): airport IATA code (3 characters)

    Returns:
        Airport: airport details
    """
    logger.info(f'API (get_airport): iata={iata}')


@router.get('',
            response_model=list[Airport],
            summary='Search for an airport',
            description='Search for details of an airport given specific information')
async def api_search_airport(
        storage: Storage = Depends(get_storage),
        iata: str | None = Query(None, regex='^[a-zA-Z]{3}$',
                                 title='Airport IATA code',
                                 description='Airport IATA code (3 characters)',
                                 example='AMS'),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Maximum number of airports to retrieve (0=all)',
                           example=10)
    ) -> list[Airport]:
    """Search for an airport based on given information

    Args:
        storage (Storage): backend storage manager
        iata (str | None): airport IATA code (3 characters)
        limit (int, optional): maximum number of airports to retrieve (0=all). Defaults to 0 (all).

    Returns:
        list[Airport]: airport search results
    """
    logger.info(f'API (search_airport): iata={iata} limit={limit}')


# @router.get('/{iata}', response_model=Airport)
# async def get_airport(storage: Storage = Depends(get_storage),
#                       iata: str = Path()) -> Airport:
#     """Get the details of a specific airport

#     Args:
#         storage (Storage, optional): database storage instance. Defaults to Depends(get_storage).
#         iata (str, optional): airport IATA code. Defaults to Path().

#     Returns:
#         Airport: details of the chosen airport
#     """
#     logger.info(f'API (get_airport): iata={iata}')
#     return await get_specific_airport(storage, iata)
