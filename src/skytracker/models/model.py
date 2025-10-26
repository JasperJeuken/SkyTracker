"""Generic model module"""
from typing import Any, Type, TypeVar

from pydantic import BaseModel, field_validator, ValidationInfo


class APIBaseModel(BaseModel):
    """Generic base model for API responses"""

    @field_validator('*', mode='before')
    @classmethod
    def pre_processing(cls, value: Any, info: ValidationInfo) -> Any:
        """Perform common pre-processing steps

        Args:
            value (Any): value to process
            info (ValidationInfo): field information

        Returns:
            Any: processed value
        """
        # String pre-processing
        if isinstance(value, str):
            value = value.strip()
            if not len(value):
                return None
            if value.lower() in ('-', '_', 'n/a', 'none', 'null'):
                return None
            return value

        return value


ModelType = TypeVar('ModelType', bound=BaseModel)


def flatten_model(model: BaseModel, sep: str = '__') -> dict[str, Any]:
    """Flatten a base model into a one-level dictionary

    Args:
        model (BaseModel): base model to flatten
        sep (str, optional): level separator. Defaults to '__'.

    Returns:
        dict[str, Any]: flattened model
    """

    def _flatten_dict(nested: dict[str, Any], prefix: str = '', _sep: str = '__') -> dict[str, Any]:
        """Helper function for flattening a dictionary

        Args:
            nested (dict[str, Any]): nested dictionary to flatten
            prefix (str, optional): current level prefix. Defaults to ''.
            _sep (str, optional): level separator. Defaults to '__'.

        Returns:
            dict[str, Any]: flattened dictionary
        """
        _flat = {}
        for key, value in nested.items():
            if not isinstance(value, dict):
                _flat[f'{prefix}{key}'] = value
            else:
                _flat |= _flatten_dict(value, f'{prefix}{key}{_sep}', _sep)
        return _flat
    
    return _flatten_dict(model.model_dump(), _sep=sep)


def unflatten_model(flat: dict[str, Any], expected: Type[ModelType], sep: str = '__') -> ModelType:
    """Unflatten a one-level dictionary into a base model

    Args:
        flat (dict[str, Any]): flattened model
        expected (Type[ModelType]): expected base model
        sep (str, optional): level separator. Defaults to '__'.

    Returns:
        ModelType: unflattened model
    """

    def _unflatten_dict(_flat: dict[str, Any], _sep: str = '__') -> dict[str, Any]:
        """Helper function for unflattening a dictionary

        Args:
            flat (dict[str, Any]): flat dictionary
            _sep (str, optional): level separator. Defaults to '__'.

        Returns:
            dict[str, Any]: unflattened dictionary
        """
        _unflat = {}
        for key, value in _flat.items():
            keys = key.split(_sep)
            current = _unflat
            for key in keys[:-1]:
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
        return _unflat
    
    unflattened = _unflatten_dict(flat, _sep=sep)
    return expected.model_validate(unflattened)
