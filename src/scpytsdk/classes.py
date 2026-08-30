from uuid import UUID
from dataclasses import dataclass, fields
from scpytsdk.enums import Region, SeedType
from enum import Enum
from typing import get_args, get_origin, get_type_hints
from datetime import datetime

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
    name: str
    timestamp: datetime

    def __init__(self, **kwargs):
        type_hints = get_type_hints(type(self))

        for field in fields(self):
            if field.name not in kwargs:
                continue

            value = kwargs[field.name]
            field_type = type_hints.get(field.name, field.type)

            value = _convert_value(value, field_type)

            setattr(self, field.name, value)
