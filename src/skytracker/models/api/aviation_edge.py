"""Aviation Edge API models"""
from typing import Annotated, Iterator, Generic, TypeVar
from datetime import datetime, timezone
import re

from pydantic import RootModel, Field, field_validator, model_validator

from skytracker.models.api import APIResponse, APIType
from skytracker.models import APIBaseModel
from skytracker.models.state import State, StateStatus
from skytracker.models.airport import Airport
from skytracker.models.airline import Airline
from skytracker.models.aircraft import Aircraft, AircraftLifecycle, AircraftIdentity, AircraftModel
from skytracker.utils.conversions import country_name_to_country_code, country_code_to_country_name
from skytracker.utils import Regex


class AviationEdgeFlightTrackingAircraft(APIBaseModel):
    """Aviation Edge API flight tracking aircraft data"""

    iataCode: Annotated[str, Field(description='Aircraft IATA code')]
    """str: aircraft IATA code"""
    icaoCode: Annotated[str, Field(description='Aircraft ICAO code')]
    """str: aircraft ICAO code"""
    icao24: Annotated[str, Field(description='Aircraft ICAO 24-bit address (hex)')]
    """str: aircraft ICAO 24-bit address (hex)"""
    regNumber: Annotated[str, Field(description='Aircraft registration number')]
    """str: aircraft registration number"""


class AviationEdgeFlightTrackingAirline(APIBaseModel):
    """Aviation Edge API flight tracking airline data"""

    iataCode: Annotated[str, Field(description='Airline IATA code')]
    """str: airline IATA code"""
    icaoCode: Annotated[str, Field(description='Airline ICAO code')]
    """str: airline ICAO code"""


class AviationEdgeFlightTrackingAirport(APIBaseModel):
    """Aviation Edge API flight tracking airport data"""

    iataCode: Annotated[str, Field(description='Airport IATA code')]
    """str: airport IATA code"""
    icaoCode: Annotated[str, Field(description='Airport ICAO code')]
    """str: airport ICAO code"""


class AviationEdgeFlightTrackingFlight(APIBaseModel):
    """Aviation Edge API flight tracking flight data"""

    iataNumber: Annotated[str, Field(description='Flight IATA number')]
    """str: flight IATA number"""
    icaoNumber: Annotated[str, Field(description='Flight ICAO number')]
    """str: flight ICAO number"""
    number: Annotated[str, Field(description='Flight number')]
    """str: flight number"""


class AviationEdgeFlightTrackingGeography(APIBaseModel):
    """Aviation Edge API flight tracking geography data"""

    altitude: Annotated[float, Field(description='Aircraft altitude [m]')]
    """float: aircraft altitude [m]"""
    direction: Annotated[float, Field(description='Aircraft heading [deg]')]
    """float: aircraft heading [deg]"""
    latitude: Annotated[float, Field(description='Aircraft latitude [deg]')]
    """float: aircraft latitude [deg]"""
    longitude: Annotated[float, Field(description='Aircraft longitude [deg]')]
    """float: aircraft longitude [deg]"""


class AviationEdgeFlightTrackingSpeed(APIBaseModel):
    """Aviation Edge API flight tracking speed data"""

    horizontal: Annotated[float, Field(description='Aircraft horizontal speed [km/h]')]
    """float: aircraft horizontal speed [km/h]"""
    isGround: Annotated[bool, Field(description='Whether aircraft is on ground')]
    """bool: whether aircraft is on ground"""
    vspeed: Annotated[float, Field(description='Aircraft vertical speed [km/h]')]
    """float: aircraft vertical speed"""


class AviationEdgeFlightTrackingSystem(APIBaseModel):
    """Aviation Edge API flight tracking system data"""

    squawk: Annotated[str | None, Field(description='Aircraft squawk code')]
    """str | None: aircraft squawk code"""
    updated: Annotated[int, Field(description='Aircraft squawk code update time (Unix)')]
    """int: aircraft squawk code update time (Unix)"""


class AviationEdgeFlightTrackingState(APIBaseModel):
    """Aviation Edge API flight tracking response data"""

    aircraft: Annotated[AviationEdgeFlightTrackingAircraft, Field(description='Aircraft data')]
    """AviationEdgeAircraft: aircraft data"""
    airline: Annotated[AviationEdgeFlightTrackingAirline, Field(description='Airline data')]
    """AviationEdgeAirline: airline data"""
    arrival: Annotated[AviationEdgeFlightTrackingAirport, Field(description='Arrival airport data')]
    """AviationEdgeAirport: arrival airport data"""
    departure: Annotated[AviationEdgeFlightTrackingAirport,
                         Field(description='Departure airport data')]
    """AviationEdgeAirport: departure airport data"""
    flight: Annotated[AviationEdgeFlightTrackingFlight, Field(description='Flight data')]
    """AviationEdgeFlight: flight data"""
    geography: Annotated[AviationEdgeFlightTrackingGeography,
                         Field(description='Aircraft geography data')]
    """AviationEdgeGeography: aircraft geography data"""
    speed: Annotated[AviationEdgeFlightTrackingSpeed, Field(description='Aircraft speed data')]
    """AviationEdgeSpeed: aircraft speed data"""
    status: Annotated[str, Field(description='Aircraft status')]
    """str: aircraft status"""
    system: Annotated[AviationEdgeFlightTrackingSystem, Field(description='Aircraft system data')]
    """AviationEdgeSystem: aircraft system data"""


ListModelType = TypeVar('ListModelType')


class ListModel(RootModel[list[ListModelType]], Generic[ListModelType]):
    """Generic root model containing a list of entries"""

    def __iter__(self) -> Iterator:
        """Get state iterator
        
        Returns:
            Iterator: state iterator
        """
        return iter(self.root)
    
    def __len__(self) -> int:
        """Get number of states
        
        Returns:
            int: number of states
        """
        return len(self.root)
    
    def __getitem__(self, index: int) -> ListModelType:
        """Get a state from the state list

        Args:
            index (int): index of state to get

        Returns:
            ListModelType: indexed state
        """
        return self.root[index]


class AviationEdgeFlightTrackingResponse(ListModel[AviationEdgeFlightTrackingState], APIResponse):
    """Aviation Edge API response data"""

    _time: datetime | None = None

    def model_post_init(self, _) -> None:
        """Store the time of the response validation"""
        if self._time is None:
            self._time = datetime.now(tz=timezone.utc)

    def to_states(self) -> list[State]:
        """Convert Aviation Edge API response to list of aircraft states

        Returns:
            list[State]: list of aircraft states
        """
        return [State(
            time=self._time,
            data_source=APIType.AVIATION_EDGE,
            aircraft_iata=entry.aircraft.iataCode,
            aircraft_icao=entry.aircraft.icaoCode,
            aircraft_icao24=entry.aircraft.icao24,
            aircraft_registration=entry.aircraft.regNumber,
            airline_iata=entry.airline.iataCode,
            airline_icao=entry.airline.icaoCode,
            arrival_iata=entry.arrival.iataCode,
            arrival_icao=entry.arrival.icaoCode,
            departure_iata=entry.departure.iataCode,
            departure_icao=entry.departure.icaoCode,
            flight_iata=entry.flight.iataNumber,
            flight_icao=entry.flight.icaoNumber,
            flight_number=entry.flight.number,
            position=(entry.geography.latitude, entry.geography.longitude),
            geo_altitude=None,
            baro_altitude=entry.geography.altitude,
            heading=entry.geography.direction,
            speed_horizontal=entry.speed.horizontal / 3.6,
            speed_vertical=entry.speed.vspeed / 3.6,
            is_on_ground=bool(entry.speed.isGround),
            status=StateStatus.from_string(entry.status),
            squawk=entry.system.squawk if entry.system.squawk is not None and \
                len(entry.system.squawk) else None,
            squawk_time=datetime.fromtimestamp(entry.system.updated, tz=timezone.utc)
        ) for entry in self.root]


class AviationEdgeAirport(APIBaseModel):
    """Aviation Edge API airport data"""

    GMT: Annotated[str | None, Field(description='GMT offset at airport location')]
    """str: GMT offset at airport location"""
    airportId: Annotated[int, Field(description='Aviation Edge airport ID')]
    """int: Aviation Edge airport ID"""
    codeIataAirport: Annotated[str, Field(description='Airport IATA code')]
    """str: airport IATA code"""
    codeIataCity: Annotated[str | None, Field(description='City IATA code')]
    """str: city IATA code"""
    codeIcaoAirport: Annotated[str | None, Field(description='Airport ICAO code')]
    """str | None: airport ICAO code"""
    codeIso2Country: Annotated[str | None, Field(description='Airport country ISO2 code')]
    """str: airport country ISO2 code"""
    geonameId: Annotated[int | None, Field(description='Airport Geonames ID')]
    """int: airport Geonames ID"""
    latitudeAirport: Annotated[float | None, Field(description='Airport latitude [deg]')]
    """float | None: airport latitude [deg]"""
    longitudeAirport: Annotated[float | None, Field(description='Airport longitude [deg]')]
    """float | None: airport longitude [deg]"""
    nameAirport: Annotated[str, Field(description='Airport name')]
    """str: airport name"""
    nameCountry: Annotated[str | None, Field(description='Country name')]
    """str: country name"""
    phone: Annotated[str | None, Field(description='Airport phone number')]
    """str: airport phone number"""
    timezone: Annotated[str | None, Field(description='Airport timezone name')]

    @field_validator('geonameId', mode='before')
    @classmethod
    def parse_geoname_id(cls, value: int | str | None) -> int | None:
        """Parse Geoname ID value

        Args:
            value (int | None): Geoname ID value

        Returns:
            int | None: parsed Geoname ID value
        """
        if value in ('0', 0):
            return None
        return value
    
    @field_validator('phone', mode='before')
    @classmethod
    def parse_phone(cls, value: str | None) -> str | None:
        """Parse phone number value

        Args:
            value (str | None): phone number value

        Returns:
            str | None: processed phone number
        """
        if isinstance(value, str) and not re.match(Regex.phone_number, value.strip()):
            return None
        return value
    
    @model_validator(mode='after')
    def post_process(self) -> 'AviationEdgeAirport':
        """Post process the airport data

        Returns:
            AviationEdgeAirport: post-processed airport data
        """
        # Handle missing country ISO2 code or name
        if self.codeIso2Country is None and self.nameCountry is not None:
            self.codeIso2Country = country_name_to_country_code(self.nameCountry)
        if self.nameCountry is None and self.codeIso2Country is not None:
            self.nameCountry = country_code_to_country_name(self.codeIso2Country)
        return self


class AviationEdgeAirportDatabase(ListModel[AviationEdgeAirport]):
    """Aviation Edge API airport database"""

    def to_airports(self) -> list[Airport]:
        """Convert Aviation Edge API airport database to list of airports

        Returns:
            list[Airport]: list of airports
        """
        return [Airport(
            iata=airport.codeIataAirport,
            icao=airport.codeIcaoAirport,
            name=airport.nameAirport,
            latitude=airport.latitudeAirport,
            longitude=airport.longitudeAirport,
            geoname_id=airport.geonameId,
            phone=airport.phone,
            timezone=airport.timezone,
            gmt=airport.GMT,
            city_iata=airport.codeIataCity,
            country_iso2=airport.codeIso2Country[:2],
            country_name=airport.nameCountry
        ) for airport in self.root]


class AviationEdgeAirline(APIBaseModel):
    """Aviation Edge API airline data"""

    ageFleet: Annotated[float | None, Field(description='Fleet age [years]')]
    """float | None: fleet age [years]"""
    airlineId: Annotated[int, Field(description='Aviation Edge airline ID')]
    """int: Aviation Edge airline ID"""
    callsign: Annotated[str | None, Field(description='Airline callsign')]
    """str | None: airline callsign"""
    codeHub: Annotated[str | None, Field(description='Airline hub airport IATA code')]
    """str | None: airline hub airport IATA code"""
    codeIataAirline: Annotated[str | None, Field(description='Airline IATA code')]
    """str | None: airline IATA code"""
    codeIcaoAirline: Annotated[str | None, Field(description='Airline ICAO code')]
    """str | None: airline ICAO code"""
    codeIso2Country: Annotated[str | None, Field(description='Airline country ISO2 code')]
    """str | None: airline country ISO2 code"""
    founding: Annotated[int | None, Field(description='Airline founding year')]
    """int | None: airline founding year"""
    iataPrefixAccounting: Annotated[int | None, Field(description='Airline IATA accounting prefix')]
    """int | None: airline IATA accounting prefix"""
    nameAirline: Annotated[str | None, Field(description='Airline name')]
    """str | None: airline name"""
    sizeAirline: Annotated[int | None, Field(description='Airline fleet size')]
    """int | None: airline fleet size"""
    statusAirline: Annotated[str, Field(description='Airline status')]
    """str: airline status"""
    type: Annotated[str | None, Field(description='Airline type')]
    """str | None: airline type"""

    @field_validator('iataPrefixAccounting', mode='before')
    @classmethod
    def parse_raw_value(cls, value: str | int | None) -> str:
        """Parse raw value

        Args:
            value (str | None): raw value or None

        Returns:
            str: parsed value or empty string
        """
        if isinstance(value, str):
            return None
        return value
    
    @field_validator('codeIcaoAirline', mode='after')
    @classmethod
    def parse_icao_code(cls, value: str | None) -> str | None:
        """Parse airline ICAO code value

        Args:
            value (str | None): ICAO code value

        Returns:
            str | None: parsed ICAO code
        """
        if isinstance(value, str):
            return value.replace(' ', '').replace('&', '')
        return value
    
    @field_validator('callsign', mode='after')
    @classmethod
    def parse_callsign(cls, value: str | None) -> str | None:
        """Parse airline callsign value

        Args:
            value (str | None): callsign value

        Returns:
            str | None: parsed callsign
        """
        if isinstance(value, str) and not re.match(r'[A-Z0-9\s]+', value):
            return None
        return value
    
    @field_validator('founding', mode='after')
    @classmethod
    def parse_founding(cls, value: int | None) -> int | None:
        """Parse airline founding year value

        Args:
            value (int | None): founding year value

        Returns:
            int | None: parsed founding year
        """
        if isinstance(value, int) and value == 0:
            return None
        return value
    
    @field_validator('ageFleet', mode='after')
    @classmethod
    def parse_fleet_age(cls, value: float | None) -> float | None:
        """Parse airline fleet age value

        Args:
            value (float | None): fleet age value

        Returns:
            float | None: parsed fleet age
        """
        if isinstance(value, float) and value == 0.0:
            return None
        return value
    
    @field_validator('codeHub', mode='after')
    @classmethod
    def parse_hub_iata(cls, value: str | None) -> str | None:
        """Parse airline hub IATA code value

        Args:
            value (str | None): hub IATA code value

        Returns:
            str | None: parse hub IATA code
        """
        if isinstance(value, str) and len(value) == 4:
            return None  # TODO: convert ICAO to IATA
        return value

    @model_validator(mode='after')
    def post_process(self) -> 'AviationEdgeAirline':
        """Post process the airline data

        Returns:
            AviationEdgeAirline: post-processed airline data
        """
        # Remove incorrect ICA/IATA entries
        if self.codeIataAirline is not None and self.codeIcaoAirline is not None \
            and self.codeIataAirline == 'ICA' and self.codeIcaoAirline == 'IATA':
            self.codeIataAirline, self.codeIcaoAirline = None, None
        
        # Fix swapped ICAO/IATA entries
        if self.codeIataAirline is not None and len(self.codeIataAirline) == 3 \
            and not self.codeIataAirline.endswith('*'):
            self.codeIataAirline, self.codeIcaoAirline = self.codeIcaoAirline, self.codeIataAirline

        return self


class AviationEdgeAirlineDatabase(ListModel[AviationEdgeAirline]):
    """Aviation Edge API airline database"""

    def to_airlines(self) -> list[Airline]:
        """Convert Aviation Edge airline database to list of airlines

        Returns:
            list[Airline]: list of airlines
        """
        return [Airline(
            iata=airline.codeIataAirline,
            icao=airline.codeIcaoAirline,
            name=airline.nameAirline,
            callsign=airline.callsign,
            founding=airline.founding,
            fleet_age=airline.ageFleet,
            fleet_size=airline.sizeAirline,
            status=airline.statusAirline,
            types=airline.type,
            country_iso2=airline.codeIso2Country[:2] \
                if airline.codeIso2Country is not None else None,
            hub_iata=airline.codeHub
        ) for airline in self.root]
    

class AviationEdgeAirplane(APIBaseModel):
    """Aviation Edge API airplane data"""

    airplaneIataType: Annotated[str | None, Field(description='Airplane type IATA code')]
    """str | None: airplane type IATA code"""
    airplaneId: Annotated[int, Field(description='Aviation Edge airplane ID')]
    """int: Aviation Edge airplane ID"""
    codeIataAirline: Annotated[str | None, Field(description='Airline IATA code')]
    """str | None: airline IATA code"""
    codeIataPlaneLong: Annotated[str, Field(description='Airplane IATA code (long)')]
    """str: airplane IATA code (long)"""
    codeIataPlaneShort: Annotated[str, Field(description='Airplane IATA code (short)')]
    """str: airplane IATA code (short)"""
    codeIcaoAirline: Annotated[str | None, Field(description='Airline ICAO code')]
    """str | None: airline ICAO code"""
    constructionNumber: Annotated[str | None,
                                  Field(description='Airplane manufacturer serial number')]
    """str | None: airplane manufacturer serial number"""
    deliveryDate: Annotated[datetime | None,
                            Field(description='Date aircraft was delivered to operator')]
    """datetime: date aircraft was delivered to operator"""
    enginesCount: Annotated[int | None, Field(description='Number of engines')]
    """int | None: number of engines"""
    enginesType: Annotated[str | None, Field(description='Engine type')]
    """str | None: engine type"""
    firstFlight: Annotated[datetime | None, Field(description='Date of first flight')]
    """datetime | None: date of first flight"""
    hexIcaoAirplane: Annotated[str | None, Field(description='Airplane ICAO 24-bit address (hex)')]
    """str | None: airplane ICAO 24-bit address (hex)"""
    lineNumber: Annotated[str | None, Field(description='Airplane manufacturer line number')]
    """int | None: airplane manufacturer line number"""
    modelCode: Annotated[str | None, Field(description='Airplane manufacturer model code')]
    """str | None: airplane manufacturer model code"""
    numberRegistration: Annotated[str, Field(description='Aircraft tail number/registration')]
    """str: aircraft tail number/registration"""
    numberTestRgistration: Annotated[str | None,
                                     Field(description='Test registration (before delivery)')]
    """str: test registration (before delivery)"""
    planeAge: Annotated[int | None, Field(description='Airplane age [year]')]
    """int | None: airplane age [year]"""
    planeClass: Annotated[str | None, Field(description='Airplane class')]
    """str | None: airplane class"""
    planeModel: Annotated[str, Field(description='Airplane family model')]
    """str: airplane family model"""
    planeOwner: Annotated[str | None, Field(description='Current owner of aircraft')]
    """str | None: current owner of aircraft"""
    planeSeries: Annotated[str | None, Field(description='Airplane series variant number')]
    """str | None: airplane series variant number"""
    planeStatus: Annotated[str | None, Field(description='Airplane status')]
    """str | None: airplane status"""
    productionLine: Annotated[str | None, Field(description='Airplane subfamily production line')]
    """str | None: airplane subfamily production line"""
    registrationDate: Annotated[datetime | None,
                                Field(description='Date when airplane was registered')]
    """datetime | None: date when airplane was registered"""
    rolloutDate: Annotated[datetime | None, Field(description='Date when aircraft was rolled out')]
    """datetime | None: date when aircraft was rolled out"""

    @field_validator('deliveryDate', 'firstFlight', 'registrationDate', 'rolloutDate',
                     mode='before')
    @classmethod
    def parse_date(cls, date_value: datetime | str | None) -> datetime | None:
        """Parse a date value

        Args:
            date_value (datetime | str | None): date value

        Returns:
            datetime | None: parsed date
        """
        if isinstance(date_value, str):
            if not len(date_value) or date_value == '0000-00-00':
                return None
        return date_value
    
    @field_validator('planeAge', mode='before')
    @classmethod
    def parse_integer(cls, integer_value: int | str | None) -> int | None:
        """Parse integer value

        Args:
            integer_value (int | str | None): integer value

        Returns:
            int | None: parsed integer
        """
        if isinstance(integer_value, str) and not len(integer_value):
            return None
        return integer_value
    
    @field_validator('hexIcaoAirplane', 'numberTestRgistration', mode='after')
    @classmethod
    def parse_uppercase(cls, value: str | None) -> str | None:
        """Parse string uppercase value

        Args:
            value (str | None): string value

        Returns:
            str | None: uppercase string
        """
        if isinstance(value, str):
            return value.upper()
        return value
    
    @field_validator('constructionNumber', mode='after')
    @classmethod
    def parse_serial_number(cls, value: str | None) -> str | None:
        """Parse serial number value

        Args:
            value (str | None): serial number value

        Returns:
            str | None: parsed serial number
        """
        if isinstance(value, str) and value == 'Unknown':
            return None
        return value
    
    @field_validator('planeAge', mode='after')
    @classmethod
    def parse_age(cls, value: int | None) -> int | None:
        """Parse age value

        Args:
            value (int | None): age value

        Returns:
            int | None: parsed age
        """
        if isinstance(value, int) and value > 500:
            return datetime.now(tz=timezone.utc).year - value
        return value


class AviationEdgeAirplaneDatabase(ListModel[AviationEdgeAirplane]):
    """Aviation Edge API airplane database"""

    def to_aircraft(self) -> list[Aircraft]:
        """Convert Aviation Edge airplane database to list of aircraft

        Returns:
            list[Aircraft]: list of aircraft
        """
        return [Aircraft(
            identity=AircraftIdentity(
                icao24=airplane.hexIcaoAirplane,
                registration=airplane.numberRegistration,
                test_registration=airplane.numberTestRgistration,
                owner=airplane.planeOwner,
                airline_iata=airplane.codeIataAirline,
                airline_icao=airplane.codeIcaoAirline
            ),
            model=AircraftModel(
                type_iata=airplane.airplaneIataType,
                type_iata_code_short=airplane.codeIataPlaneShort,
                type_iata_code_long=airplane.codeIataPlaneLong,
                engine_count=airplane.enginesCount,
                engine_type=airplane.enginesType,
                model_code=airplane.modelCode.strip() if airplane.modelCode is not None else None,
                line_number=airplane.lineNumber,
                serial_number=airplane.constructionNumber,
                family=airplane.planeModel,
                sub_family=airplane.productionLine,
                series=airplane.planeSeries,
                classification=airplane.planeClass
            ),
            lifecycle=AircraftLifecycle(
                date_delivery=airplane.deliveryDate,
                date_first_flight=airplane.firstFlight,
                date_registration=airplane.registrationDate,
                date_rollout=airplane.rolloutDate,
                age=airplane.planeAge
            ),
            status=airplane.planeStatus
        ) for airplane in self.root]
