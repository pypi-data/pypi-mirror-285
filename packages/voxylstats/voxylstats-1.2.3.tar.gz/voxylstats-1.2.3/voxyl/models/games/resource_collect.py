from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["ResourceCollect", "ResourceCollectSingle", "ResourceCollectDouble"]


@dataclass
class ResourceCollectSingle(WinsKills):
    pass


@dataclass
class ResourceCollectDouble(WinsKills):
    pass


@dataclass
class ResourceCollect(WinsKills):
    single: ResourceCollectSingle = None
    double: ResourceCollectDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
