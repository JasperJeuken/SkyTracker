"""Airline endpoint services"""
from typing import Literal

from skytracker.models.airline import Airline, AirlineType
from skytracker.storage import Storage
from skytracker.utils import log_and_raise_http
from skytracker.utils.analysis import decode


async def get_airline(storage: Storage, icao: str) -> Airline:
    """Get the details of a specific airline

    Args:
        storage (Storage): backend storage manager
        icao (str): airline ICAO code

    Returns:
        Airline: airline details
    """
    try:
        return await storage['airline'].get_airline(icao)
    except KeyError as err:
        log_and_raise_http(f'Could not find airline with ICAO code "{icao}"', 404, err)


async def search_airline(storage: Storage, limit: int = 0, icao: str | None = None,
                         iata: str | None = None, name: str | None = None,
                         callsign: str | None = None,
                         types: list[Literal['SCHEDULED', 'CHARTER', 'CARGO', 'VIRTUAL', 'LEISURE',
                                             'GOVERNMENT', 'PRIVATE', 'MANUFACTURER', 'SUPPLIER',
                                             'DIVISION'] | None] = None,
                         country: str | None = None, hub: str | None = None) -> list[Airline]:
    """Search for an airline given specific information

    Args:
        storage (Storage): backend storage manager
        limit (int, optional): maximum number of airlines to retrieve (0=all). Defaults to 0 (all).
        icao (str | None, optional): airline ICAO code. Defaults to None.
        iata (str | None, optional): airline IATA code. Defaults to None.
        name (str | None, optional): full airline name. Defaults to None.
        types (list[Literal['SCHEDULED', 'CHARTER', 'CARGO', 'VIRTUAL', 'LEISURE', 'GOVERNMENT',
                            'PRIVATE', 'MANUFACTURER', 'SUPPLIER', 'DIVISION'] | None], optional):
            airline type (one or more can be specified). Defaults to None.
        callsign (str | None, optional): airline callsign. Defaults to None.
        country (str | None, optional): ISO 3166-1 A-2 country code. Defaults to None
        hub (str | None): hub airport ICAO code (3 characters)

    Returns:
        list[Airline]: airline search results
    """
    # Assemble search fields
    types = [AirlineType.from_string(al_type) for al_type in types if al_type is not None] \
        if types is not None else None
    keys = ('icao', 'iata', 'name', 'callsign', 'types', 'country_iso2', 'hub_icao')
    values = (decode(icao), decode(iata), decode(name), decode(callsign), types, country,
              decode(hub))
    fields = {key: value for key, value in zip(keys, values) if value is not None}
    if not len(fields):
        log_and_raise_http(f'At least one parameter must be specified', 400)

    # Return results
    return await storage['airline'].search_airline(fields, limit)
