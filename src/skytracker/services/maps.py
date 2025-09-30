"""Maps endpoint services"""
from fastapi import HTTPException

from skytracker.storage import Storage
from skytracker.models.maps import SimpleMapState, DetailedMapState
from skytracker.utils import logger


async def get_nearby(storage: Storage, lat: float, lon: float,
                     radius: float, limit: int) -> list[SimpleMapState]:
    """Get list of aircraft states close to a specified location

    Args:
        storage (Storage): backend storage manager
        lat (float): latitude [deg]
        lon (float): longitude [deg]
        radius (float): distance from point to search in [km]
        limit (int): maximum number of states to get (0=all)

    Returns:
        list[SimpleMapState]: list of aircraft near specified point
    """
    try:
        states = await storage['state'].get_nearby(lat, lon, radius, limit)
        return [SimpleMapState(callsign=state.flight_icao,
                               position=state.position,
                               heading=state.heading) for state in states]
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err


async def get_track(storage: Storage, callsign: str, duration: str, limit: int) -> list[DetailedMapState]:
    """Get the track history of a specific aircraft

    Args:
        storage (Storage): backend storage manager
        callsign (str): aircraft callsign (ICAO)
        duration (str): duration of track (i.e. "5h20m" or "10m20s")
        limit (int): maximum number of states to get (0=all)

    Returns:
        list[DetailedMapState]: list of aircraft track states
    """
    try:
        states = await storage['state'].get_track(callsign, duration, limit)
        return [DetailedMapState(time=state.time, callsign=state.flight_icao,
                                 position=state.position, heading=state.heading,
                                 altitude=state.baro_altitude) for state in states]
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err


async def get_all(storage: Storage, south: float, north: float,
                  west: float, east: float, limit: int) -> list[SimpleMapState]:
    """Get the latest batch of aircraft states

    Args:
        storage (Storage): backend storage manager
        south (float): minimum latitude [deg]
        north (float): maximum latitude [deg]
        west (float): minimum longitude [deg]
        east (float): maximum longitude [deg]
        limit (int): maximum number of states to return (0=all)

    Returns:
        list[SimpleMapState]: list of aircraft map states
    """
    try:
        states = await storage['state'].get_latest_batch(limit, south, north, west, east)
        return [SimpleMapState(callsign=state.flight_icao, position=state.position,
                               heading=state.heading) for state in states]
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err
