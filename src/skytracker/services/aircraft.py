"""Aircraft endpoint services"""
from urllib.parse import quote

from skytracker.models.aircraft import AircraftPhoto
from skytracker.services.browser import WebBrowser
from skytracker.storage import Storage
from skytracker.utils import logger, log_and_raise


async def get_aircraft_photos(storage: Storage, browser: WebBrowser,
                              icao24: str, limit: int = 5) -> list[AircraftPhoto]:
    """Fetch aircraft photos from planespotters.net for a given ICAO 24-bit address

    Args:
        storage (Storage): database storage instance
        browser (WebBrowser): web browser instance
        icao24 (str): aircraft ICAO 24-bit address
        limit (int, optional): maximum number of results to return (0=all). Defaults to 0 (all).

    Returns:
        list[AircraftPhoto]: aircraft photos
    """
    # Get aircraft callsign
    state = await storage['state'].get_last_state(icao24)
    if state is None:
        log_and_raise(ValueError, f'Could not get last state (icao24={icao24})')
    if state.callsign is None:
        log_and_raise(ValueError, f'Aircraft has no known callsign (icao24={icao24})')
    callsign = state.callsign.strip()
    
    # Search for images
    search_url = f'https://www.bing.com/images/search?q=aircraft+{quote(callsign)}'
    urls = await browser.get_images_from_page(search_url, limit=limit)
    return [AircraftPhoto(image_url=url['image'], detail_url=url['detail']) for url in urls]
