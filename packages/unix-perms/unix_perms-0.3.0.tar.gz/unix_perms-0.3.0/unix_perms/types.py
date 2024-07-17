from typing import Dict, Literal, Union

from pydantic import BaseModel

from unix_perms.octals import (OctalConfig, from_octal_digit_to_config,
                               from_octal_to_permissions_mode)
from unix_perms.permissions import OctalPermissions
from unix_perms.utils import get_all_class_parameters


class PermissionsConfig(BaseModel):
    """
    File permissions configuration for an octal digit. Can specify whether
    read, write, and execute permissions should be allowed.

    Args:
        read (bool): A boolean indicating whether read permission is included.
        write (bool): A boolean indicating whether write permission is included.
        execute (bool): A boolean indicating whether execute permission is included.
    """
    read: bool = False
    write: bool = False
    execute: bool = False

    @classmethod
    def from_octal_digit(cls, octal_digit: Union[str, int]) -> 'PermissionsConfig':
        """
        Creates a PermissionsConfig instance from an octal digit.

        Args:
            octal_digit (str | int): A string or integer octal digit, ranging from 0 to 7.

        Returns:
            PermissionsConfig: A new instance of PermissionsConfig corresponding to the octal digit.
        """
        octal_config: OctalConfig = from_octal_digit_to_config(octal_digit=octal_digit)
        return cls(
            read=octal_config.read, write=octal_config.write, execute=octal_config.execute
        )


class PermissionsByte:
    """
    A simple structure representing a Unix permissions byte for one of any
    of the following authorites: ('owner', 'group', 'others').

    Args:
        authority (Literal['owner', 'group', 'others']): A specific permissions authority.
        config (PermissionsConfig): A file permissions configuration for an octal digit.
    """
    def __init__(
        self,
        authority: Literal['owner', 'group', 'others'],
        config: PermissionsConfig = PermissionsConfig()
    ):
        self.authority = authority
        self._config = config

        # Set permissions for specific authority
        self.permissions = OctalPermissions(authority=self.authority)

    def __add__(self, permission_byte: 'PermissionsByte') -> 'PermissionsMode':
        if not isinstance(permission_byte, PermissionsByte):
            raise TypeError(
                f'can only add PermissionsByte (not "{type(permission_byte)}") to PermissionsByte'
            )

        return PermissionsMode._from_permissions_bytes(
            permissions_byte_one=self, permissions_byte_two=permission_byte
        )

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__} authority={self.authority} '
            f'permissions_mode={self.permissions_mode}>'
        )

    @property
    def read_permission(self) -> bool:
        """A boolean indicating whether read permission is included."""
        return self._config.read

    @property
    def write_permission(self) -> bool:
        """A boolean indicating whether write permission is included."""
        return self._config.write

    @property
    def execute_permission(self) -> bool:
        """A boolean indicating whether execute permission is included."""
        return self._config.execute

    @property
    def permissions_mode(self) -> str:
        """The Unix permissions mode."""
        base_permissions = self.permissions.no_permissions
        if self._config.read:
            base_permissions |= self.permissions.read

        if self._config.write:
            base_permissions |= self.permissions.write

        if self._config.execute:
            base_permissions |= self.permissions.execute

        return format(base_permissions, 'o').zfill(3)

    @property
    def permissions_description(self) -> str:
        """A string description of the Unix permissions mode."""
        permissions_mode = self.permissions_mode.strip('0')
        permissions_mode = permissions_mode or 0
        permissions_mode = int(permissions_mode)
        octal_config: OctalConfig = from_octal_digit_to_config(octal_digit=permissions_mode)
        return octal_config.description

    @property
    def permissions_description_detailed(self) -> Dict[str, Union[str, bool]]:
        """A more detailed description of the Unix permissions mode, as a dict."""
        return {
            'authority': self.authority,
            'mode': self.permissions_mode,
            'read': self.read_permission,
            'write': self.write_permission,
            'execute': self.execute_permission
        }

    @property
    def permissions_mode_as_decimal_repr(self) -> int:
        """The decimal representation of the Unix permissions mode"""
        return int(self.permissions_mode, 8)

    @property
    def permissions_mode_as_int(self) -> int:
        """The integer representation of the Unix permissions mode"""
        return int(self.permissions_mode)

    @property
    def permissions_mode_as_octal_literal(self) -> str:
        """The string octal literal representation of the Unix permissions mode."""
        return f'0o{self.permissions_mode}'


class PermissionsMode:
    """
    A simple structure representing a full Unix permissions mode, including all
    of the following authorites: ('owner', 'group', 'others').

    Args:
        owner (PermissionsByte): A PermissionsByte instance for the owner authority.
        group (PermissionsByte): A PermissionsByte instance for the group authority.
        others (PermissionsByte): A PermissionsByte instance for the others authority.
    """
    def __init__(
        self,
        owner: PermissionsByte,
        group: PermissionsByte,
        others: PermissionsByte
    ):
        self.owner = owner
        self.group = group
        self.others = others

    def __sub__(self, permission_byte: PermissionsByte) -> 'PermissionsMode':
        if not isinstance(permission_byte, PermissionsByte):
            raise TypeError(
                f'can only subtract PermissionsByte (not "{type(permission_byte)}") from PermissionsMode'
            )

        permissions_mode: int = self.permissions_mode_as_decimal_repr
        permissions_mode_updated: int = (
            permissions_mode & ~permission_byte.permissions_mode_as_decimal_repr
        )
        class_arguments: Dict[str, PermissionsByte] = PermissionsMode.__transform_permission_mode(
            permissions_mode_updated=permissions_mode_updated
        )

        return PermissionsMode(**class_arguments)

    def __add__(self, permission_byte: PermissionsByte) -> 'PermissionsMode':
        if not isinstance(permission_byte, PermissionsByte):
            raise TypeError(
                f'can only add PermissionsByte (not "{type(permission_byte)}") to PermissionsMode'
            )

        permissions_mode: int = self.permissions_mode_as_decimal_repr
        permissions_mode_updated: int = (
            permissions_mode | permission_byte.permissions_mode_as_decimal_repr
        )
        class_arguments: Dict[str, PermissionsByte] = PermissionsMode.__transform_permission_mode(
            permissions_mode_updated=permissions_mode_updated
        )

        return PermissionsMode(**class_arguments)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__} permissions_mode={self.permissions_mode}>'
        )

    @staticmethod
    def __transform_permission_mode(permissions_mode_updated: int) -> Dict[str, PermissionsByte]:
        """
        Private static method to take the decimal representation of a transformed permissions
        mode from __add__ or __sub__, convert to the Unix permissions mode, and generate
        updated class arguments for a new PermissionsMode instance.
        """
        permission_mode: str = from_octal_to_permissions_mode(octal=permissions_mode_updated)
        class_arguments: Dict[str, PermissionsByte] = PermissionsMode.__generate_class_arguments_from_mode(
            permission_mode=permission_mode
        )
        return class_arguments

    @staticmethod
    def __generate_class_arguments_from_mode(permission_mode: str) -> Dict[str, PermissionsByte]:
        """
        Private static method to generate class arguments for a PermissionsMode instance based on
        a Unix permission mode.
        """
        owner_config = PermissionsConfig.from_octal_digit(octal_digit=permission_mode[0])
        group_config = PermissionsConfig.from_octal_digit(octal_digit=permission_mode[1])
        others_config = PermissionsConfig.from_octal_digit(octal_digit=permission_mode[2])

        class_arguments = {
            'owner': PermissionsByte(authority='owner', config=owner_config),
            'group': PermissionsByte(authority='group', config=group_config),
            'others': PermissionsByte(authority='others',config=others_config)
        }

        return class_arguments

    @classmethod
    def _from_permissions_bytes(
        cls,
        permissions_byte_one: PermissionsByte,
        permissions_byte_two: PermissionsByte
    ) -> 'PermissionsMode':
        """
        Private class method to generate a PermissionsMode instance from two PermissionByte
        instances.
        """
        class_arguments = dict()
        class_parameters = get_all_class_parameters(class_object=cls)
        if permissions_byte_one.authority == permissions_byte_two.authority:
            raise ValueError("'authority' cannot be the same for both PermissionsByte objects")

        for byte in [permissions_byte_one, permissions_byte_two]:
            class_parameters.remove(byte.authority)
            class_arguments.update({byte.authority: byte})

        for parameter in class_parameters:
            class_arguments.update(
                {parameter: PermissionsByte(authority=parameter, config=PermissionsConfig())}
            )

        return cls(**class_arguments)

    @classmethod
    def from_octal_representation(cls, octal: Union[str, int]) -> 'PermissionsMode':
        """
        Creates a PermissionsMode instance from an octal representation.

        This function accepts either a string or an integer as input. If the argument is
        a string, the value must be either in the format of an octal literal (e.g., '0o777')
        or as a Unix permissions mode (e.g., '777'). If the value is an integer, it must be a
        decimal representation of an octal as an octal literal (e.g., 0o777) or directly as an
        integer (e.g., 511).

        Args:
            octal (str | int): An octal representation as a string or integer.

        Returns:
            PermissionsMode: A new instance of PermissionsMode corresponding to the
                provided octal value.
        """
        permission_mode: str = from_octal_to_permissions_mode(octal=octal)
        class_arguments: Dict[str, PermissionsByte] = PermissionsMode.__generate_class_arguments_from_mode(
            permission_mode=permission_mode
        )

        return cls(**class_arguments)

    @property
    def permissions_mode(self) -> str:
        """The Unix permissions mode."""
        permissions_mode = (
            self.owner.permissions_mode_as_decimal_repr |
            self.group.permissions_mode_as_decimal_repr |
            self.others.permissions_mode_as_decimal_repr
        )
        return format(permissions_mode, 'o').zfill(3)

    @property
    def permissions_mode_as_decimal_repr(self) -> int:
        """The decimal representation of the Unix permissions mode"""
        return int(self.permissions_mode, 8)

    @property
    def permissions_mode_as_int(self) -> int:
        """The integer representation of the Unix permissions mode"""
        return int(self.permissions_mode)

    @property
    def permissions_mode_as_octal_literal(self) -> str:
        """The string octal literal representation of the Unix permissions mode."""
        return f'0o{self.permissions_mode}'
