"""State API endpoints"""
from typing import Literal

from fastapi import APIRouter, Depends, Query, Path

from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.models.state import SimpleMapState, DetailedMapState, State
from skytracker.services.state import get_nearby, get_track, get_area, get_latest, search_state
from skytracker.utils import logger, Errors, Regex


router = APIRouter(prefix='/state', tags=['state'])


@router.get('/nearby',
            response_model=list[SimpleMapState],
            summary='Get aircraft states near a specific point',
            description='Retrieve states of aircraft that are close to a specified position')
async def api_get_nearby(
        storage: Storage = Depends(get_storage),
        lat: float = Query(title='Point latitude',
                           description='Point latitude [deg]',
                           example=52.3),
        lon: float = Query(title='Point longitude',
                           description='Point longitude [deg]',
                           example=4.9),
        radius: float = Query(50, ge=1, le=1000,
                             title='Radius',
                             description='Maximum radius from point [km]',
                             example=250),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Maximum number of states to retrieve (0=all)',
                           example=20)
    ) -> list[SimpleMapState]:
    """Get list of aircraft states close to a specified location

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        lat (float): location latitude [deg].
        lon (float): location longitude [deg].
        radius (float, optional): distance from location to search in [km]. Defaults to 50.0 km.
        limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    Returns:
        list[SimpleMapState]: list of aircraft states near specific point
    """
    logger.info(f'API (get_nearby): lat={lat} lon={lon} radius={radius} limit={limit}')
    return await get_nearby(storage, lat, lon, radius, limit)


@router.get('/area',
            response_model=list[SimpleMapState],
            summary='Get aircraft states within a bounding box',
            description='Retrieve states of aircraft that are within a specified bounding box')
async def api_get_all(
        storage: Storage = Depends(get_storage),
        south: float | None = Query(None,
                                    title='Minimum latitude',
                                    description='Minimum latitude [deg]',
                                    example=51.1),
        north: float | None = Query(None,
                                    title='Maximum latitude',
                                    description='Maximum latitude [deg]',
                                    example=52.9),
        west: float | None = Query(None,
                                   title='Minimum longitude',
                                   description='Minimum longitude [deg]',
                                   example=4.1),
        east: float | None = Query(None,
                                   title='Maximum longitude',
                                   description='Maximum longitude [deg]',
                                   example=6.2),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Max. number of states to return (0=all)',
                           example=20)
    ) -> list[SimpleMapState]:
    """Get the latest batch of aircraft states

    The latest batch of aircraft states represent the most up-to-date states of aircraft around
    the world. Returned are the unique aircraft ICAO 24-bit address, latitude, longitude, and the
    aircraft heading.

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        south (float, optional): minimum latitude in decimal degrees. Defaults to None.
        north (float, optional): maximum latitude in decimal degrees. Defaults to None.
        west (float, optional): minimum longitude in decimal degrees. Defaults to None.
        east (float, optional): maximum longitude in decimal degrees. Defaults to None.
        limit (int, optional): maximum number of states to return (0=all). Defaults to 0 (all).

    Returns:
        List[SimpleMapState]: list of aircraft map states (icao24, latitude, longitude, heading)
    """
    logger.info(f'API (get_all): south={south} north={north} west={west} east={east} limit={limit}')
    return await get_area(storage, south, north, west, east, limit)


@router.get('/{callsign}/latest',
            response_model=State,
            summary='Get latest state of a specific aircraft',
            description='Use the callsign of an aircraft to retrieve ' + \
                        'the latest state of that aircraft',
            responses=Errors.not_found)
async def api_get_latest(
        storage: Storage = Depends(get_storage),
        callsign: str = Path(regex=Regex.aircraft_callsign,
                             title='Callsign',
                             description='Aircraft callsign (ICAO)',
                             example='ABC1234')
    ) -> State:
    """Get the last known state of a specific aircraft

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        callsign (str, optional): aircraft callsign (ICAO)

    Returns:
        State: last known state
    """
    logger.info(f'API (get_latest): callsign={callsign}')
    return await get_latest(storage, callsign)


@router.get('/{callsign}/history',
            response_model=list[DetailedMapState],
            summary='Get the state history of a specific aircraft',
            description='Use the callsign of an aircraft to retrieve ' + \
                        'the state history of that aircraft',
            responses=Errors.not_found)
async def api_get_track(
        storage: Storage = Depends(get_storage),
        callsign: str = Path(regex=Regex.aircraft_callsign,
                             title='Callsign',
                             description='Aircraft callsign (ICAO)',
                             example='ABC1234'),
        duration: str = Query('1d',
                              title='Duration',
                              description='Length of history to retrieve (time string)',
                              example='2h40m'),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Max. number of states to retrieve (0=all)',
                           example=20)
    ) -> list[DetailedMapState]:
    """Get the track history of a specific aircraft

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        callsign (str): aircraft callsign (ICAO)
        duration (str, optional): duration of track (i.e. "5h20m" or "10m20s"). Defaults to 1 day.
        limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    Returns:
        list[DetailedMapState]: list of aircraft track states with specified duration
    """
    logger.info(f'API (get_track): callsign={callsign} duration={duration} limit={limit}')
    return await get_track(storage, callsign, duration, limit)


@router.get('',
            response_model=list[State],
            summary='Search for a state',
            description='Search for details of a state given specific information')
async def api_search_state(
        storage: Storage = Depends(get_storage),
        callsign: str | None = Query(None, regex=Regex.aircraft_callsign_wildcard,
                                     title='Callsign',
                                     description='Aircraft callsign (ICAO)',
                                     example='ABC1234'),
        status: Literal['UNKNOWN', 'STARTED', 'LANDED', 'EN_ROUTE'] | None =
                        Query(None,
                              title='Status',
                              description='Aircraft status ' + \
                                          '(UNKNOWN, STARTED, LANDED, or EN_ROUTE)',
                              example='LANDED'),
        model: str | None = Query(None, regex=Regex.aircraft_model_wildcard,
                                  title='Aircraft model',
                                  description='Aircraft model IATA code (4 characters)',
                                  example='B737'),
        registration: str | None = Query(None, regex=Regex.aircraft_registration_wildcard,
                                         title='Aircraft registration',
                                         description='Aircraft registration (tail number)',
                                         example='AB-CDE'),
        airline: str | None = Query(None, regex=Regex.code_2_wildcard,
                                    title='Airline IATA code',
                                    description='Airline IATA code (2 characters)',
                                    example='AA'),
        arrival: str | None = Query(None, regex=Regex.code_3_wildcard,
                                    title='Arrival airport IATA code',
                                    description='Arrival airport IATA code (3 characters)',
                                    example='AMS'),
        departure: str | None = Query(None, regex=Regex.code_3_wildcard,
                                      title='Departure airport IATA code',
                                      description='Departure airport IATA code (3 characters)',
                                      example='AMS'),
        on_ground: bool | None = Query(None,
                                       title='Whether on ground',
                                       description='Whether aircraft is on ground',
                                       example=True),
        squawk: str | None = Query(None, regex=Regex.transponder_squawk_wildcard,
                                   title='Squawk code',
                                   description='Transponder squawk code',
                                   example=1234),
        limit: int = Query(0, ge=0,
                           title='Limit',
                           description='Max. number of states to retrieve (0=all)',
                           example=20)
    ) -> list[State]:
    """Search for a state based on given information

    Args:
        storage (Storage): backend storage manager
        callsign (str | None): aircraft callsign (ICAO)
        status (Literal['UNKNOWN', 'STARTED', 'LANDED', 'EN_ROUTE'] | None): aircraft status
        model (str | None): aircraft model IATA code (4 characters)
        registration (str | None): aircraft registration (tail number)
        airline (str | None): airline IATA code (2 characters)
        arrival (str | None): arrival airport IATA code (3 characters)
        departure (str | None): departure airport IATA code (3 characters)
        on_ground (bool | None): whether aircraft is on ground
        squawk (str | None): transponder squawk code
        limit (int, optional): maximum number of states to retrieve (0=all). Defaults to 0 (all).

    Returns:
        list[State]: state search results
    """
    logger.info(f'API (search_state): callsign={callsign} status={status} model={model} ' + \
                f'registration={registration} airline={airline} arrival={arrival} ' + \
                f'departure={departure} on_ground={on_ground} squawk={squawk}')
    return await search_state(storage, limit, callsign, status, model, registration, airline,
                              arrival, departure, on_ground, squawk)
