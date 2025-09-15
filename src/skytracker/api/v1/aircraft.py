"""Aircraft API endpoints"""
from typing import Annotated, Optional, List

from fastapi import APIRouter, HTTPException, Query, Path, Depends

from skytracker.storage import Storage
from skytracker.dependencies import get_storage
from skytracker.models.aircraft import AircraftDetails
from skytracker.models.maps import AircraftMapState


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


@router.get('/nearby', response_model=List[AircraftMapState])
async def get_nearby_aircraft(storage: Storage = Depends(get_storage),
                              lat: float = Query(ge=-90, le=90),
                              lon: float = Query(ge=-180, le=180),
                              radius: Optional[float] = Query(50, ge=1, le=1000),
                              limit: Optional[int] = Query(0, ge=0)) -> List[AircraftMapState]:
    """Get list of aircraft close to a specified location

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
    try:
        states = await storage['state'].get_in_radius(lat, lon, radius, limit)
    except ValueError:
        raise HTTPException('Invalid argument supplied')
    
    # Convert to map state model, only if latitude and longitude available
    return [AircraftMapState(icao24=state.icao24, latitude=state.latitude,
                                 longitude=state.longitude, heading=state.true_track) 
            for state in states if state.longitude is not None and state.latitude is not None]


@router.get('/{icao24}')
async def get_aircraft_details(icao24: Annotated[str, Path(regex='^[0-9A-Fa-f]{6}$')]):
    """Get the details of a specific aircraft

    Args:
        icao24 (str): aircraft ICAO 24-bit address.

    Returns:
        _type_: _description_
    """
    return {'message': f'track: icao24={icao24}'}


@router.get('/{icao24}/track')
async def get_aircraft_track(icao24: Annotated[str, Path(regex='^[0-9A-Fa-f]{6}$')]):
    """Get the track of a specific aircraft

    Args:
        icao24 (str): aircraft ICAO 24-bit address.

    Returns:
        _type_: _description_
    """
    return {'message': f'track: icao24={icao24}'}
