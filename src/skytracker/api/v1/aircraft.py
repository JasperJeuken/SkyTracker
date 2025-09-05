"""Aircraft API endpoints"""
from typing import Annotated

from fastapi import APIRouter, Query, Path

# from skytracker.models.aircraft import
# from skytracker.services.aircraft import


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


@router.get('/nearby')
async def get_nearby_aircraft(lat: Annotated[float, Query(ge=-90, le=90)],
                              lon: Annotated[float, Query(ge=-180, le=180)],
                              radius: Annotated[float, Query(ge=1, le=1000)] = 50.0):
    """Get list of aircraft close to a specified location

    Args:
        lat (float): location latitude [deg].
        lon (float): location longitude [deg].
        radius (float, optional): distance from location to search in [km]. Defaults to 50.0.

    Returns:
        _type_: _description_
    """
    return {'message': f'nearby: lat={lat}, lon={lon}, radius={radius}'}


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
