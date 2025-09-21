"""Geographic utilities"""
import numpy as np


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
