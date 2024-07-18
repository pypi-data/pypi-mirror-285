from dataclasses import dataclass
from .default_game_structure import WinsFinalsKillsBeds

__all__ = ["BridgeFight", "BridgeFightSingle", "BridgeFightDouble", "BridgeFightComp"]


@dataclass
class BridgeFightSingle(WinsFinalsKillsBeds):
    pass


@dataclass
class BridgeFightDouble(WinsFinalsKillsBeds):
    pass


@dataclass
class BridgeFightComp(WinsFinalsKillsBeds):
    pass


@dataclass
class BridgeFight(WinsFinalsKillsBeds):
    single: BridgeFightSingle = None
    double: BridgeFightDouble = None
    comp: BridgeFightComp = None

    def __post_init__(self):
        self.wins = self.single.wins + self.double.wins + self.comp.wins
        self.finals = self.single.finals + self.double.finals + self.comp.finals
        self.kills = self.single.kills + self.double.kills + self.comp.kills
        self.beds = self.single.beds + self.double.beds + self.comp.beds
