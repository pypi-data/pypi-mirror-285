from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["Miniwars", "MiniwarsSingle", "MiniwarsDouble"]


@dataclass
class MiniwarsSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class MiniwarsDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class Miniwars(WinsFinalsKillsBeds):
    single: MiniwarsSingle = None
    double: MiniwarsDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
