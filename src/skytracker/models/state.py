"""State models"""
from typing import Optional, List, Literal, Any, ClassVar, get_args
from dataclasses import dataclass, field
from enum import Enum


class StatePositionSource(Enum):
    """Source of state position."""
    ADSB: int = 0
    """ADS-B."""
    ASTERIX: int = 1
    """ASTERIX."""
    MLAT: int = 2
    """MLAT."""
    FLARM: int = 3
    """FLARM."""


class StateCategory(Enum):
    """State object category."""
    NO_INFO: int = 0
    """No information at all."""
    NO_ADSB_INFO: int = 1
    """No ADS-B emitter category information."""
    LIGHT: int = 2
    """Light (< 15500 lbs)."""
    SMALL: int = 3
    """Small (15500 to 75000 lbs)."""
    LARGE: int = 4
    """Large (75000 to 300000 lbs)."""
    HIGH_VORTEX_LARGE: int = 5
    """High vortex large (such as B-757)."""
    HEAVY: int = 6
    """Heavy (> 300000 lbs)."""
    HIGH_PERFORMANCE: int = 7
    """High performance (> 5g acceleration and 400 kts)."""
    ROTORCRAFT: int = 8
    """Rotorcraft."""
    GLIDER: int = 9
    """Glider / sailplane."""
    LIGHTER_THAN_AIR: int = 10
    """Lighter-than-air."""
    PARACHUTIST: int = 11
    """Parachutist / skydiver."""
    ULTRALIGHT: int = 12
    """Ultralight / hang-glider / paraglider."""
    RESERVED: int = 13
    """Reserved."""
    UNMANNED_AERIAL_VEHICLE: int = 14
    """Unmanned aerial vehicle (UAV)."""
    SPACE_VEHICLE: int = 15
    """Space / trans-atmospheric vehicle."""
    SURFACE_EMERGENCY_VEHICLE: int = 16
    """Surface emergency vehicle."""
    SURFACE_SERVICE_VEHICLE: int = 17
    """Surface service vehicle."""
    POINT_OBSTACLE: int = 18
    """Point obstacle (includes tethered balloons)."""
    CLUSTER_OBSTACLE: int = 19
    """Cluster obstacle."""
    LINE_OBSTACLE: int = 20
    """Line obstacle."""


StateFields = Literal['time', 'icao24', 'callsign', 'origin_country', 'time_position',
                      'last_contact', 'longitude', 'latitude', 'baro_altitude', 'on_ground',
                      'velocity', 'true_track', 'vertical_rate', 'sensors', 'geo_altitude',
                      'squawk', 'spi', 'position_source', 'category']


@dataclass
class State:
    """Aircraft state."""

    time: int
    """Unix timestamp for this state."""
    icao24: str
    """Unique ICAO 24-bit address of the transponder in hex string representation."""
    callsign: Optional[str]
    """Callsign of the vehicle (8 characters). Can be null if no callsign has been received."""
    origin_country: str
    """Country name inferred from the ICAO 24-bit address."""
    time_position: Optional[int]
    """Unix timestamp for last position update. Can be null if no position received for past 15s."""
    last_contact: int
    """Unix timestamp for last update in general. Updated for any valid message from transponder."""
    longitude: Optional[float]
    """WGS-84 latitude in decimal degrees. Can be null."""
    latitude: Optional[float]
    """WGS-84 longitude in decimal degrees. Can be null."""
    baro_altitude: Optional[float]
    """Barometric altitude in meters. Can be null."""
    on_ground: bool
    """Whether position was retrieved from a surface position report."""
    velocity: Optional[float]
    """Velocity over ground in m/s. Can be null."""
    true_track: Optional[float]
    """True track in decimal degrees clockwise from north (=0 deg). Can be null."""
    vertical_rate: Optional[float]
    """Vertical rate in m/s. Positive is climbing, negative is descending. Can be null."""
    geo_altitude: Optional[float]
    """Geometric altitude in meters. Can be null."""
    squawk: Optional[str]
    """The transponder code (squawk). Can be null."""
    spi: bool
    """Whether flight status indicates special purpose."""
    position_source: StatePositionSource
    """Origin of the position information."""
    category: StateCategory
    """Object category."""
    sensors: List[int] = field(default_factory=list)
    """IDs of the receivers which contributed to this state. Null if no sensor filter requested."""

    FIELDS: ClassVar[tuple[str, ...]] = get_args(StateFields)
    """Names of fields present in state object"""

    def to_json(self) -> dict[StateFields, Any]:
        """Get state as JSON dictionary

        Returns:
            dict[StateFields, Any]: state as JSON dictionary
        """
        return {
            'time': self.time,
            'icao24': self.icao24,
            'callsign': self.callsign,
            'origin_country': self.origin_country,
            'time_position': self.time_position,
            'last_contact': self.last_contact,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'baro_altitude': self.baro_altitude,
            'on_ground': 1 if self.on_ground else 0,
            'velocity': self.velocity,
            'true_track': self.true_track,
            'vertical_rate': self.vertical_rate,
            'sensors': self.sensors,
            'geo_altitude': self.geo_altitude,
            'squawk': self.squawk,
            'spi': 1 if self.spi else 0,
            'position_source': self.position_source.value,
            'category': self.category.value
        }
    
    @classmethod
    def from_raw(cls, raw: list[Any]) -> 'State':
        """Populate aircraft state object from raw data

        Args:
            raw (list[Any]): raw data

        Returns:
            State: parsed state object
        """
        # Decode strings where necessary
        raw = list(raw)
        for i in range(len(raw)):
            if isinstance(raw[i], bytes):
                raw[i] = raw[i].decode('utf-8')
        
        # Transform raw list into raw dictionary
        raw: dict[StateFields, Any] = dict(zip(cls.FIELDS, raw))

        # Clean up specific fields
        callsign = raw['callsign']
        if callsign is not None and callsign in ('', '        '):
            callsign = None
        elif callsign is not None:
            callsign = f'{callsign:<8}'[:8]
        sensors = raw['sensors']
        if sensors is None:
            sensors = []
        squawk = raw['squawk']
        if squawk is not None and squawk in ('',):
            squawk = None

        # Create state
        return cls(
            time=raw['time'],
            icao24=f"{raw['icao24']:<6}"[:6],
            callsign=callsign,
            origin_country=raw['origin_country'],
            time_position=raw['time_position'],
            last_contact=raw['last_contact'],
            longitude=raw['longitude'],
            latitude=raw['latitude'],
            baro_altitude=raw['baro_altitude'],
            on_ground=raw['on_ground'],
            velocity=raw['velocity'],
            true_track=raw['true_track'],
            vertical_rate=raw['vertical_rate'],
            geo_altitude=raw['geo_altitude'],
            squawk=squawk,
            spi=raw['spi'],
            position_source=StatePositionSource(raw['position_source']),
            category=StateCategory(raw['category']),
            sensors=sensors
        )


# FieldNames = Literal['time', 'icao24', 'callsign', 'origin_country', 'time_position',
#                       'last_contact', 'longitude', 'latitude', 'baro_altitude', 'on_ground',
#                       'velocity', 'true_track', 'vertical_rate', 'sensors', 'geo_altitude',
#                       'squawk', 'spi', 'position_source', 'category']

# Operators = Literal['==', '!=', '<', '<=', '>', '>=', 'contains', 'startswith', 'endswith']


# class FieldInfo(NamedTuple):
#     """Field info metadata"""
#     optional: bool
#     data_type: str


# class State:
#     """Aircraft state data"""

#     def __init__(self, data: np.ndarray) -> None:
#         """Store state data

#         Args:
#             data (np.ndarray): state data
#         """
#         self._data: np.ndarray = data

#     def __str__(self) -> str:
#         """Get a string representation of this state

#         Returns:
#             str: state string representation
#         """
#         return f'State<t={self["time"]}, callsign={self["callsign"]}>'

#     def __getitem__(self, field_name: FieldNames) -> Union[int, float, str, bool,
#                                                             StateCategory, StatePositionSource]:
#         """Get an item by field name

#         Args:
#             field_name (FieldNames): name of field to get

#         Returns:
#             Union[int, float, str, bool, StateCategory, StatePositionSource]: field value
#         """
#         value = self._data[field_name]

#         # Strings
#         if isinstance(value, np.bytes_):
#             if field_name == 'sensors':
#                 sensors_str = value.decode('utf-8')
#                 if len(sensors_str):
#                     return [int(x) for x in sensors_str.split(',')]
#                 return None
#             return value.decode('utf-8').strip()

#         # Integers
#         if isinstance(value, np.integer):
#             return int(value)

#         # Bools
#         if isinstance(value, np.bool_):
#             return bool(value)

#         # NaNs
#         if np.isnan(value):
#             return None

#         # Floats
#         return float(value)


# class States:
#     """Collection of aircraft states"""

#     FIELDS: dict[FieldNames, FieldInfo] = {
#         'time': FieldInfo(False, 'u8'),
#         'icao24': FieldInfo(False, 'S6'),
#         'callsign': FieldInfo(True, 'S8'),
#         'origin_country': FieldInfo(False, 'S64'),
#         'time_position': FieldInfo(True, 'u8'),
#         'last_contact': FieldInfo(False, 'u8'),
#         'longitude': FieldInfo(True, 'f8'),
#         'latitude': FieldInfo(True, 'f8'),
#         'baro_altitude': FieldInfo(True, 'f8'),
#         'on_ground': FieldInfo(False, '?'),
#         'velocity': FieldInfo(True, 'f8'),
#         'true_track': FieldInfo(True, 'f8'),
#         'vertical_rate': FieldInfo(True, 'f8'),
#         'sensors': FieldInfo(True, 'S64'),
#         'geo_altitude': FieldInfo(True, 'f8'),
#         'squawk': FieldInfo(True, 'S4'),
#         'spi': FieldInfo(False, '?'),
#         'position_source': FieldInfo(False, 'u1'),
#         'category': FieldInfo(False, 'u1')
#     }
#     DTYPE = np.dtype([(name, info.data_type) for name, info in FIELDS.items()])

#     _data: np.ndarray
#     _hdf5_dataset_name: str = 'states'

#     def __init__(self,
#                  data: Optional[list[dict[FieldNames, Union[str, float, int]]]] = None) -> None:
#         """Initialize this state from the OpenSky API data

#         Args:
#             data (Optional[list[dict[FieldNames, Union[str, float, int]]]]): OpenSky API data
#         """
#         # Parse data if provided
#         self._data = np.empty(0, dtype=self.DTYPE)
#         if data is not None:
#             self._data = np.empty(len(data), dtype=self.DTYPE)
#             for i, s in enumerate(data):
#                 self._data[i] = (
#                     s['time'] if s.get('time', None) is not None else 0,
#                     s['icao24'].encode('utf-8') if s.get('icao24', None) is not None else b'',
#                     s['callsign'].encode('utf-8') if s.get('callsign', None) is not None else b'',
#                     s['origin_country'].encode('utf-8') if \
#                         s.get('origin_country', None) is not None else b'',
#                     s['time_position'] if s.get('time_position', None) is not None else 0,
#                     s['last_contact'] if s.get('last_contact', None) is not None else 0,
#                     s['longitude'] if s.get('longitude', None) is not None else np.nan,
#                     s['latitude'] if s.get('latitude', None) is not None else np.nan,
#                     s['baro_altitude'] if s.get('baro_altitude', None) is not None else np.nan,
#                     s['on_ground'] if s.get('on_ground', None) is not None else True,
#                     s['velocity'] if s.get('velocity', None) is not None else np.nan,
#                     s['true_track'] if s.get('true_track', None) is not None else np.nan,
#                     s['vertical_rate'] if s.get('vertical_rate', None) is not None else np.nan,
#                     ','.join(str(x) for x in s['sensors']).encode('utf-8') if \
#                         s.get('sensors', None) is not None else b'',
#                     s['geo_altitude'] if s.get('geo_altitude', None) is not None else np.nan,
#                     s['squawk'].encode('utf-8') if s.get('squawk', None) is not None else b'',
#                     s['spi'] if s.get('spi', None) is not None else False,
#                     s['position_source'] if s.get('position_source', None) is not None else 0,
#                     s['category'] if s.get('category', None) is not None else 0,
#                 )

#         # Iterator variable
#         self._current_iter: int = 0

#     def __str__(self) -> str:
#         """Get string representation of states

#         Returns:
#             str: states string representation
#         """
#         return f'States<n={len(self)}>'

#     def __len__(self) -> int:
#         """Get number of stored states

#         Returns:
#             int: number of stored states
#         """
#         return len(self._data)

#     def set_data(self, new_data: np.ndarray) -> None:
#         """Set the data in the states list

#         Args:
#             new_data (np.ndarray): new data
#         """
#         self._data = new_data

#     @overload
#     def __getitem__(self, index: int) -> State:
#         """Get a row from the states list

#         Args:
#             index (int): index of row to get

#         Returns:
#             State: selected state
#         """
#     @overload
#     def __getitem__(self, index: slice) -> 'States':
#         """Get multiple rows from the states list

#         Args:
#             index (slice): slice of rows to get
#         Returns:
#             States: selected states
#         """
#     @overload
#     def __getitem__(self, index: FieldNames) -> np.ndarray:
#         """Get a column from the states list

#         Args:
#             index (FieldNames): name of column to get

#         Returns:
#             np.ndarray: selected column
#         """
#     def __getitem__(self, index: Union[int, slice, np.ndarray, FieldNames]) \
#         -> Union[State, 'States', np.ndarray]:
#         """Get a section of the states data

#         Args:
#             index (Union[int, slice, np.ndarray, FieldNames]): row index/indices, or field name

#         Returns:
#             Union[State, States, np.ndarray]: selected row, selected rows, or selected column
#         """
#         # Select single state (return as State)
#         if isinstance(index, (int, np.integer)):
#             row = self._data[index]
#             return State(row)

#         # Select multiple states (return as States)
#         if isinstance(index, (slice, np.ndarray)):
#             rows = self._data[index]
#             new_states = States()
#             new_states.set_data(rows)
#             return new_states

#         # Select field column (return as array)
#         if isinstance(index, str):
#             if index not in self.FIELDS:
#                 raise TypeError(f'Unknown field name "{index}"')
#             return self._data[index]

#         raise TypeError(f'Index must be field name, integer or slice index, got {type(index)}')

#     def to_hdf5(self, filename: str) -> None:
#         """Save the states to an HDF5 file

#         Args:
#             filename (str): file to write to (if exists, append)
#         """
#         # Create new file
#         if not os.path.exists(filename):
#             with h5py.File(filename, 'w', libver='latest') as file:
#                 max_shape = (None,)  # unlimited
#                 dataset = file.create_dataset(self._hdf5_dataset_name, data=self._data,
#                                     maxshape=max_shape, chunks=True)
#                 dataset.flush()
#                 file.swmr_mode = True  # single writer-multiple reader mode

#         # Append to existing file
#         else:
#             with h5py.File(filename, 'a', libver='latest') as file:
#                 file.swmr_mode = True
#                 n_new = self._data.shape[0]
#                 dataset = file[self._hdf5_dataset_name]
#                 old_size = dataset.shape[0]
#                 dataset.resize(old_size + n_new, axis=0)
#                 dataset[old_size:] = self._data
#                 dataset.flush()

#     @classmethod
#     def from_hdf5(cls, filename: str) -> 'States':
#         """Load states from an HDF5 file

#         Raises:
#             FileNotFoundError: if specified file does not exist
#             KeyError: if HDF5 file does not contain states data

#         Args:
#             filename (str): file to load from

#         Returns:
#             States: loaded states
#         """
#         # Ensure file exists
#         if not os.path.exists(filename):
#             raise FileNotFoundError(f'File "{filename}" not found')

#         # Read in file data
#         states = States()
#         with h5py.File(filename, 'r', libver='latest', swmr=True) as file:
#             if states._hdf5_dataset_name not in file:
#                 raise KeyError(f'"states" dataset not found in "{filename}"')
#             states.set_data(file[states._hdf5_dataset_name][:])
#         return states

#     def __iter__(self) -> 'States':
#         """Start iterator

#         Returns:
#             States: self
#         """
#         self._current_iter = 0
#         return self

#     def __next__(self) -> State:
#         """Get next iteration

#         Returns:
#             State: current iteration
#         """
#         if self._current_iter >= self._data.shape[0]:
#             raise StopIteration
#         state = self[self._current_iter]
#         self._current_iter += 1
#         return state

#     def select(self, *conditions: tuple[tuple[FieldNames, Operators, object]]) -> 'States':
#         """Select states from the list based on one or more conditions

#         Args:
#             conditions (tuple[str, Operators, object]): condition with field name, operator, value

#         Returns:
#             States: matching states
#         """
#         # No conditions: return all states
#         if not conditions:
#             return self

#         # Map string operators to callable operators
#         operators: dict[Operators, Callable] = {
#             '==': operator.eq,
#             '!=': operator.ne,
#             '<': operator.lt,
#             '<=': operator.le,
#             '>': operator.gt,
#             '>=': operator.ge,
#             'contains': lambda a, b: b in a if a is not None else False,
#             'startswith': lambda a, b: a.startswith(b) if a is not None else False,
#             'endswith': lambda a, b: a.endswith(b) if a is not None else False
#         }
#         mapped_conditions: list[tuple[FieldNames, Callable, object]] = []
#         for field, operator_str, value in conditions:
#             if operator_str not in operators:
#                 raise ValueError(f'Unsupported operator "{operator_str}"')
#             mapped_conditions.append((field, operators[operator_str], value))

#         # Find matching rows
#         mask = np.ones(len(self._data), dtype=bool)
#         for i, row in enumerate(self._data):
#             state = State(row)
#             match = True

#             # Check each condition
#             for field, operator_func, value in mapped_conditions:
#                 field_value = state[field]

#                 if field_value is None:
#                     match = False
#                     break
#                 if not operator_func(field_value, value):
#                     match = False
#                     break
#             mask[i] = match

#         # Select matched rows
#         new_states = States()
#         new_states.set_data(self._data[mask])
#         return new_states

#     def not_nan(self, *fields: FieldNames) -> 'States':
#         """Get subset of states where specified fields are not NaN

#         Returns:
#             States: states where specified fields are not NaN
#         """
#         if fields is None or len(fields) == 0:
#             return self

#         # Create mask using NaN condition
#         mask = np.ones(len(self._data), dtype=bool)
#         for field in fields:
#             if np.issubdtype(self._data[field].dtype, np.floating):
#                 mask &= ~np.isnan(self._data[field])
#             elif np.issubdtype(self._data[field].dtype, np.bytes_):
#                 mask &= np.logical_and(self._data[field] != b'', self._data[field] != b'        ')
#             else:
#                 mask &= self._data[field] is not None

#         # Select masked rows
#         new_states = States()
#         new_states.set_data(self._data[mask])
#         return new_states
