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
    return {'message': 'nearby'}


@router.get('/{icao24}')
async def get_aircraft_details(icao24: str = Path(regex='^[0-9A-Fa-f]{6}$')):
    return {'message': 'details'}


@router.get('/{icao24}/track')
async def get_aircraft_track(icao24: str = Path(regex='^[0-9A-Fa-f]{6}$')):
    return {'message': 'track'}
