from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["StickFight", "StickFightSingle", "StickFightDouble"]


@dataclass
class StickFightSingle(WinsKills):
    pass


@dataclass
class StickFightDouble(WinsKills):
    pass


@dataclass
class StickFight(WinsKills):
    single: StickFightSingle = None
    double: StickFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
