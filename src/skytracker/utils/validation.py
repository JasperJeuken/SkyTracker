"""String validation module"""
from re import match


class Regex:
    """Common regular expressions"""

    aircraft_registration: str = r'^[A-Z0-9]{1,4}-?[A-Z0-9]{2,5}(-?[A-Z]{1,3})?$'
    """str: regular expression for aircraft registration"""
    aircraft_registration_wildcard: str = r'^[A-Z0-9\_\-\.]+$'
    """str: regular expresion for aircraft registration supporting wildcards"""
    aircraft_icao24: str = r'^[0-9A-Fa-f]{6}$'
    """str: regular expression for aircraft ICAO 24-bit address (hex)"""
    aircraft_icao24_wildcard: str = r'^[A-Z0-9\_\.]{1,6}$'
    """str: regular expression for aircraft ICAO 24-bit address (hex) supporting wildcards"""
    aircraft_callsign: str = r'^[A-Z0-9]{1,10}$'
    """str: regular expression for aircraft callsign"""
    aircraft_callsign_wildcard: str = r'^[A-Z0-9\_\.]{1,10}$'
    """str: regular expression for aircraft callsign supporting wildcards"""
    aircraft_model: str = r'^[A-Z0-9]{3,4}$'
    """str: regular expression for aircraft model code"""
    aircraft_model_wildcard: str = r'^[A-Z0-9\_\.]{1,4}$'
    """str: regular expression for aircraft model code supporting wildcards"""
    transponder_squawk: str = r'^[0-9]{1,4}$'
    """str: regular expression for transponder squawk code"""
    transponder_squawk_wildcard: str = r'^[0-9\_\.]{1,4}$'
    """str: regular expression for transponder squawk code supporting wildcards"""
    code_2: str = r'^[A-Z0-9]{2}$'
    """str: regular expression for 2-character alphanumeric code"""
    code_2_wildcard: str = r'^[A-Z0-9\_\.]{1,2}$'
    """str: regular expression for 2-character alphanumeric code supporting wildcards"""
    code_3: str = r'^[A-Z0-9]{3}$'
    """str: regular expression for 3-character alphanumeric code"""
    code_3_wildcard: str = r'^[A-Z0-9\_\.]{1,3}$'
    """str: regular expression for 3-character alphanumeric code supporting wildcards"""
    code_4: str = r'^[A-Z0-9]{4}$'
    """str: regular expression for 4-character alphanumeric code"""
    code_4_wildcard: str = r'^[A-Z0-9\_\.]{1,4}$'
    """str: regular expression for 4-character alphanumeric code supporting wildcards"""
    alphanumeric: str = r'^[a-zA-Z0-9]+$'
    """str: regular expression for alphanumeric text"""
    alphanumeric_wildcard: str = r'^[a-zA-Z0-9\_\.]+$'
    """str: regular expression for alphanumeric text supporting wildcards"""
    alphanumeric_spaces: str = r'^[a-zA-Z0-9\s]+$'
    """str: regular expression for alphanumeric text with spaces"""
    alphanumeric_spaces_wildcard: str = r'^[a-zA-Z0-9\s\_\.]+$'
    """str: regular expression for alphanumeric text with spaces supporting wildcards"""
    phone_number: str = r'^\(?\+?\d{1,3}?\)?[\s-]?(?:\(0\))?(?:\(?\d+\)?[\s-]?|\w+[\s-]?)+$'
    """str: regular expression for (international) phone numbers"""
