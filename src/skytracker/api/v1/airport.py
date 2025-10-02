"""Airport API endpoints"""
from fastapi import APIRouter, Path, Query, Depends

from skytracker.models.airport import Airport
from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.utils import logger, Errors, Regex
from skytracker.utils.geographic import country_code_validator
from skytracker.services.airport import get_airport, search_airport


router = APIRouter(prefix='/airport', tags=['airport'])


@router.get('/{iata}',
            response_model=Airport,
            summary='Get details of specific airport',
            description='Use the IATA code of an airport to retrieve details of that airport',
            responses=Errors.not_found)
async def api_get_airport(
        storage: Storage = Depends(get_storage),
        iata: str = Path(regex=Regex.code_3,
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
    return await get_airport(storage, iata)


@router.get('',
            response_model=list[Airport],
            summary='Search for an airport',
            description='Search for details of an airport given specific information')
async def api_search_airport(
        storage: Storage = Depends(get_storage),
        iata: str | None = Query(None, regex=Regex.code_3_wildcard,
                                 title='Airport IATA code',
                                 description='Airport IATA code (3 characters)',
                                 example='AMS'),
        icao: str | None = Query(None, regex=Regex.code_4_wildcard,
                                 title='Airport ICAO code',
                                 description='Airport ICAO code (4 characters)',
                                 example='EHAM'),
        name: str | None = Query(None,
                                 title='Airport name',
                                 description='Airport name',
                                 example='Schiphol'),
        city: str | None = Query(None,
                                 title='City IATA code',
                                 description='City IATA code (3 characters)',
                                 example='AMS'),
        country: str | None = Depends(country_code_validator),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Maximum number of airports to retrieve (0=all)',
                           example=10)
    ) -> list[Airport]:
    """Search for an airport based on given information

    Args:
        storage (Storage): backend storage manager
        iata (str | None): airport IATA code (3 characters)
        icao (str | None): airport ICAO code (4 characters)
        name (str | None): airport name
        city (str | None): city IATA code (3 characters)
        country (str | None): ISO 3166-1 A-2 country code (2 characters)
        limit (int, optional): maximum number of airports to retrieve (0=all). Defaults to 0 (all).

    Returns:
        list[Airport]: airport search results
    """
    logger.info(f'API (search_airport): iata={iata} icao={icao} name={name} city={city} ' + \
                f'country={country} limit={limit}')
    return await search_airport(storage, limit, iata, icao, name, city, country)
