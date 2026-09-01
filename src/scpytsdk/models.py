from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum
from typing import get_args, get_origin, get_type_hints
from uuid import UUID

from scpytsdk._enums import DatabaseEncryptionCipher, Region, SeedType


def _convert_value(value, target_type):
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        if not isinstance(value, target_type):
            return target_type(value)
        return value

    origin = get_origin(target_type)
    args = get_args(target_type)

    if origin is list and args:
        item_type = args[0]
        return [_convert_value(item, item_type) for item in value]

    return value


@dataclass(init=False)
class Database:
    Name: str
    DbId: UUID
    Hostname: str
    block_reads: bool
    block_writes: bool
    delete_protection: bool
    regions: list[Region]
    primaryRegion: Region
    group: str

    def __init__(self, **kwargs):
        """
        The Database class.
        Name: The database name. String.
        DbId: The database ID. UUID.
        Hostname: The database hostname. String.
        block_reads: Boolean.
        block_writes: Boolean
        delete_protection: Boolean
        regions: The AWS regions in which the database instances are located. List of Region. Depracated.
        primaryRegion: The AWS region in which the primary database instance is located. Region.
        group: The database group. String.
        """

        type_hints = get_type_hints(type(self))

        for field in fields(self):
            if field.name not in kwargs:
                continue

            value = kwargs[field.name]
            field_type = type_hints.get(field.name, field.type)

            value = _convert_value(value, field_type)

            setattr(self, field.name, value)


@dataclass(init=False)
class DatabaseSeed:
    type: SeedType
    name: str | None
    timestamp: datetime | None

    def __init__(self, **kwargs):
        """
        The database seed object.
        type: The seed type. SeedType.
        name: The database name from which to branch (Only available if type is SeedType.DATABASE). String.
        timestamp: The timestamp from which to branch (Only available if type is SeedType.DATABASE). datetime.
        """
        type_hints = get_type_hints(type(self))

        for field in fields(self):
            if field.name not in kwargs:
                continue

            value = kwargs[field.name]
            field_type = type_hints.get(field.name, field.type)

            value = _convert_value(value, field_type)

            setattr(self, field.name, value)


@dataclass(init=False)
class Group:
    name: str
    version: str
    uuid: UUID
    locations: list[Region]
    primary: Region
    delete_protection: bool
    archived: bool

    def __init__(self, **kwargs):
        """
        The group class.
        name: The group name. String.
        version: The libsql version that databases in the group are running. String.
        uuid: The group UUID. UUID.
        locations: A list of locations in which the group is located. List of Region. Depracated.
        primary: The group's primary location key. Region.
        delete_protection: Boolean.
        archived: Boolean
        """

        type_hints = get_type_hints(type(self))

        for field in fields(self):
            if field.name not in kwargs:
                continue

            value = kwargs[field.name]
            field_type = type_hints.get(field.name, field.type)

            value = _convert_value(value, field_type)

            setattr(self, field.name, value)


@dataclass(init=False)
class DatabaseEncryption:
    encryption_key: str
    encryption_cipher: DatabaseEncryptionCipher

    def __init__(self, **kwargs):
        """
        The remote database encryption class.
        encryption_key: The base64 encoded encryption key. Must be the correct size for the cipher ( 32 bytes for AES256_GCM, CHACHA20_POLY1305, AEGIS256 variants and 16 bytes for AES128_GCM, AEGIS128L variants ). String.
        encryption_cipher: The encryption cipher. DatabaseEncryptionCipher.
        """

        type_hints = get_type_hints(type(self))

        for field in fields(self):
            if field.name not in kwargs:
                continue

            value = kwargs[field.name]
            field_type = type_hints.get(field.name, field.type)

            value = _convert_value(value, field_type)

            setattr(self, field.name, value)
