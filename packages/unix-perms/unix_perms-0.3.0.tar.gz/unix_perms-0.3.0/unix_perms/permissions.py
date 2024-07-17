import stat
from typing import Literal

from unix_perms.models import Authority

OWNER_PERMISSIONS = Authority(
    read_write_execute=stat.S_IRWXU,
    read_write=stat.S_IRUSR | stat.S_IWUSR,
    read=stat.S_IRUSR,
    read_execute=stat.S_IRUSR | stat.S_IXUSR,
    write_execute=stat.S_IWUSR | stat.S_IXUSR,
    write=stat.S_IWUSR,
    execute=stat.S_IXUSR
)
GROUP_PERMISSIONS = Authority(
    read_write_execute=stat.S_IRWXG,
    read_write=stat.S_IRGRP | stat.S_IWGRP,
    read=stat.S_IRGRP,
    read_execute=stat.S_IRGRP | stat.S_IXGRP,
    write_execute=stat.S_IWGRP | stat.S_IXGRP,
    write=stat.S_IWGRP,
    execute=stat.S_IXGRP
)
OTHERS_PERMISSIONS = Authority(
    read_write_execute=stat.S_IRWXO,
    read_write=stat.S_IROTH | stat.S_IWOTH,
    read=stat.S_IROTH,
    read_execute=stat.S_IROTH | stat.S_IXOTH,
    write_execute=stat.S_IWOTH | stat.S_IXOTH,
    write=stat.S_IWOTH,
    execute=stat.S_IXOTH
)

PERMISSIONS_MAPPING = {
    'owner': OWNER_PERMISSIONS, 'group': GROUP_PERMISSIONS, 'others': OTHERS_PERMISSIONS
}

class OctalPermissions:
    """
    An abstract interface facilitating access to octal permissions for
    read, write, and execute for any of the following authorites: ('owner', 'group', 'others').

    This class validates the given authority and assigns the corresponding
    permissions mapping.

    Args:
        authority (Literal['owner', 'group', 'others']): A specific permissions authority.

    Raises:
        ValueError: If 'authority' is not one of ('owner', 'group', 'others').
    """
    def __init__(self, authority: Literal['owner', 'group', 'others']):
        self.authority = authority

        if authority not in {'owner', 'group', 'others'}:
            raise ValueError("'authority' input should be one of ('owner', 'group', 'others')")

        self._permissions: Authority = PERMISSIONS_MAPPING.get(authority)

    @property
    def no_permissions(self) -> int:
        return 0o000

    @property
    def read_write_execute(self) -> int:
        return self._permissions.read_write_execute

    @property
    def read_write(self) -> int:
        return self._permissions.read_write

    @property
    def read(self) -> int:
        return self._permissions.read

    @property
    def read_execute(self) -> int:
        return self._permissions.read_execute

    @property
    def write_execute(self) -> int:
        return self._permissions.write_execute

    @property
    def write(self) -> int:
        return self._permissions.write

    @property
    def execute(self) -> int:
        return self._permissions.execute
