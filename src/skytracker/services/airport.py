"""Airport endpoint services"""
from skytracker.models.airport import Airport
from skytracker.storage import Storage
from skytracker.utils import log_and_raise_http
from skytracker.utils.analysis import decode


async def get_airport(storage: Storage, iata: str) -> Airport:
    """Get the details of a specific airport

    Args:
        storage (Storage): backend storage manager
        iata (str): airport IATA code

    Returns:
        Airport: airport details
    """
    try:
        return await storage['airport'].get_airport(iata)
    except KeyError as err:
        log_and_raise_http(f'Could not find airport with IATA code "{iata}"', 404, err)


async def search_airport(storage: Storage, limit: int = 0, iata: str | None = None,
                         icao: str | None = None, name: str | None = None, city: str | None = None,
                         country: str | None = None) -> list[Airport]:
    """Search for an airport given specific information

    Args:
        storage (Storage): backend storage manager
        limit (int, optional): maximum number of airports to retrieve (0=all). Defaults to 0 (all).
        iata (str | None, optional): airport IATA code. Defaults to None.
        icao (str | None, optional): airport ICAO code (4 characters). Defaults to None.
        name (str | None, optional): airport name. Defaults to None.
        city (str | None, optional): city IATA code (3 characters). Defaults to None.
        country (str | None, optional): ISO 3166-1 A-2 country code. Defaults to None.

    Returns:
        list[Airport]: airport search results
    """
    # Assemble search fields
    keys = ('iata', 'icao', 'name', 'city_iata', 'country_iso2')
    values = (decode(iata), decode(icao), decode(name), decode(city), country)
    fields = {key: value for key, value in zip(keys, values) if value is not None}
    if not len(fields):
        log_and_raise_http(f'At least one parameter must be specified', 400)
    
    # Return results
    return await storage['airport'].search_airport(fields, limit)
