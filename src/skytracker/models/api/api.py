"""Generic external API class"""
from abc import ABC, abstractmethod

from skytracker.models.state import State


class APIResponse(ABC):
    """Abstract class for external API response"""

    @abstractmethod
    def to_states(self) -> list[State]:
        """Parse API response into list of aircraft states

        Returns:
            list[State]: list of aircraft states
        """
