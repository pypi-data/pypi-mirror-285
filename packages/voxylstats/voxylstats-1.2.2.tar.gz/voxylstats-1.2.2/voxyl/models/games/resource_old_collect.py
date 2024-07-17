from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["ResourceOldCollect", "ResourceOldCollectSingle", "ResourceOldCollectDouble"]


@dataclass
class ResourceOldCollectSingle(WinsKills):
    pass


@dataclass
class ResourceOldCollectDouble(WinsKills):
    pass


@dataclass
class ResourceOldCollect(WinsKills):
    single: ResourceOldCollectSingle = None
    double: ResourceOldCollectDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
