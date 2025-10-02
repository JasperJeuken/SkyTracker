"""Geographic utilities"""
import numpy as np
import pycountry
from fastapi import Query

from skytracker.utils.logger import log_and_raise_http


def distance_between_points(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the distance between two points described by coordinates

    Uses the Haversine formula for great-circle distance

    Args:
        lat1 (float): latitude of first point
        lon1 (float): longitude of first point
        lat2 (float): latitude of second point
        lon2 (float): longitude of second point

    Returns:
        float: distance between points [km]
    """
    radius = 6371  # [km] Earth radius
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    return 2 * radius * np.arcsin(
        np.sqrt((1 - np.cos(dlat) + \
                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * (1 - np.cos(dlon))) / 2))


def normalize_longitude_bbox(lon_min: float, lon_max: float) -> list[tuple[float, float]]:
    """Get bounding boxes in the range [-180, 180] that are equivalent to the specified range

    Used for wrapping maps where the longitude can exceed -180 or 180.

    Args:
        lon_min (float): minimum longitude [deg]
        lon_max (float): maximum longitude [deg]

    Returns:
        list[tuple[float, float]]: equivalent bounding boxes in range [-180, 180]
    """
    # Calculate span, make sure it is nonnegative
    span = lon_max - lon_min
    while span < 0:
        span += 360

    # Catch full span box
    if span >= 360:
        return [(-180, 180)]

    # Normalize latitude and longitude
    lon_min_norm = ((lon_min + 180) % 360) - 180
    lon_max_norm = lon_min_norm + span

    # Return single box if fits in range
    if lon_max_norm <= 180:
        return [(lon_min_norm, lon_max_norm)]

    # Return two boxes if not
    return [(lon_min_norm, 180), (-180, lon_max_norm - 360)]


def shift_longitude_into_range(lon: float, lon_min: float, lon_max: float) -> float:
    """Shift a longitude from the range [-180, 180] into the specified range [lon_min, lon_max]

    Args:
        lon (float): longitude to shift
        lon_min (float): range minimum
        lon_max (float): range maximum

    Returns:
        float: mapped longitude
    """
    span = lon_max - lon_min
    if span <= 0:
        raise ValueError(f'Invalid range ({lon_min}, {lon_max})')
    
    # Shift by multiples of 360
    while lon < lon_min:
        lon += 360
    while lon > lon_max:
        lon -= 360
    return lon


def is_country_code(text: str) -> bool:
    """Check whether a code is a valid ISO 3166-1 A-2 country code

    Args:
        text (str): text to parse

    Returns:
        bool: whether text is a valid ISO 3166-1 A-2 country code
    """
    return pycountry.countries.get(alpha_2=text) is not None


def country_code_validator(code: str | None = Query(None, min_length=2, max_length=2,
                                                    alias='country',
                                                    title='Country code',
                                                    description='ISO 3166-1 A-2 code (2 character)',
                                                    example='US')) -> str:
    """Validate whether a string is a valid ISO 3166-1 A-2 country code

    Args:
        code (str): string to parse
    
    Raises:
        HTTPException: if string is not a valid ISO 3166-1 A-2 country code

    Returns:
        str: valid ISO 3166-1 A-2 country code
    """
    if code is None:
        return None
    if not is_country_code(code.upper()):
        log_and_raise_http(f'Invalid country code: {code}', 422)
    return code.upper()
