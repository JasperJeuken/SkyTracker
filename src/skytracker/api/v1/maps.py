"""Maps API endpoints"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from skytracker.dependencies import get_storage
from skytracker.storage import Storage
from skytracker.models.maps import AircraftMapState


router = APIRouter(prefix='/maps', tags=['maps'])


@router.get('', response_model=List[AircraftMapState])
async def get_latest_batch(storage: Storage = Depends(get_storage),
                           min_lat: Optional[float] = Query(None, description='Minimum latitude'),
                           max_lat: Optional[float] = Query(None, description='Maximum latitude'),
                           min_lon: Optional[float] = Query(None, description='Minimum longitude'),
                           max_lon: Optional[float] = Query(None, description='Maximum longitude'),
                           limit: Optional[int] = Query(0, ge=0, description='Max. number ' + \
                                                        'of states to return (0=all)')) \
                            -> List[AircraftMapState]:
    """Get the latest batch of aircraft states

    The latest batch of aircraft states represent the most up-to-date states of aircraft around
    the world. Returned are the unique aircraft ICAO 24-bit address, latitude, longitude, and the
    aircraft heading.

    Args:
        storage (Storage, optional): backend storage manager. Defaults to Depends(get_storage).
        min_lat (float, optional): minimum latitude in decimal degrees
        max_lat (float, optional): maximum latitude in decimal degrees
        min_lon (float, optional): minimum longitude in decimal degrees
        max_lon (float, optional): maximum longitude in decimal degrees
        limit (int, optional): maximum number of states to return (0=all). Defaults to 0 (all).

    Returns:
        List[AircraftMapState]: list of aircraft map states (icao24, latitude, longitude, heading)
    """
    # Get aircraft state matching specified settings
    try:
        states = await storage['state'].get_latest_batch(limit, min_lat, max_lat, min_lon, max_lon)
    except TypeError:
        raise HTTPException(status_code=400, detail='Bounding box values must be numeric')
    except ValueError:
        raise HTTPException(status_code=400, detail='Limit value must be >= 0')
    
    # Convert to map state model, only if latitude and longitude available
    return [AircraftMapState(icao24=state.icao24, latitude=state.latitude,
                                 longitude=state.longitude, heading=state.true_track) 
            for state in states if state.longitude is not None and state.latitude is not None]
