"""Airline API endpoints"""
from fastapi import APIRouter, Query, Path, Depends

from skytracker.models.airline import Airline
from skytracker.models.errors import Errors
from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.utils import logger
from skytracker.services.airline import get_specific_airline


router = APIRouter(prefix='/airline', tags=['airline'])


@router.get('/{icao}',
            response_model=Airline,
            summary='Get details of specific airline',
            description='Use the ICAO code of an airline to retrieve details of that airline',
            responses=Errors.not_found)
async def api_get_airline(
        storage: Storage = Depends(get_storage),
        icao: str = Path(title='Airline ICAO code',
                         description='Airline ICAO code (3 characters)',
                         example='AAL')
    ) -> Airline:
    """Get details of a specific airline by ICAO code

    Args:
        storage (storage): backend storage manager
        icao (str): airline ICAO code (3 characters)

    Returns:
        Airline: airline details
    """
    logger.info(f'API (get_airline): icao={icao}')


@router.get('',
            response_model=list[Airline],
            summary='Search for an airline',
            description='Search for details of an aircraft given specific information')
async def api_search_airline(
        storage: Storage = Depends(get_storage),
        icao: str | None = Query(None,
                                 title='Airline ICAO code',
                                 description='Airline ICAO code (3 characters)',
                                 example='AAL'),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Maximum number of airlines to retrieve (0=all)',
                           example=10)
    ) -> list[Airline]:
    """Search for an airline based on given information

    Args:
        storage (Storage): backend storage manager
        icao (str | None): airline ICAO code (3 characters)
        limit (int, optional): maximum number of airlines to retrieve (0=all). Defaults to 0 (all).

    Returns:
        list[Airline]: airline search results
    """
    logger.info(f'API (search_airline): icao={icao} limit={limit}')


# @router.get('', response_model=Airline)
# async def get_airport(storage: Storage = Depends(get_storage),
#                       iata: Annotated[str | None, Query()] = None,
#                       icao: Annotated[str | None, Query()] = None) -> Airline:
#     """Get the details of a specific airline

#     Args:
#         storage (Storage, optional): database storage instance. Defaults to Depends(get_storage).
#         iata (str, optional): airline IATA code. Defaults to Path().
#         icao (str, optional): airline icao code. Defaults to Path().

#     Returns:
#         Airline: details of the chosen airline
#     """
#     logger.info(f'API (get_airline): iata={iata} icao={icao}')
#     return await get_specific_airline(storage, iata, icao)
