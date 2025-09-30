"""Aircraft endpoint services"""
from urllib.parse import quote
from fastapi import HTTPException

from skytracker.models.aircraft import AircraftPhoto, AircraftDetails
from skytracker.services.browser import WebBrowser
from skytracker.storage import Storage
from skytracker.utils import logger


async def get_aircraft_details(storage: Storage, callsign: str) -> AircraftDetails:
    """Get the details of a specific aircraft

    Args:
        storage (Storage): backend storage manager
        callsign (str): aircraft callsign (ICAO)

    Returns:
        AircraftDetails: aircraft details
    """
    try:
        state = await storage['state'].get_last_state(callsign)
        if state is None:
            logger.error(f'No aircraft found with callsign "{callsign}"')
            raise HTTPException(status_code=400,
                                detail=f'Could not find aircraft with callsign "{callsign}"')
        return AircraftDetails(**state.model_dump() | {'aircraft_country': ''})
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
