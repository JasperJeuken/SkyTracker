"""Aircraft API endpoints"""
from typing import Annotated

from fastapi import APIRouter, Path


router = APIRouter(prefix='/aircraft', tags=['aircraft'])


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
