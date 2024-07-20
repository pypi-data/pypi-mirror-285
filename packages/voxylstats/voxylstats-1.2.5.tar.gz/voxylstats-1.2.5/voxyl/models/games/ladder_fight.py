from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["LadderFight", "LadderFightSingle", "LadderFightDouble"]


@dataclass
class LadderFightSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class LadderFightDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class LadderFight(WinsFinalsKillsBeds):
    single: LadderFightSingle = None
    double: LadderFightDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
