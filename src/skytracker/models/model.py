"""Generic model module"""
from typing import Any

from pydantic import BaseModel, field_validator, ValidationInfo


class APIBaseModel(BaseModel):
    """Generic base model which implements common pre-processing steps"""

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

        # Float pre-processing
        if isinstance(value, float):
            if any(part in info.field_name.lower() for part in ('latitude', 'longitude')) \
                    and value == 0.0:
                return None
            return value

        return value
