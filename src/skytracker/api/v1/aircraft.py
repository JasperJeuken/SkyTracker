"""Aircraft API endpoints"""
from typing import Annotated

from fastapi import APIRouter, Query, Depends

from skytracker.models.aircraft import AircraftPhoto, Aircraft
from skytracker.dependencies import get_storage, get_browser
from skytracker.storage import Storage
from skytracker.services.browser import WebBrowser
from skytracker.utils import logger
from skytracker.services.aircraft import get_aircraft_photos, get_aircraft


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


@router.get('/photos', response_model=list[AircraftPhoto])
async def api_get_photos(storage: Storage = Depends(get_storage),
                         browser: WebBrowser = Depends(get_browser),
                         callsign: Annotated[str | None, Query()] = None,
                         limit: int = Query(5, le=5, ge=1)) -> list[AircraftPhoto]:
    """Get photos of a specific aircraft

    Args:
        storage (Storage): database storage instance
        browser (WebBrowser): web browser instance
        callsign (str): aircraft callsign (ICAO)
        limit (int, optional): maximum number of image, max. 5. Defaults to 5.

    Returns:
        list[AircraftPhoto]: list of aircraft photos
    """
    logger.info(f'API (get_photos): callsign={callsign} limit={limit}')
    return await get_aircraft_photos(storage, browser, callsign, limit)


@router.get('', response_model=Aircraft)
async def api_get_aircraft(storage: Storage = Depends(get_storage),
                           registration: Annotated[str | None, Query()] = None,
                           icao24: Annotated[str | None, Query()] = None,
                           callsign: Annotated[str | None, Query()] = None) -> Aircraft:
    """Get the details of a specific aircraft

    Args:
        storage (Storage): database storage instance
        registration (str | None): aircraft registration
        icao24 (str | None): aircraft ICAO 24-bit address (hex)
        callsign (str | None): aircraft callsign

    Returns:
        AircraftState: details of the chosen aircraft
    """
    logger.info(f'API (get_aircraft): registration={registration} icao24={icao24} ' + \
                f'callsign={callsign}')
    return await get_aircraft(storage, registration, icao24, callsign)
