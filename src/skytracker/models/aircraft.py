"""Aircraft endpoint models"""
from typing import Annotated

from pydantic import BaseModel, Field

from skytracker.models.state import State


class AircraftDetails(State):
    """Aircraft detail data"""

    aircraft_country: Annotated[str, Field(description='Aircraft origin country')]
    """str: aircraft origin country"""


class AircraftPhoto(BaseModel):
    """Aircraft photo information"""
    image_url: str = Field(description='URL to image of aircraft')
    """URL to image of aircraft"""
    detail_url: str = Field(description='URL to aircraft detail page')
    """URL to aircraft detail page"""
