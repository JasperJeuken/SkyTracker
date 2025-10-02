"""Analysis utility functions"""
from typing import Any, TypeVar
from urllib.parse import quote, unquote
from fnmatch import fnmatch

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


def decode(uri: str | None) -> str | None:
    """Decode text from a Uniform Resource Identifier (URI)

    Args:
        uri (str): Uniform Resource Identifier (URI)

    Returns:
        str | None: decoded text
    """
    if uri is None:
        return None
    return unquote(uri)


def encode(text: str | None) -> str | None:
    """Encode text to a Uniform Resource Identifier

    Args:
        text (str | None): encoded text
    
    Returns:
        str | None: Uniform Resource Identifier (URI)
    """
    if text is None:
        return None
    return quote(text)


def get_nested_attribute(obj: Any, attribute_path: str, default: Any = None) -> Any:
    """Get a nested attribute of an object using a dot-separated path

    Args:
        obj (Any): object to get attribute from
        attribute_path (str): dot-separated attribute path
        default (Any, optional): default value if attribute is not found. Defaults to None.

    Returns:
        Any: attribute value
    """
    try:
        for attribute in attribute_path.split('.'):
            obj = getattr(obj, attribute)
        return obj
    except AttributeError:
        return default


ObjectType = TypeVar('ObjectType')


def search_object_list(objects: list[ObjectType], fields: dict[str, Any],
                       limit: int = 0) -> list[ObjectType]:
    """Search for objects in a list of objects that match dot-separated attribute path values

    Args:
        objects (list[ObjectType]): list of objects to search
        fields (dict[str, Any]): dot-separated path, value pairs
        limit (int, optional): maximum number of objects to return (0=all). Defaults to 0.

    Returns:
        list[ObjectType]: objects matching fields
    """
    results = []
    for obj in objects:

        match = True
        for field, value in fields.items():
            obj_value = get_nested_attribute(obj, field)

            # Support wildcards for strings
            if obj_value is None and value is not None:
                match = False
                break
            if isinstance(value, str):
                if not fnmatch(obj_value, value.replace('.', '*').replace('_', '?')):
                    match = False
                    break
            elif obj_value != value:
                match = False
                break

        if match:
            results.append(obj)
        if limit > 0 and len(results) >= limit:
            break

    return results
