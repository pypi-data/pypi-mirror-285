from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["PearlFight", "PearlFightSingle", "PearlFightDouble"]


@dataclass
class PearlFightSingle(WinsKills):
    pass


@dataclass
class PearlFightDouble(WinsKills):
    pass


@dataclass
class PearlFight(WinsKills):
    single: PearlFightSingle = None
    double: PearlFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
