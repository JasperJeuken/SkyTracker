"""Maps API endpoints"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Path, HTTPException

from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.models.maps import AircraftMapState
from skytracker.utils import logger


router = APIRouter(prefix='/maps', tags=['maps'])


@router.get('/nearby', response_model=List[AircraftMapState])
async def get_nearby(storage: Storage = Depends(get_storage),
                     lat: float = Query(ge=-90, le=90),
                     lon: float = Query(ge=-180, le=180),
                     radius: Optional[float] = Query(50, ge=1, le=1000),
                     limit: Optional[int] = Query(0, ge=0)) -> List[AircraftMapState]:
    """Get list of aircraft states close to a specified location

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        lat (float): location latitude [deg].
        lon (float): location longitude [deg].
        radius (float, optional): distance from location to search in [km]. Defaults to 50.0 km.
        limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    Returns:
        List[AircraftMapState]: list of aircraft states near specific point
    """
    # Get aircraft state matching specified settings
    logger.info(f'Get nearby aircraft: lat={lat}, lon={lon}, radius={radius}, limit={limit}')
    try:
        states = await storage['state'].get_nearby(lat, lon, radius, limit)
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err

    # Convert to map state model
    logger.info(f'Get nearby aircraft: {len(states)} states retrieved.')
    return [AircraftMapState(icao24=state.icao24,
                             latitude=state.latitude,
                             longitude=state.longitude,
                             heading=state.true_track) for state in states]


@router.get('/track/{icao24}', response_model=List[AircraftMapState])
async def get_track(storage: Storage = Depends(get_storage),
                    icao24: str = Path(min_length=6, max_length=6, regex='^[0-9A-Fa-f]{6}$'),
                    duration: str = Query('1d'),
                    limit: int = Query(0, ge=0)) -> List[AircraftMapState]:
    """Get the track history of a specific aircraft

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        icao24 (str): aircraft ICAO 24-bit address (must be 6-character hex code).
        duration (str, optional): duration of track (i.e. "5h20m" or "10m20s"). Defaults to 1 day.
        limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    Returns:
        List[AircraftMapState]: list of aircraft track states with specified duration
    """
    # Get aircraft states matching specified settings
    logger.info(f'Get track history: icao24={icao24}, duration={duration}, limit={limit}')
    try:
        states = await storage['state'].get_track(icao24, duration, limit)
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err

    # Convert to map state model
    logger.info(f'Get track history: {len(states)} states retrieved.')
    return [AircraftMapState(icao24=state.icao24,
                             latitude=state.latitude,
                             longitude=state.longitude,
                             heading=state.true_track) for state in states]


@router.get('', response_model=List[AircraftMapState])
async def get_all(storage: Storage = Depends(get_storage),
                  lat_min: Optional[float] = Query(None, description='Minimum latitude'),
                  lat_max: Optional[float] = Query(None, description='Maximum latitude'),
                  lon_min: Optional[float] = Query(None, description='Minimum longitude'),
                  lon_max: Optional[float] = Query(None, description='Maximum longitude'),
                  limit: Optional[int] = Query(0, ge=0, description='Max. number ' + \
                                              'of states to return (0=all)')) \
                  -> List[AircraftMapState]:
    """Get the latest batch of aircraft states

    The latest batch of aircraft states represent the most up-to-date states of aircraft around
    the world. Returned are the unique aircraft ICAO 24-bit address, latitude, longitude, and the
    aircraft heading.

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        lat_min (float, optional): minimum latitude in decimal degrees
        lat_max (float, optional): maximum latitude in decimal degrees
        lon_min (float, optional): minimum longitude in decimal degrees
        lon_max (float, optional): maximum longitude in decimal degrees
        limit (int, optional): maximum number of states to return (0=all). Defaults to 0 (all).

    Returns:
        List[AircraftMapState]: list of aircraft map states (icao24, latitude, longitude, heading)
    """
    # Get aircraft state matching specified settings
    logger.info(f'Get latest batch: bbox=({lat_min}, {lat_max}, {lon_min}, {lon_max}), ' + \
                f'limit={limit}')
    try:
        states = await storage['state'].get_latest_batch(limit, lat_min, lat_max, lon_min, lon_max)
    except ValueError as err:
        logger.error(f'Request failed ({err})')
        raise HTTPException(status_code=400, detail=f'{err}') from err

    # Convert to map state model
    logger.info(f'Get latest batch: {len(states)} states retrieved.')
    return [AircraftMapState(icao24=state.icao24,
                             latitude=state.latitude,
                             longitude=state.longitude,
                             heading=state.true_track) for state in states]
