from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["BedwarsNormal", "BedwarsNormalSingle", "BedwarsNormalDouble"]


@dataclass
class BedwarsNormalSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsNormalDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsNormal(WinsFinalsKillsBeds):
    single: BedwarsNormalSingle = None
    double: BedwarsNormalDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
