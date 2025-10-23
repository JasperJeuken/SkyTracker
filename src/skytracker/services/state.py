"""State endpoint services"""
from typing import Literal

from fastapi import HTTPException

from skytracker.storage import Storage
from skytracker.models.state import MapState, State, StateStatus
from skytracker.utils import logger, log_and_raise_http
from skytracker.utils.analysis import decode


async def get_nearby(storage: Storage, lat: float, lon: float,
                     radius: float, limit: int) -> list[MapState]:
    """Get list of aircraft states close to a specified location

    Args:
        storage (Storage): backend storage manager
        lat (float): latitude [deg]
        lon (float): longitude [deg]
        radius (float): distance from point to search in [km]
        limit (int): maximum number of states to get (0=all)

    Returns:
        list[MapState]: list of aircraft near specified point
    """
    try:
        states = await storage['state'].get_nearby(lat, lon, radius, limit)
        return [MapState(time=state.time,
                         callsign=state.flight.icao,
                         position=state.geography.position,
                         heading=state.geography.heading,
                         model=state.aircraft.iata,
                         altitude=state.geography.baro_altitude,
                         velocity=state.geography.speed_horizontal) for state in states]
    except ValueError as err:
        log_and_raise_http(f'{err}', 400, err)


async def get_track(storage: Storage, callsign: str, duration: str, limit: int) -> list[MapState]:
    """Get the track history of a specific aircraft

    Args:
        storage (Storage): backend storage manager
        callsign (str): aircraft callsign (ICAO)
        duration (str): duration of track (i.e. "5h20m" or "10m20s")
        limit (int): maximum number of states to get (0=all)

    Returns:
        list[MapState]: list of aircraft track states
    """
    try:
        states = await storage['state'].get_track(callsign, duration, limit)
        return [MapState(time=state.time,
                         callsign=state.flight.icao,
                         position=state.geography.position,
                         heading=state.geography.heading,
                         model=state.aircraft.iata,
                         altitude=state.geography.baro_altitude,
                         velocity=state.geography.speed_horizontal) for state in states]
    except ValueError as err:
        log_and_raise_http(f'Request failed ({err})', 400, err)


async def get_latest(storage: Storage, callsign: str) -> State:
    """Get the latest state of a specific aircraft

    Args:
        storage (Storage): backend storage manager
        callsign (str): aircraft callsign (ICAO)

    Returns:
        State: last known aircraft state
    """
    try:
        state = await storage['state'].get_last_state(callsign)
        if state is None:
            log_and_raise_http(f'State not found ({callsign})', 404)
        return state
    except ValueError as err:
        log_and_raise_http(f'{err}', 400, err)


async def get_area(storage: Storage, south: float, north: float,
                  west: float, east: float, limit: int) -> list[MapState]:
    """Get the latest batch of aircraft states within a specific area

    Args:
        storage (Storage): backend storage manager
        south (float): minimum latitude [deg]
        north (float): maximum latitude [deg]
        west (float): minimum longitude [deg]
        east (float): maximum longitude [deg]
        limit (int): maximum number of states to return (0=all)

    Returns:
        list[MapState]: list of aircraft map states
    """
    try:
        return await storage['state'].get_latest_batch_map(limit, south, north, west, east)
    except ValueError as err:
        log_and_raise_http(f'{err}', 400, err)


async def search_state(storage: Storage, limit: int = 0,
                       callsign: str | None = None,
                       status: Literal['UNKNOWN', 'STARTED', 'LANDED', 'EN_ROUTE'] | None = None,
                       model: str | None = None, registration: str | None = None,
                       airline: str | None = None, arrival: str | None = None,
                       departure: str | None = None, on_ground: bool | None = None,
                       squawk: str | None = None) -> list[State]:
    """Search for a state given specific information

    Args:
        storage (Storage): backend storage manager
        limit (int, optional): maximum number of states to retrieve (0=all). Defaults to 0 (all).
        callsign (str | None, optional): aircraft callsign (ICAO). Defaults to None.
        status (Literal['UNKNOWN', 'STARTED', 'LANDED', 'EN_ROUTE'] | None, optional):
            aircraft status. Defaults to None.
        model (str | None, optional): aircraft model IATA code (4 characters). Defaults to None.
        registration (str | None, optional): aircraft registration (tail number). Defaults to None.
        airline (str | None, optional): airline IATA code (2 characters). Defaults to None.
        arrival (str | None, optional): arrival airport IATA code (3 characters). Defaults to None.
        departure (str | None, optional):
            departure airport IATA code (3 characters). Defaults to None.
        on_ground (bool | None, optional): whether aircraft is on ground. Defaults to None.
        squawk (str | None, optional): transponder squawk code. Defaults to None.

    Returns:
        list[State]: state search results
    """
    # Assemble search fields
    status = StateStatus.from_string(status) if status is not None else None
    keys = ('flight.icao', 'status', 'aircraft.iata', 'aircraft.registration', 'airline.iata',
            'airport.arrival_iata', 'airport.departure_iata', 'geography.is_on_ground',
            'transponder.squawk')
    values = (decode(callsign), status, decode(model), decode(registration),
              decode(airline), decode(arrival), decode(departure), on_ground, decode(squawk))
    fields = {key: value for key, value in zip(keys, values) if value is not None}
    if not len(fields):
        log_and_raise_http(f'At least one parameter must be specified', 400)
    
    # Return results
    return await storage['state'].search_state(fields, limit)
