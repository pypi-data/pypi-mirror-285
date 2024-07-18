from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["FlatFight", "FlatFightSingle", "FlatFightDouble"]


@dataclass
class FlatFightSingle(WinsKills):
    pass


@dataclass
class FlatFightDouble(WinsKills):
    pass


@dataclass
class FlatFight(WinsKills):
    single: FlatFightSingle = None
    double: FlatFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
