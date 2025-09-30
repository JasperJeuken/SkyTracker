"""Maps endpoint models"""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class SimpleMapState(BaseModel):
    """Simple map state with position and heading"""

    callsign: Annotated[str, Field(description='Aircraft callsign')]
    """str: aircraft callsign"""
    position: Annotated[tuple[float, float], Field(description='Latitude/longitude position [deg]')]
    """tuple[float, float]: latitude/longitude position [deg]"""
    heading: Annotated[float | None, Field(description='Heading [deg]')]
    """float | None: heading [deg]"""


class DetailedMapState(BaseModel):
    """Detailed map state with time, position, heading, and altitude"""

    time: Annotated[datetime, Field(description='State timestamp')]
    """datetime: state timestamp"""
    callsign: Annotated[str, Field(description='Aircraft callsign')]
    """str: aircraft callsign"""
    position: Annotated[tuple[float, float], Field(description='Latitude/longitude position [deg]')]
    """tuple[float, float]: latitude/longitude position [deg]"""
    heading: Annotated[float | None, Field(description='Heading [deg]')]
    """float | None: heading [deg]"""
    altitude: Annotated[float | None, Field(description='Barometric altitude [m]')]
    """float | None: barometric altitude [m]"""
