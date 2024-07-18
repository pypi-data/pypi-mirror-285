from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["VoidFight", "VoidFightSingle", "VoidFightDouble"]


@dataclass
class VoidFightSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class VoidFightDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class VoidFight(WinsFinalsKillsBeds):
    single: VoidFightSingle = None
    double: VoidFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
