"""Airline API endpoints"""
from typing import Literal

from fastapi import APIRouter, Query, Path, Depends

from skytracker.models.airline import Airline
from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.utils import logger, Errors, Regex
from skytracker.utils.geographic import country_code_validator
from skytracker.services.airline import get_airline, search_airline


router = APIRouter(prefix='/airline', tags=['airline'])


@router.get('/{icao}',
            response_model=Airline,
            summary='Get details of specific airline',
            description='Use the ICAO code of an airline to retrieve details of that airline',
            responses=Errors.not_found)
async def api_get_airline(
        storage: Storage = Depends(get_storage),
        icao: str = Path(regex=Regex.code_3,
                         title='Airline ICAO code',
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
    return await get_airline(storage, icao)


@router.get('',
            response_model=list[Airline],
            summary='Search for an airline',
            description='Search for details of an aircraft given specific information')
async def api_search_airline(
        storage: Storage = Depends(get_storage),
        icao: str | None = Query(None, regex=Regex.code_3_wildcard,
                                 title='Airline ICAO code',
                                 description='Airline ICAO code (3 characters)',
                                 example='AAL'),
        iata: str | None = Query(None, regex=Regex.code_2_wildcard,
                                 title='Airline IATA code',
                                 description='Airline IATA code (2 characters)',
                                 example='AA'),
        name: str | None = Query(None,
                                 title='Airline name',
                                 description='Full airline name',
                                 example='American Airlines'),
        callsign: str | None = Query(None, regex=Regex.alphanumeric_spaces_wildcard,
                                     title='Airline callsign',
                                     description='Airline callsign',
                                     example='AMERICAN'),
        types: list[Literal['SCHEDULED', 'CHARTER', 'CARGO', 'VIRTUAL', 'LEISURE', 'GOVERNMENT',
                            'PRIVATE', 'MANUFACTURER', 'SUPPLIER', 'DIVISION'] | None] = 
                            Query(None,
                                  title='Airline type (one or more)',
                                  description='Airline type (one or more can be specified)',
                                  example=['SCHEDULED', 'CARGO']),
        country: str | None = Depends(country_code_validator),
        hub: str | None = Query(None, regex=Regex.code_3_wildcard,
                                title='Hub airport ICAO code',
                                description='Hub airport ICAO code (3 characters)',
                                example='LAX'),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Maximum number of airlines to retrieve (0=all)',
                           example=10)
    ) -> list[Airline]:
    """Search for an airline based on given information

    Args:
        storage (Storage): backend storage manager
        icao (str | None): airline ICAO code (3 characters)
        iata (str | None): airline IATA code (2 characters)
        name (str | None): full airline name
        callsign (str | None): airline callsign
        types (list[Literal['SCHEDULED', 'CHARTER', 'CARGO', 'VIRTUAL', 'LEISURE', 'GOVERNMENT',
                            'PRIVATE', 'MANUFACTURER', 'SUPPLIER', 'DIVISION'] | None]):
            airline type (one or more can be specified)
        country (str | None): ISO 3166-1 A-2 country code (2 characters)
        hub (str | None): hub airport ICAO code (3 characters)
        limit (int, optional): maximum number of airlines to retrieve (0=all). Defaults to 0 (all).

    Returns:
        list[Airline]: airline search results
    """
    logger.info(f'API (search_airline): icao={icao} iata={iata} name={name} ' + \
                f'callsign={callsign} types={types} country={country} hub={hub} limit={limit}')
    return await search_airline(storage, limit, icao, iata, name, callsign, types, country, hub)
