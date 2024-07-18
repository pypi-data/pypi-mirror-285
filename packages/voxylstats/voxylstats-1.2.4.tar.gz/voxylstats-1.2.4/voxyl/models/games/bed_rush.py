from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["BedRush", "BedRushSingle", "BedRushDouble"]


@dataclass
class BedRushSingle(WinsKills):
    pass


@dataclass
class BedRushDouble(WinsKills):
    pass


@dataclass
class BedRush(WinsKills):
    single: BedRushSingle = None
    double: BedRushDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
