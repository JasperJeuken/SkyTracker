"""Aircraft endpoint models"""
from typing import Annotated, Optional

from pydantic import BaseModel, Field, constr


class AircraftDetails(BaseModel):
    """Model for aircraft details"""

    icao24: Annotated[str, constr(min_length=1, max_length=1)] = \
        Field(description='Unique aircraft ICAO 24-bit address (hex string)')
    """Aircraft ICAO 24-bit address (hex)"""
    known_callsigns: list[str] = Field(description='List of known callsigns')
    """List of known callsigns used for this aircraft"""
    origin_country: str = Field(description='Origin country (inferred from ICAO code)')
    """Origin country (inferred from ICAO code)"""
    last_state: int = Field(description='Unix timestamp of last known state')
    """Unix timestamp of last known state"""
    last_position: int = Field(description='Unix timestamp of last known position update')
    """Unix timestamp of last known position update"""
    last_contact: int = Field(description='Unix timestamp of last known transponder message')
    """Unix timestamp of last known transponder message"""
    last_latitude: Optional[float] = Field(None, description='Last known latitude')
    """Last known latitude"""
    last_longitude: Optional[float] = Field(None, description='Last known longitude')
    """Last known longitude"""
    last_baro_altitude: Optional[float] = Field(None, description='Last known barometric altitude')
    """Last known barometric altitude"""
    last_geo_altitude: Optional[float] = Field(None, description='Last known geometric altitude')
    """Last known geometric altitude"""
    last_velocity: Optional[float] = Field(None, description='Last known velocity')
    """Last known velocity"""
    last_heading: Optional[float] = Field(None, description='Last known heading')
    """Last known heading"""
    last_vertical_rate: Optional[float] = Field(None, description='Last known vertical rate')
    """Last known vertical rate"""
    last_on_ground: bool = Field(description='Whether last position was a surface report')
    """Whether last position was a surface report"""
    last_spi: bool = Field(description='Special purpose indicator')
    """Special purpose indicator"""
    last_squawk: Optional[str] = Field(description='Last known squawk code')
    """Last known squawk code"""
    last_position_source: str = Field(description='Last known position source')
    """Last known position source"""
    last_category: str = Field(description='Last known category')
    """Last known category"""


class AircraftPhoto(BaseModel):
    """Aircraft photo information"""
    image_url: str = Field(description='URL to image of aircraft')
    """URL to image of aircraft"""
    detail_url: str = Field(description='URL to aircraft detail page')
    """URL to aircraft detail page"""
