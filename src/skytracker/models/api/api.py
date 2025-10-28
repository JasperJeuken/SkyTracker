"""Generic external API class"""
from abc import ABC, abstractmethod
from enum import IntEnum

from skytracker.models.state import State
from skytracker.settings import Settings


class APIResponse(ABC):
    """Abstract class for external API response"""

    @abstractmethod
    def to_states(self) -> list[State]:
        """Parse API response into list of aircraft states

        Returns:
            list[State]: list of aircraft states
        """


class API(ABC):
    """Abstract class for external API"""

    def __init__(self, settings: Settings) -> None:
        """Initialize API using settings

        Args:
            settings (Settings): settings
        """

    @abstractmethod
    def get_states(self) -> list[State]:
        """Get list of aircraft states from external API

        Returns:
            list[State]: aircraft states
        """


class APIType(IntEnum):
    """External API type"""

    OPENSKY_NETWORK: int = 1
    """int: OpenSky Network API"""
    AVIATION_EDGE: int = 2
    """int: Aviation Edge API"""
