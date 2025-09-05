"""State models"""
from typing import Union, NamedTuple, Literal, Optional, Callable, overload
from enum import Enum
import os
import operator

import numpy as np
import h5py



class StatePositionSource(Enum):
    """Source of state position"""
    ADSB: int = 0
    ASTERIX: int = 1
    MLAT: int = 2
    FLARM: int = 3


class StateCategory(Enum):
    """State object category"""
    NO_INFO: int = 0
    NO_ADSB_INFO: int = 1
    LIGHT: int = 2  # <15500 lbs
    SMALL: int = 3  # 15500 to 75000 lbs
    LARGE: int = 4  # 75000 to 300000 lbs
    HIGH_VORTEX_LARGE: int = 5  # such as B-757
    HEAVY: int = 6  # >300000 lbs
    HIGH_PERFORMANCE: int = 7  # >5g acceleration and 400 kts
    ROTORCRAFT: int = 8
    GLIDER: int = 9
    LIGHTER_THAN_AIR: int = 10
    PARACHUTIST: int = 11
    ULTRALIGHT: int = 12
    RESERVED: int = 13
    UNMANNED_AERIAL_VEHICLE: int = 14
    SPACE_VEHICLE: int = 15
    SURFACE_EMERGENCY_VEHICLE: int = 16
    SURFACE_SERVICE_VEHICLE: int = 17
    POINT_OBSTACLE: int = 18
    CLUSTER_OBSTACLE: int = 19
    LINE_OBSTACLE: int = 20


FieldNames = Literal['time', 'icao24', 'callsign', 'origin_country', 'time_position',
                      'last_contact', 'longitude', 'latitude', 'baro_altitude', 'on_ground',
                      'velocity', 'true_track', 'vertical_rate', 'sensors', 'geo_altitude',
                      'squawk', 'spi', 'position_source', 'category']

Operators = Literal['==', '!=', '<', '<=', '>', '>=', 'contains', 'startswith', 'endswith']


class FieldInfo(NamedTuple):
    """Field info metadata"""
    optional: bool
    data_type: str


class State:
    """Aircraft state data"""

    def __init__(self, data: np.ndarray) -> None:
        """Store state data

        Args:
            data (np.ndarray): state data
        """
        self._data: np.ndarray = data

    def __str__(self) -> str:
        """Get a string representation of this state

        Returns:
            str: state string representation
        """
        return f'State<t={self["time"]}, callsign={self["callsign"]}>'

    def __getitem__(self, field_name: FieldNames) -> Union[int, float, str, bool,
                                                            StateCategory, StatePositionSource]:
        """Get an item by field name

        Args:
            field_name (FieldNames): name of field to get

        Returns:
            Union[int, float, str, bool, StateCategory, StatePositionSource]: field value
        """
        value = self._data[field_name]

        # Strings
        if isinstance(value, np.bytes_):
            if field_name == 'sensors':
                sensors_str = value.decode('utf-8')
                if len(sensors_str):
                    return [int(x) for x in sensors_str.split(',')]
                return None
            return value.decode('utf-8').strip()

        # Integers
        if isinstance(value, np.integer):
            return int(value)

        # Bools
        if isinstance(value, np.bool_):
            return bool(value)

        # NaNs
        if np.isnan(value):
            return None

        # Floats
        return float(value)


class States:
    """Collection of aircraft states"""

    FIELDS: dict[FieldNames, FieldInfo] = {
        'time': FieldInfo(False, 'u8'),
        'icao24': FieldInfo(False, 'S6'),
        'callsign': FieldInfo(True, 'S8'),
        'origin_country': FieldInfo(False, 'S64'),
        'time_position': FieldInfo(True, 'u8'),
        'last_contact': FieldInfo(False, 'u8'),
        'longitude': FieldInfo(True, 'f8'),
        'latitude': FieldInfo(True, 'f8'),
        'baro_altitude': FieldInfo(True, 'f8'),
        'on_ground': FieldInfo(False, '?'),
        'velocity': FieldInfo(True, 'f8'),
        'true_track': FieldInfo(True, 'f8'),
        'vertical_rate': FieldInfo(True, 'f8'),
        'sensors': FieldInfo(True, 'S64'),
        'geo_altitude': FieldInfo(True, 'f8'),
        'squawk': FieldInfo(True, 'S4'),
        'spi': FieldInfo(False, '?'),
        'position_source': FieldInfo(False, 'u1'),
        'category': FieldInfo(False, 'u1')
    }
    DTYPE = np.dtype([(name, info.data_type) for name, info in FIELDS.items()])

    _data: np.ndarray
    _hdf5_dataset_name: str = 'states'

    def __init__(self,
                 data: Optional[list[dict[FieldNames, Union[str, float, int]]]] = None) -> None:
        """Initialize this state from the OpenSky API data

        Args:
            data (Optional[list[dict[FieldNames, Union[str, float, int]]]]): OpenSky API data
        """
        # Parse data if provided
        self._data = np.empty(0, dtype=self.DTYPE)
        if data is not None:
            self._data = np.empty(len(data), dtype=self.DTYPE)
            for i, s in enumerate(data):
                self._data[i] = (
                    s['time'] if s.get('time', None) is not None else 0,
                    s['icao24'].encode('utf-8') if s.get('icao24', None) is not None else b'',
                    s['callsign'].encode('utf-8') if s.get('callsign', None) is not None else b'',
                    s['origin_country'].encode('utf-8') if \
                        s.get('origin_country', None) is not None else b'',
                    s['time_position'] if s.get('time_position', None) is not None else 0,
                    s['last_contact'] if s.get('last_contact', None) is not None else 0,
                    s['longitude'] if s.get('longitude', None) is not None else np.nan,
                    s['latitude'] if s.get('latitude', None) is not None else np.nan,
                    s['baro_altitude'] if s.get('baro_altitude', None) is not None else np.nan,
                    s['on_ground'] if s.get('on_ground', None) is not None else True,
                    s['velocity'] if s.get('velocity', None) is not None else np.nan,
                    s['true_track'] if s.get('true_track', None) is not None else np.nan,
                    s['vertical_rate'] if s.get('vertical_rate', None) is not None else np.nan,
                    ','.join(str(x) for x in s['sensors']).encode('utf-8') if \
                        s.get('sensors', None) is not None else b'',
                    s['geo_altitude'] if s.get('geo_altitude', None) is not None else np.nan,
                    s['squawk'].encode('utf-8') if s.get('squawk', None) is not None else b'',
                    s['spi'] if s.get('spi', None) is not None else False,
                    s['position_source'] if s.get('position_source', None) is not None else 0,
                    s['category'] if s.get('category', None) is not None else 0,
                )

        # Iterator variable
        self._current_iter: int = 0

    def __str__(self) -> str:
        """Get string representation of states

        Returns:
            str: states string representation
        """
        return f'States<n={len(self)}>'

    def __len__(self) -> int:
        """Get number of stored states

        Returns:
            int: number of stored states
        """
        return len(self._data)

    def set_data(self, new_data: np.ndarray) -> None:
        """Set the data in the states list

        Args:
            new_data (np.ndarray): new data
        """
        self._data = new_data

    @overload
    def __getitem__(self, index: int) -> State:
        """Get a row from the states list

        Args:
            index (int): index of row to get

        Returns:
            State: selected state
        """
    @overload
    def __getitem__(self, index: slice) -> 'States':
        """Get multiple rows from the states list

        Args:
            index (slice): slice of rows to get
        Returns:
            States: selected states
        """
    @overload
    def __getitem__(self, index: FieldNames) -> np.ndarray:
        """Get a column from the states list

        Args:
            index (FieldNames): name of column to get

        Returns:
            np.ndarray: selected column
        """
    def __getitem__(self, index: Union[int, slice, np.ndarray, FieldNames]) \
        -> Union[State, 'States', np.ndarray]:
        """Get a section of the states data

        Args:
            index (Union[int, slice, np.ndarray, FieldNames]): row index/indices, or field name

        Returns:
            Union[State, States, np.ndarray]: selected row, selected rows, or selected column
        """
        # Select single state (return as State)
        if isinstance(index, (int, np.integer)):
            row = self._data[index]
            return State(row)

        # Select multiple states (return as States)
        if isinstance(index, (slice, np.ndarray)):
            rows = self._data[index]
            new_states = States()
            new_states.set_data(rows)
            return new_states

        # Select field column (return as array)
        if isinstance(index, str):
            if index not in self.FIELDS:
                raise TypeError(f'Unknown field name "{index}"')
            return self._data[index]

        raise TypeError(f'Index must be field name, integer or slice index, got {type(index)}')

    def to_hdf5(self, filename: str) -> None:
        """Save the states to an HDF5 file

        Args:
            filename (str): file to write to (if exists, append)
        """
        # Create new file
        if not os.path.exists(filename):
            with h5py.File(filename, 'w') as file:
                max_shape = (None,)  # unlimited
                file.create_dataset(self._hdf5_dataset_name, data=self._data,
                                    maxshape=max_shape, chunks=True)

        # Append to existing file
        else:
            with h5py.File(filename, 'a') as file:
                n_new = self._data.shape[0]
                dataset = file[self._hdf5_dataset_name]
                old_size = dataset.shape[0]
                dataset.resize(old_size + n_new, axis=0)
                dataset[old_size:] = self._data

    @classmethod
    def from_hdf5(cls, filename: str) -> 'States':
        """Load states from an HDF5 file

        Raises:
            FileNotFoundError: if specified file does not exist
            KeyError: if HDF5 file does not contain states data

        Args:
            filename (str): file to load from

        Returns:
            States: loaded states
        """
        # Ensure file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f'File "{filename}" not found')

        # Read in file data
        states = States()
        with h5py.File(filename, 'r') as file:
            if states._hdf5_dataset_name not in file:
                raise KeyError(f'"states" dataset not found in "{filename}"')
            states.set_data(file[states._hdf5_dataset_name][:])
        return states

    def __iter__(self) -> 'States':
        """Start iterator

        Returns:
            States: self
        """
        self._current_iter = 0
        return self

    def __next__(self) -> State:
        """Get next iteration

        Returns:
            State: current iteration
        """
        if self._current_iter >= self._data.shape[0]:
            raise StopIteration
        state = self[self._current_iter]
        self._current_iter += 1
        return state

    def select(self, *conditions: tuple[tuple[FieldNames, Operators, object]]) -> 'States':
        """Select states from the list based on one or more conditions

        Args:
            conditions (tuple[str, Operators, object]): condition with field name, operator, value

        Returns:
            States: matching states
        """
        # No conditions: return all states
        if not conditions:
            return self

        # Map string operators to callable operators
        operators: dict[Operators, Callable] = {
            '==': operator.eq,
            '!=': operator.ne,
            '<': operator.lt,
            '<=': operator.le,
            '>': operator.gt,
            '>=': operator.ge,
            'contains': lambda a, b: b in a if a is not None else False,
            'startswith': lambda a, b: a.startswith(b) if a is not None else False,
            'endswith': lambda a, b: a.endswith(b) if a is not None else False
        }
        mapped_conditions: list[tuple[FieldNames, Callable, object]] = []
        for field, operator_str, value in conditions:
            if operator_str not in operators:
                raise ValueError(f'Unsupported operator "{operator_str}"')
            mapped_conditions.append((field, operators[operator_str], value))

        # Find matching rows
        mask = np.ones(len(self._data), dtype=bool)
        for i, row in enumerate(self._data):
            state = State(row)
            match = True

            # Check each condition
            for field, operator_func, value in mapped_conditions:
                field_value = state[field]

                if field_value is None:
                    match = False
                    break
                if not operator_func(field_value, value):
                    match = False
                    break
            mask[i] = match

        # Select matched rows
        new_states = States()
        new_states.set_data(self._data[mask])
        return new_states

    def not_nan(self, *fields: FieldNames) -> 'States':
        """Get subset of states where specified fields are not NaN

        Returns:
            States: states where specified fields are not NaN
        """
        if fields is None or len(fields) == 0:
            return self

        # Create mask using NaN condition
        mask = np.ones(len(self._data), dtype=bool)
        for field in fields:
            if np.issubdtype(self._data[field].dtype, np.floating):
                mask &= ~np.isnan(self._data[field])
            elif np.issubdtype(self._data[field].dtype, np.bytes_):
                mask &= np.logical_and(self._data[field] != b'', self._data[field] != b'        ')
            else:
                mask &= self._data[field] is not None

        # Select masked rows
        new_states = States()
        new_states.set_data(self._data[mask])
        return new_states
