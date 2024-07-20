from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["BowFight", "BowFightSingle", "BowFightDouble"]


@dataclass
class BowFightSingle(WinsKills):
    pass


@dataclass
class BowFightDouble(WinsKills):
    pass


@dataclass
class BowFight(WinsKills):
    single: BowFightSingle = None
    double: BowFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
