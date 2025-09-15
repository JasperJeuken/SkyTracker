"""Maps endpoint models"""
from typing import Annotated, Optional

from pydantic import BaseModel, Field, constr


class AircraftMapState(BaseModel):
    """Model for aircraft map state"""

    icao24: Annotated[str, constr(min_length=1, max_length=1)] = \
        Field(..., description='Unique aircraft ICAO 24-bit address (hex string)')
    """Aircraft ICAO 24-bit address (hex)"""
    latitude: float = Field(..., description='Latitude in decimal degrees')
    """Aircraft latitude in decimal degrees"""
    longitude: float = Field(..., description='Longitude in decimal degrees')
    """Aircraft longitude in decimal degrees"""
    heading: Optional[float] = Field(..., description='Aircraft heading in degrees (0=360=north)')
    """Aircraft heading in degrees (0=360=north)"""
