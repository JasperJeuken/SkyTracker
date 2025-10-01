"""Aircraft endpoint services"""
from urllib.parse import quote
from fastapi import HTTPException

from skytracker.models.aircraft import AircraftPhoto, Aircraft
from skytracker.services.browser import WebBrowser
from skytracker.storage import Storage
from skytracker.utils import logger


async def get_aircraft(storage: Storage, registration: str | None = None,
                       icao24: str | None = None, callsign: str | None = None) -> Aircraft:
    """Get the details of a specific aircraft

    Args:
        storage (Storage): backend storage manager
        registration (str | None): aircraft callsign (ICAO)
        icao24 (str | None): aircraft ICAO 24-bit address (hex)
        callsign (str | None): aircraft callsign

    Returns:
        Aircraft: aircraft details
    """
    if registration is None and icao24 is None and callsign is None:
        logger.error(f'Registration, ICAO24, nor callsign specified')
        raise HTTPException(status_code=400, detail=f'Registration, ICAO24, or callsign ' + \
                            'must be specified')
    try:
        if callsign is not None:
            state = await storage['state'].get_last_state(callsign)
            if state is not None:
                registration, icao24 = state.aircraft_registration, state.aircraft_icao24
        aircraft = await storage['aircraft'].get_aircraft(registration, icao24)
        if aircraft is None:
            logger.error(f'Aircraft not found ({registration})')
            raise HTTPException(status_code=400, detail=f'Aircraft not found')
        return aircraft
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err


async def get_aircraft_photos(storage: Storage, browser: WebBrowser,
                              callsign: str, limit: int = 5) -> list[AircraftPhoto]:
    """Fetch aircraft photos from planespotters.net for a given ICAO 24-bit address

    Args:
        storage (Storage): database storage instance
        browser (WebBrowser): web browser instance
        callsign (str): aircraft ICAO 24-bit address
        limit (int, optional): maximum number of results to return (0=all). Defaults to 0 (all).

    Returns:
        list[AircraftPhoto]: aircraft photos
    """
    # Get aircraft registration
    try:
        state = await storage['state'].get_last_state(callsign)
        if state is None:
            logger.error(f'Could not get last state (callsign={callsign})')
            raise HTTPException(status_code=400,
                                detail=f'Could not get last state (callsign={callsign})')
        registration = state.aircraft_registration
        if not registration or registration == 'XXB':
            logger.error(f'Aircraft has no known registration (callsign={callsign})')
            raise HTTPException(status_code=400,
                                detail=f'Aircraft has no known registration (callsign={callsign})')
    except ValueError as err:
        logger.error(f'Could not get registration (callsign={callsign})')
        raise HTTPException(status_code=400,
                            detail=f'Could not get registration (callsign={callsign})')
    
    # Search for images
    search_url = f'https://www.bing.com/images/search?q=aircraft+{quote(registration)}'
    trusted_domains = ['planespotters.net', 'flightradar24.com']
    urls = await browser.get_images_from_page(search_url, limit=limit,
                                              timeout=5000, trusted_domains=trusted_domains)
    return [AircraftPhoto(image_url=url['image'], detail_url=url['detail']) for url in urls]
