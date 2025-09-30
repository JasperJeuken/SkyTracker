"""Aircraft API endpoints"""
from fastapi import APIRouter, Path, Query, Depends, HTTPException

from skytracker.models.aircraft import AircraftDetails, AircraftPhoto
from skytracker.dependencies import get_storage, get_browser
from skytracker.storage import Storage
from skytracker.services.browser import WebBrowser
from skytracker.utils import logger, log_and_raise
from skytracker.utils.conversions import country_name_to_country_code
from skytracker.services.aircraft import get_aircraft_photos, get_aircraft_details


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


@router.get('/{callsign}/photos', response_model=list[AircraftPhoto])
async def api_get_photos(storage: Storage = Depends(get_storage),
                         browser: WebBrowser = Depends(get_browser),
                         callsign: str = Path(),
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


@router.get('/{callsign}', response_model=AircraftDetails)
async def api_get_details(storage: Storage = Depends(get_storage),
                          callsign: str = Path()) -> AircraftDetails:
    """Get the details of a specific aircraft

    Args:
        storage (Storage): database storage instance
        callsign (str): aircraft callsign (ICAO)

    Returns:
        AircraftDetails: details of the chosen aircraft
    """
    logger.info(f'API (get_details): callsign={callsign}')
    return await get_aircraft_details(storage, callsign)
