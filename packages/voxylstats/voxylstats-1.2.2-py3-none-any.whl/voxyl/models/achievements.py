from dataclasses import dataclass, field, InitVar
from typing import Dict

from ..constants import *
from .utils import alias_convert

__all__ = ["Achievement"]


@dataclass
class Achievement:
    _data: InitVar[Dict] = None
    achievement_id: int = 0
    name: str = None
    description: str = None
    xp: int = 0

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "ACHIEVEMENT")
        for i in data:
            setattr(self, i, data[i])
