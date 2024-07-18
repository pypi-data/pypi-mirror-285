from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["BedwarsMega", "BedwarsMegaSingle", "BedwarsMegaDouble"]


@dataclass
class BedwarsMegaSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsMegaDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class BedwarsMega(WinsFinalsKillsBeds):
    single: BedwarsMegaSingle = None
    double: BedwarsMegaDouble = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins
        self.finals = self.single.finals + self.double.finals
        self.kills = self.single.kills + self.double.kills
        self.beds = self.single.beds + self.double.beds
