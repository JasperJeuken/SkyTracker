"""Analysis utility functions"""
from skytracker.models.state import State


def filter_states(states: list[State], *required_field) -> list[State]:
    """Filter a list of states to ensure specific required fields are not None

    Args:
        states (list[State]): original list of states

    Returns:
        list[State]: filtered list of states
    """
    return [state for state in states if \
            all(getattr(state, field) is not None for field in required_field)]
