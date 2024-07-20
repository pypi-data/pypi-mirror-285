from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["BedwarsRush", "BedwarsRushSingle", "BedwarsRushDouble"]


@dataclass
class BedwarsRushSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsRushDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsRush(WinsFinalsKillsBeds):
    single: BedwarsRushSingle = None
    double: BedwarsRushDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
