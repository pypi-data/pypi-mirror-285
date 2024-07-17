from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["GroundFight", "GroundFightSingle", "GroundFightDouble"]


@dataclass
class GroundFightSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class GroundFightDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class GroundFight(WinsFinalsKillsBeds):
    single: GroundFightSingle = None
    double: GroundFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
