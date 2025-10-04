"""Aircraft endpoint models"""
from typing import Annotated, Any
from datetime import datetime, timezone
from enum import IntEnum

from pydantic import BaseModel, Field, field_validator, field_serializer

from skytracker.utils import log_and_raise


class AircraftStatus(IntEnum):
    """Aircraft status"""

    ACTIVE: int = 1
    """int: active status"""
    INACTIVE: int = 2
    """int: inactive status"""
    UNKNOWN: int = 3
    """int: unknown status"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get aircraft status from a string

        Args:
            value (str): string to parse

        Returns:
            int: aircraft status
        """
        match value.lower():
            case 'active':
                return cls.ACTIVE
            case 'inactive':
                return cls.INACTIVE
            case '' | 'unknown':
                return cls.UNKNOWN
            case _:
                log_and_raise(ValueError, f'Unknown aircraft status: {value}')


class AircraftEngineType(IntEnum):
    """Aircraft engine type"""

    JET: int = 1
    """int: jet engine"""
    TURBOFAN: int = 2
    """int: turbofan engine"""
    TURBOPROP: int = 3
    """int: turboprop engine"""
    UNKNOWN: int = 4
    """int: unknown engine"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get engine type from a string

        Args:
            value (str): string to parse

        Returns:
            int: engine type
        """
        match value.lower():
            case 'jet':
                return cls.JET
            case 'turbofan':
                return cls.TURBOFAN
            case 'turboprop':
                return cls.TURBOPROP
            case '' | 'unknown':
                return cls.UNKNOWN
            case _:
                log_and_raise(ValueError, f'Unknown engine type: {value}')


class AircraftClassification(IntEnum):
    """Aircraft classification (currently not working)"""

    UNKNOWN: int = 1
    """int: unknown classification"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get aircraft classification from a string

        Args:
            value (str): string to parse

        Returns:
            int: aircraft classification
        """
        match value.lower():
            case '' | 'unknown':
                return cls.UNKNOWN
            case _:
                log_and_raise(ValueError, f'Unknown aircaft classification: {value}')


class AircraftIdentity(BaseModel):
    """Aircraft identity data"""

    icao24: Annotated[str | None, Field(description='Aircraft IATA 24-bit address (hex)')]
    """str | None: aircraft IATA 24-bit address (hex)"""
    registration: Annotated[str | None, Field(description='Aircraft registration')]
    """str | None: aircraft registration"""
    test_registration: Annotated[str | None,
                                 Field(description='Aircraft test registration (before delivery)')]
    """str | None: aircraft test registration (before delivery)"""
    owner: Annotated[str | None, Field(description='Current aircraft owner')]
    """str | None: current aircraft owner"""
    airline_iata: Annotated[str | None, Field(description='Airline IATA code')]
    """str | None: airline IATA code"""
    airline_icao: Annotated[str | None, Field(description='Airline ICAO code')]
    """str | None: airline ICAO code"""

class AircraftModel(BaseModel):
    """Aircraft model data"""

    type_iata: Annotated[str | None, Field(description='Aircraft type IATA designation')]
    """str | None: aircraft type IATA designation"""
    type_iata_code_short: Annotated[str, Field(description='Aircraft type IATA code (short)')]
    """str: aircraft type IATA code (short)"""
    type_iata_code_long: Annotated[str, Field(description='Aircraft type IATA code (long)')]
    """str: aircraft type IATA code (long)"""
    engine_count: Annotated[int | None, Field(description='Number of engines on aircraft')]
    """int | None: number of engines on aircraft"""
    engine_type: Annotated[AircraftEngineType, Field(description='Type of engines on aircraft')]
    """AircraftEngineType: type of engines on aircraft"""
    model_code: Annotated[str | None, Field(description='Aircraft model code (manufacturer)')]
    """str | None: aircraft model code (manufacturer)"""
    line_number: Annotated[str | None, Field(description='Aircraft line number (manufacturer)')]
    """str | None: aircraft line number (manufacturer)"""
    serial_number: Annotated[str | None,
                                   Field(description='Aircraft serial number (manufacturer)')]
    """str | None: aircraft serial number (manufacturer)"""
    family: Annotated[str | None, Field(description='Aircraft family (manufacturer)')]
    """str | None: aircraft family (manufacturer)"""
    sub_family: Annotated[str | None, Field(description='Aircraft sub-family (manufacturer)')]
    """str | None: aircraft sub-family (manufacturer)"""
    series: Annotated[str | None, Field(description='Aircraft series/variant (manufacturer)')]
    """str | None: aircraft series/variant (manufacturer)"""
    classification: Annotated[AircraftClassification, Field(description='Aircraft classification')]
    """AircraftClassification: aircraft classification"""

    @field_validator('engine_type', mode='before')
    @classmethod
    def parse_engine_type(cls, value: Any) -> AircraftEngineType:
        """Parse engine type value

        Args:
            value (Any): engine type value

        Returns:
            AircraftStatus: parsed engine type
        """
        if value is None:
            return AircraftEngineType.UNKNOWN
        if isinstance(value, str):
            return AircraftEngineType.from_string(value)
        return value
    
    @field_serializer('engine_type')
    @classmethod
    def serialize_engine_type(cls, engine_type: AircraftEngineType) -> str:
        """Serialize engine type

        Args:
            engine_type (AircraftEngineType): engine type

        Returns:
            str: engine type name
        """
        return engine_type.name

    @field_validator('classification', mode='before')
    @classmethod
    def parse_classification(cls, value: Any) -> AircraftClassification:
        """Parse classification value

        Args:
            value (Any): classification value

        Returns:
            AircraftClassification: parsed classification
        """
        if value is None:
            return AircraftClassification.UNKNOWN
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return AircraftClassification.from_string(value)
        return value
    
    @field_serializer('classification')
    @classmethod
    def serialize_classification(cls, classification: AircraftClassification) -> str:
        """Serialize classification

        Args:
            classification (AircraftClassification): classification

        Returns:
            str: classification name
        """
        return classification.name


class AircraftLifecycle(BaseModel):
    """Aircraft lifecycle"""
    
    date_delivery: Annotated[datetime | None,
                             Field(description='Date aircraft was delivered to operator')]
    """datetime | None: date aircraft was delivered to operator"""
    date_first_flight: Annotated[datetime | None, Field('Date of first flight')]
    """datetime | None: date of first flight"""
    date_registration: Annotated[datetime | None, Field('Date aircraft was registered')]
    """datetime | None: date aircraft was registered"""
    date_rollout: Annotated[datetime | None, Field('Date aircraft was rolled out of factory')]
    """datetime | None: date aircraft was rolled out of factory"""
    age: Annotated[int | None, Field(description='Aircraft age [year]')]
    """int | None: aircraft age [year]"""

    @field_validator('date_delivery', 'date_first_flight', 'date_registration', 'date_rollout',
                     mode='before')
    @classmethod
    def validate_dates(cls, date: datetime | str | None) -> datetime:
        """Validate date attributes

        Args:
            date (datetime): date attribute

        Returns:
            datetime: validated date attribute
        """
        if date is None:
            return date
        if isinstance(date, str):
            return datetime.strptime(date.strip(), '%Y-%m-%d %H:%M:%S')
        if not date.time():
            date.hour, date.minute, date.second, date.microsecond = 0, 0, 0, 0
        return datetime(date.year, date.month, date.day,
                        date.hour, date.minute, date.second, date.microsecond, tzinfo=timezone.utc)
    
    @field_serializer('date_delivery', 'date_first_flight', 'date_registration', 'date_rollout')
    @classmethod
    def serialize_dates(cls, date: datetime | None) -> str:
        """Serialize date

        Args:
            date (datetime | None): datetime

        Returns:
            str: serialized datetime
        """
        if date is None:
            return '1970-01-01 00:00:00'
        return date.strftime('%Y-%m-%d %H:%M:%S')


class Aircraft(BaseModel):
    """Aircraft data"""

    identity: Annotated[AircraftIdentity, Field(description='Aircraft identity and registration')]
    """AircraftIdentity: aircraft identity and registration"""
    model: Annotated[AircraftModel, Field(description='Aircraft type and model')]
    """AircraftModel: aircraft type and model"""
    lifecycle: Annotated[AircraftLifecycle, Field(description='Aircraft lifecycle and dates')]
    """AircraftLifecycle: aircraft lifecycle and dates"""
    status: Annotated[AircraftStatus, Field(description='Aircraft status')]
    """AircraftStatus: aircraft status"""

    @field_validator('status', mode='before')
    @classmethod
    def parse_aircraft_status(cls, value: Any) -> AircraftStatus:
        """Parse aircraft status value

        Args:
            value (Any): aircraft status value

        Returns:
            AircraftStatus: parsed aircraft status
        """
        if value is None:
            return AircraftStatus.UNKNOWN
        if isinstance(value, str):
            return AircraftStatus.from_string(value)
        return value
    
    @field_serializer('status')
    @classmethod
    def serialize_aircraft_status(cls, aircraft_status: AircraftStatus) -> str:
        """Serialize aircraft status

        Args:
            aircraft_status (AircraftStatus): aircraft status

        Returns:
            str: aircraft status name
        """
        return aircraft_status.name


class AircraftPhoto(BaseModel):
    """Aircraft photo information"""
    image_url: str = Field(description='URL to image of aircraft')
    """URL to image of aircraft"""
    detail_url: str = Field(description='URL to aircraft detail page')
    """URL to aircraft detail page"""
