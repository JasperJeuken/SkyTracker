"""Airport endpoint models"""
from typing import Annotated

from pydantic import BaseModel, Field


class Airport(BaseModel):
    """Airport data"""

    iata: Annotated[str, Field(description='Airport IATA code')]
    """str: airport IATA code"""
    icao: Annotated[str | None, Field(description='Airport ICAO code')]
    """str | None: airport ICAO code"""
    name: Annotated[str, Field(description='Airport name')]
    """str: airport name"""
    latitude: Annotated[float | None, Field(description='Airport latitude [deg]')]
    """float | None: airport latitude [deg]"""
    longitude: Annotated[float | None, Field(description='Airport longitude [deg]')]
    """float | None: airport longitude [deg]"""
    geoname_id: Annotated[int | None, Field(description='Airport Geonames ID')]
    """int | None: airport Geonames ID"""
    phone: Annotated[str | None, Field(description='Airport phone number')]
    """str: airport phone number"""
    timezone: Annotated[str | None, Field(description='Airport timezone name')]
    """str: airport timezone name"""
    gmt: Annotated[str | None, Field(description='Airport GMT offset')]
    """float: airport GMT offset"""
    city_iata: Annotated[str | None, Field(description='City IATA code')]
    """str: city IATA code"""
    country_iso2: Annotated[str, Field(description='Country ISO 3166-1 alpha-2 code')]
    """str: country ISO 3166-1 alpha-2 code"""
    country_name: Annotated[str, Field(description='Country name')]
    """str: country name"""
