"""API configuration"""
from typing import Any
import json


def get_credentials(path: str = 'credentials.json') -> dict[str, Any]:
    """Load application credentials from a JSON file

    Args:
        path (str, optional): path to credentials JSON file. Defaults to 'credentials.json'.

    Returns:
        dict[str, Any]: pairs of credential name and value
    """
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)
