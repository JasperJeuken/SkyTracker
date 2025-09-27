"""Aircraft API endpoints"""
from fastapi import APIRouter, Path, Query, Depends, HTTPException

from skytracker.models.aircraft import AircraftDetails, AircraftPhoto
from skytracker.dependencies import get_storage, get_browser
from skytracker.storage import Storage
from skytracker.services.browser import WebBrowser
from skytracker.utils import logger, log_and_raise
from skytracker.utils.conversions import country_name_to_country_code
from skytracker.services.aircraft import get_aircraft_photos


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


@router.get('/{icao24}/photos', response_model=list[AircraftPhoto])
async def get_photos(storage: Storage = Depends(get_storage),
                     browser: WebBrowser = Depends(get_browser),
                     icao24: str = Path(),
                     limit: int = Query(5, le=5, ge=1)) -> list[AircraftPhoto]:
    """Get photos of a specific aircraft

    Args:
        storage (Storage): database storage instance
        browser (WebBrowser): web browser instance
        icao24 (str): aircraft ICAO 24-bit address.
        limit (int, optional): maximum number of image, max. 5. Defaults to 5.

    Returns:
        list[AircraftPhoto]: list of aircraft photos
    """
    logger.info(f'Get aircraft photos: icao24={icao24}')
    try:
        photos = await get_aircraft_photos(storage, browser, icao24, limit)
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err

    logger.info(f'Get aircraft photos: {len(photos)} photos retrieved.')
    return photos


@router.get('/{icao24}', response_model=AircraftDetails)
async def get_details(storage: Storage = Depends(get_storage),
                      icao24: str = Path(min_length=6, max_length=6, regex='^[0-9A-Fa-f]{6}$')) \
        -> AircraftDetails:
    """Get the details of a specific aircraft

    Args:
        storage (Storage): database storage instance
        icao24 (str): aircraft ICAO 24-bit address.

    Returns:
        AircraftDetails: details of the chosen aircraft
    """
    # Get last aircraft state matching specified settings
    logger.info(f'Get aircraft details: icao24={icao24}')
    try:
        state = await storage['state'].get_last_state(icao24)
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err
    
    # Ensure state is found
    if state is None:
        log_and_raise(HTTPException, f'Request failed (could not find icao24={icao24})')
    
    # Convert to aircraft details model
    logger.info('Get aircraft details: 1 state retrieved.')  # TODO: use more history
    return AircraftDetails(icao24=state.icao24,
                           known_callsigns=[state.callsign.strip() 
                                            if state.callsign is not None else "N/A"],
                           origin_country=country_name_to_country_code(state.origin_country),
                           last_state=state.time, last_position=state.time_position,
                           last_contact=state.last_contact, last_latitude=state.latitude,
                           last_longitude=state.longitude, last_baro_altitude=state.baro_altitude,
                           last_geo_altitude=state.geo_altitude, last_velocity=state.velocity,
                           last_heading=state.true_track, last_vertical_rate=state.vertical_rate,
                           last_on_ground=state.on_ground, last_spi=state.spi,
                           last_squawk=state.squawk,
                           last_position_source=state.position_source.name,
                           last_category=state.category.name)
