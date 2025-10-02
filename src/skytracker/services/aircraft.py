"""Aircraft endpoint services"""
from typing import Literal

from fastapi import HTTPException

from skytracker.models.aircraft import AircraftPhoto, Aircraft, AircraftEngineType
from skytracker.services.browser import WebBrowser
from skytracker.storage import Storage
from skytracker.utils import logger, log_and_raise_http
from skytracker.utils.analysis import decode, encode


async def get_aircraft(storage: Storage, registration: str) -> Aircraft:
    """Get the details of a specific aircraft

    Args:
        storage (Storage): backend storage manager
        registration (str): aircraft registration (tail number)

    Returns:
        Aircraft: aircraft details
    """
    try:
        return await storage['aircraft'].get_aircraft(registration)
    except KeyError as err:
        log_and_raise_http(f'Could not find aircraft with registration "{registration}"', 404, err)


async def search_aircraft(storage: Storage, limit: int = 0, registration: str | None = None,
                          icao24: str | None = None, callsign: str | None = None,
                          model: str | None = None, airline: str | None = None,
                          engine_count: int | None = None,
                          engine_type: Literal['JET', 'UNKNOWN', 'TURBOFAN', 'TURBOPROP'] \
                            | None = None) -> list[Aircraft]:
    """Search for an aircraft given specific information

    Args:
        storage (Storage): backend storage manager
        limit (int, optional): maximum number of aircraft to retrieve (0=all). Defaults to 0 (all).
        registration (str | None, optional): aircraft registration (tail number). Defaults to None.
        icao24 (str | None, optional): aircraft ICAO code. Defaults to None.
        callsign (str | None, optional): aircraft callsign. Defaults to None.
        model (str | None, optional): aircraft model IATA code. Defaults to None.
        engine_count (int | None, optional): number of engines on aircraft (2, 3, or 4)
        engine_type (Literal['JET', 'UNKNOWN', 'TURBOFAN', 'TURBOPROP'] | None, optional):
            type of engines on aircaft (JET, TURBOPROP, TURBOFAN, or UNKNOWN). Defaults to None.
        airline (str | None, optional): airline IATA code. Defaults to None.

    Returns:
        list[Aircraft]: aircraft search results
    """
    # Assemble search fields
    engine_type = AircraftEngineType.from_string(engine_type) if engine_type is not None else None
    keys = ('identity.registration', 'identity.icao24', 'identity.callsign',
            'model.type_iata_code_long', 'identity.airline_iata', 'model.engine_count',
            'model.engine_type')
    values = (decode(registration), decode(icao24), decode(callsign), decode(model),
              decode(airline), engine_count, engine_type)
    fields = {key: value for key, value in zip(keys, values) if value is not None}
    if not len(fields):
        log_and_raise_http(f'At least one parameter must be specified', 400)

    # Returns results
    return await storage['aircraft'].search_aircraft(fields, limit)


async def get_aircraft_photos(browser: WebBrowser, registration: str,
                              limit: int = 5) -> list[AircraftPhoto]:
    """Fetch aircraft photos from planespotters.net for a given ICAO 24-bit address

    Args:
        browser (WebBrowser): web browser instance
        registration (str): aircraft registration (tail number)
        limit (int, optional): maximum number of results to return. Defaults to 5 images.

    Returns:
        list[AircraftPhoto]: aircraft photos
    """
    search_url = f'https://www.bing.com/images/search?q=aircraft+{encode(registration)}'
    trusted_domains = ['planespotters.net', 'flightradar24.com']
    urls = await browser.get_images_from_page(search_url, limit=limit, timeout=2000,
                                              trusted_domains=trusted_domains)
    return [AircraftPhoto(image_url=url['image'], detail_url=url['detail']) for url in urls]
