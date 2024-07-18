from pydantic import BaseModel


class Authority(BaseModel):
    """
    Represents octals for all Unix file permission settings for a specific authority.

    Args:
        read_write_execute (int): The octal for read, write, and execute permissions.
        read_write (int): The octal for read and write permissions.
        read (int): The octal for read only permissions.
        read_execute (int): The octal for read and execute permissions.
        write_execute (int): The octal for write and execute permissions.
        write (int): The octal for write only permissions.
        execute (int): The octal for execute only permissions.
    """
    read_write_execute: int
    read_write: int
    read: int
    read_execute: int
    write_execute: int
    write: int
    execute: int
