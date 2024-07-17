from collections import namedtuple
from typing import Dict, Set, Union

from unix_perms.exceptions import InvalidOctalError

OctalConfig = namedtuple('OctalConfig', ['description', 'read', 'write', 'execute'])

VALID_OCTAL_DIGITS: Set[str] = {str(num) for num in range(8)}

OCTAL_MODE_DIGIT_0 = OctalConfig(description='No permissions', read=False, write=False, execute=False)
OCTAL_MODE_DIGIT_1 = OctalConfig(description='Execute permission only', read=False, write=False, execute=True)
OCTAL_MODE_DIGIT_2 = OctalConfig(description='Write permission only', read=False, write=True, execute=False)
OCTAL_MODE_DIGIT_3 = OctalConfig(description='Write and execute permissions', read=False, write=True, execute=True)
OCTAL_MODE_DIGIT_4 = OctalConfig(description='Read permission only', read=True, write=False, execute=False)
OCTAL_MODE_DIGIT_5 = OctalConfig(description='Read and execute permissions', read=True, write=False, execute=True)
OCTAL_MODE_DIGIT_6 = OctalConfig(description='Read and write permissions', read=True, write=True, execute=False)
OCTAL_MODE_DIGIT_7 = OctalConfig(description='Read, write, and execute permissions', read=True, write=True, execute=True)

OCTAL_DIGIT_CONFIGS: Dict[int, OctalConfig] = {
    0: OCTAL_MODE_DIGIT_0,
    1: OCTAL_MODE_DIGIT_1,
    2: OCTAL_MODE_DIGIT_2,
    3: OCTAL_MODE_DIGIT_3,
    4: OCTAL_MODE_DIGIT_4,
    5: OCTAL_MODE_DIGIT_5,
    6: OCTAL_MODE_DIGIT_6,
    7: OCTAL_MODE_DIGIT_7
}

def _get_octal_digit_config(octal_digit: int) -> OctalConfig:
    """
    Private function to retrieve an OctalConfig object for a given octal digit.
    """
    if 0 <= octal_digit <= 7:
        return OCTAL_DIGIT_CONFIGS.get(octal_digit)
    else:
        raise InvalidOctalError(
            "an integer representation of an octal digit must be a single digit ranging from 0 to 7"
        )


def from_octal_digit_to_config(octal_digit: Union[str, int]) -> OctalConfig:
    """
    Given an octal digit, will return an OctalConfig object.

    Args:
        octal_digit (int): An integer octal digit, ranging from 0 to 7.

    Returns:
        OctalConfig: A named tuple containing basic permissions info for the digit.

    """
    if not isinstance(octal_digit, (str, int)):
        raise TypeError(f"{type(octal_digit)} is not a valid 'octal_digit' type")

    if isinstance(octal_digit, str):
        try:
            octal_digit = int(octal_digit)
        except ValueError:
            raise InvalidOctalError(
                "expecting a string representation of an integer octal digit"
            )

    octal_config = _get_octal_digit_config(octal_digit=octal_digit)
    return octal_config


def _octal_validation(octal: str) -> str:
    """
    Private function to validate and convert a string Unix permissions mode to a three digit mode.
    """
    octal_string_length: int = len(octal)

    if not 1 <= octal_string_length <= 3:
        raise InvalidOctalError(
            'invalid octal representation length, must have a length ranging from 0 to 3'
        )

    any_invalid_digits: bool = any(digit not in VALID_OCTAL_DIGITS for digit in octal)
    if any_invalid_digits:
        raise InvalidOctalError(
            'invalid digits in octal representation, digits must range from 0 to 7'
        )

    octal_int_string_repr: str = octal.zfill(3)
    return octal_int_string_repr


def _from_decimal_to_permissions_mode(octal: int) -> str:
    """
    Private function to convert a decimal representation of an octal
    to a three digit string Unix permissions mode.
    """
    octal_string: str = format(octal, 'o')
    octal_int_string_repr: str = _octal_validation(octal=octal_string)
    return octal_int_string_repr


def from_octal_to_permissions_mode(octal: Union[str, int]) -> str:
    """
    Creates a Unix permissions mode from an octal representation.

    This function accepts either a string or an integer as input. If the argument is
    a string, the value must be either in the format of an octal literal (e.g., '0o777')
    or as a Unix permissions mode (e.g., '777'). If the value is an integer, it must be a
    decimal representation of an octal as an octal literal (e.g., 0o777) or directly as an
    integer (e.g., 511).

    Args:
        octal (str | int): An octal representation as a string or integer.

    Returns:
        str: A string representation of a Unix permissions mode.
    """
    if not isinstance(octal, (str, int)):
        raise TypeError(
            f"{type(octal)} is not a valid 'octal' type, must be of type ('str', 'int')"
        )

    if isinstance(octal, str):
        int_base = 10
        message = "must be a valid decimal representation of an octal"

        if octal.startswith('0o'):
            int_base = 8
            message = "must be a valid octal literal"

        try:
            octal_as_int = int(octal, int_base)
        except ValueError:
            raise InvalidOctalError(message)
        else:
            octal_as_str = str(octal_as_int)
            permissions_mode: str = _octal_validation(octal=octal_as_str)
            return permissions_mode
    else:
        permissions_mode: str = _from_decimal_to_permissions_mode(octal=octal)
        return permissions_mode


def is_permissions_mode(octal: str) -> bool:
    """
    A boolean function which determines if an octal representation is a valid Unix permissions mode.

    This function accepts either a string or an integer as input. If the argument is
    a string, the value must be either in the format of an octal literal (e.g., '0o777')
    or as a Unix permissions mode (e.g., '777'). If the value is an integer, it must be a
    decimal representation of an octal as an octal literal (e.g., 0o777) or directly as an
    integer (e.g., 511).

    Args:
        octal (str | int): An octal representation as a string or integer.

    Returns:
        bool: A boolean indicating whether the octal is a Unix permissions mode.
    """
    try:
        _ = from_octal_to_permissions_mode(octal=octal)
        is_perms_mode = True
    except InvalidOctalError:
        is_perms_mode = False
    return is_perms_mode
