from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["BedwarsLate", "BedwarsLateSingle", "BedwarsLateDouble"]


@dataclass
class BedwarsLateSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsLateDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsLate(WinsFinalsKillsBeds):
    single: BedwarsLateSingle = None
    double: BedwarsLateDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
