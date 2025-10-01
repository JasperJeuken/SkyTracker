"""State API endpoints"""
from fastapi import APIRouter, Depends, Query, Path

from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.models.state import SimpleMapState, DetailedMapState, State
from skytracker.services.maps import get_nearby, get_track, get_all, get_latest
from skytracker.utils import logger


router = APIRouter(prefix='/state', tags=['state'])


@router.get('/nearby', response_model=list[SimpleMapState])
async def api_get_nearby(storage: Storage = Depends(get_storage),
                         lat: float = Query(),
                         lon: float = Query(),
                         radius: float = Query(50, ge=1, le=1000),
                         limit: int = Query(0, ge=0)) -> list[SimpleMapState]:
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


@router.get('/track/{callsign}', response_model=list[DetailedMapState])
async def api_get_track(storage: Storage = Depends(get_storage),
                        callsign: str = Path(),
                        duration: str = Query('1d'),
                        limit: int = Query(0, ge=0)) -> list[DetailedMapState]:
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


@router.get('/all', response_model=list[SimpleMapState])
async def api_get_all(storage: Storage = Depends(get_storage),
                      south: float | None = Query(None, description='Minimum latitude'),
                      north: float | None = Query(None, description='Maximum latitude'),
                      west: float | None = Query(None, description='Minimum longitude'),
                      east: float | None = Query(None, description='Maximum longitude'),
                      limit: int = Query(0, ge=0, description='Max. number ' + \
                                                   'of states to return (0=all)')) \
                  -> list[SimpleMapState]:
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
    return await get_all(storage, south, north, west, east, limit)


@router.get('/{callsign}', response_model=State)
async def api_get_latest(storage: Storage = Depends(get_storage), callsign: str = Path()) -> State:
    """Get the last known state of a specific aircraft

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        callsign (str, optional): aircraft callsign (ICAO)

    Returns:
        State: last known state
    """
    logger.info(f'API (get_latest): callsign={callsign}')
    return await get_latest(storage, callsign)
