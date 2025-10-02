"""Aircraft API endpoints"""
from typing import Literal

from fastapi import APIRouter, Query, Path, Depends

from skytracker.models.aircraft import AircraftPhoto, Aircraft
from skytracker.dependencies import get_storage, get_browser
from skytracker.storage import Storage
from skytracker.services.browser import WebBrowser
from skytracker.utils import logger, Errors, Regex
from skytracker.services.aircraft import get_aircraft_photos, get_aircraft, search_aircraft


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


@router.get('/{registration}',
            response_model=Aircraft,
            summary='Get details of specific aircraft',
            description='Use the registration of an aircraft to retrieve details of that aircraft',
            responses=Errors.not_found)
async def api_get_aircraft(
        storage: Storage = Depends(get_storage),
        registration: str = Path(regex=Regex.aircraft_registration,
                                 title='Aircraft registration',
                                 description='Aircraft registration (tail number)',
                                 example='AB-CDE')
    ) -> Aircraft:
    """Get details of a specific aircraft by registration

    Args:
        storage (Storage): backend storage manager
        registration (str): aircraft registration (tail number)

    Returns:
        Aircraft: aircraft details
    """
    logger.info(f'API (get_aircraft): registration={registration}')
    return await get_aircraft(storage, registration)


@router.get('/{registration}/photos',
            response_model=list[AircraftPhoto],
            summary='Get photos of a specific aircraft',
            description='Use the registration of an aircraft to retrieve images of that aircraft',
            responses=Errors.not_found)
async def api_get_photos(
        browser: WebBrowser = Depends(get_browser),
        registration: str = Path(regex=Regex.aircraft_registration,
                                 title='Aircraft registration',
                                 description='Aircraft registration (tail number)',
                                 example='AB-CDE'),
        limit: int = Query(5, ge=1, le=5,
                           title='Limit',
                           description='Maximum number of images to retrieve (max. 5)',
                           example=5)
    ) -> list[AircraftPhoto]:
    """Get photos of a specific aircraft by registration

    Args:
        browser (WebBrowser): web browser
        registration (str): aircraft registration (tail number)
        limit (int, optional): maximum number of images to retrieve (max. 5). Defaults to 5.

    Returns:
        list[AircraftPhoto]: list of aircraft photos
    """
    logger.info(f'API (get_photos): registration={registration} limit={limit}')
    return await get_aircraft_photos(browser, registration, limit)


@router.get('',
            response_model=list[Aircraft],
            summary='Search for an aircraft',
            description='Search for details of an aircraft given specific information',
            responses=Errors.bad_request)
async def api_search_aircraft(
        storage: Storage = Depends(get_storage),
        registration: str | None = Query(None, regex=Regex.aircraft_registration_wildcard,
                                         title='Aircraft registration',
                                         description='Aircraft registration (tail number)',
                                         example='AB-CDE'),
        icao24: str | None = Query(None, regex=Regex.aircraft_icao24_wildcard,
                                   title='Aircraft ICAO 24-bit address',
                                   description='Aircraft ICAO 24-bit address (hex, 6 characters)',
                                   example='1A2B3C'),
        callsign: str | None = Query(None, regex=Regex.aircraft_callsign_wildcard,
                                     title='Aircraft callsign',
                                     description='Aircraft callsign (ICAO)',
                                     example='ABC123D'),
        model: str | None = Query(None, regex=Regex.aircraft_model_wildcard,
                                  title='Aircraft model IATA code',
                                  description='Aircraft model IATA code (4 characters)',
                                  example='B737'),
        airline: str | None = Query(None, regex=Regex.code_2_wildcard,
                                    title='Airline IATA code',
                                    description='Airline IATA code (2 characters)',
                                    example='AA'),
        engine_count: int | None = Query(None, ge=2, le=4,
                                         title='Number of engines',
                                         description='Number of engines on aircraft (2, 3, or 4)',
                                         example=4),
        engine_type: Literal['JET', 'UNKNOWN', 'TURBOPROP', 'TURBOFAN'] | None = 
                             Query(None,
                                 title='Type of engines',
                                 description='Type of engines on aircraft ' + \
                                             '(JET, TURBOPROP, TURBOFAN, or UNKNOWN)',
                                 example='JET'),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Maximum number of aircraft to retrieve (0=all)',
                           example=10)
    ) -> list[Aircraft]:
    """Search for an aircraft based on given information

    Args:
        storage (Storage): backend storage manager
        registration (str | None): aircraft registration (tail number)
        icao24 (str | None): aircraft ICAO 24-bit address (hex, 6 characters)
        callsign (str | None): aircraft callsign (ICAO)
        model (str | None): aircraft model IATA code (4 characters)
        airline (str | None): airline IATA code (2 characters)
        engine_count (int | None): number of engines on aircraft (2, 3, or 4)
        engine_type (Literal['JET', 'UNKNOWN', 'TURBOPROP', 'TURBOFAN'] | None)
            type of engines on aircaft (JET, TURBOPROP, TURBOFAN, or UNKNOWN)
        limit (int, optional): maximum number of aircraft to retrieve (0=all). Defaults to 0 (all).

    Returns:
        list[AircraftState]: aircraft search results
    """
    logger.info(f'API (search_aircraft): registration={registration} icao24={icao24} ' + \
                f'callsign={callsign} model={model} airline={airline} ' + 
                f'engine_count={engine_count} engine_type={engine_type} limit={limit}')
    return await search_aircraft(storage, limit, registration, icao24, callsign, model,
                                 airline, engine_count, engine_type)
