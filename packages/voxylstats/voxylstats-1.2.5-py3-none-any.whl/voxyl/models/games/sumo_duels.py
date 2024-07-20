from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["SumoDuels", "SumoDuelsSingle", "SumoDuelsDouble"]


@dataclass
class SumoDuelsSingle(WinsKills):
    pass


@dataclass
class SumoDuelsDouble(WinsKills):
    pass


@dataclass
class SumoDuels(WinsKills):
    single: SumoDuelsSingle = None
    double: SumoDuelsDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.kills = self.single.kills + self.double.kills
