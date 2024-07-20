"""
Validator functions for th
"""
import re
from rut_chile import rut_chile


def validate_chilean_phone_number(number):
    """
    Validates a Chilean phone number.
    """
    if not re.match(r"^\+?56 \d{1} \d{4} \d{4}$", number):
        raise ValueError("phone must be in the format '+56 X XXXX XXXX'.")
    return number


def validate_rut(rut):
    """
    Validates a Chilean RUT.
    """
    if not re.match(r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$", rut):
        raise ValueError("rut must be in the format 'XX.XXX.XXX-X'.")
    if not rut_chile.is_valid_rut(rut.upper()):
        raise ValueError("rut is not valid.")
    return rut
