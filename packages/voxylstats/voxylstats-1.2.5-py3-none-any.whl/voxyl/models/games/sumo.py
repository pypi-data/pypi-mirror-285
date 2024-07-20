from dataclasses import dataclass
from .default_game_structure import WinsKills

__all__ = ["Sumo", "BlockSumo", "BetaSumo"]


@dataclass
class BlockSumo(WinsKills):
    pass


@dataclass
class BetaSumo(WinsKills):
    pass


@dataclass
class Sumo(WinsKills):
    block_sumo: BlockSumo = None
    beta_sumo: BetaSumo = None

    def __post_init__(self):
        self.wins = self.block_sumo.wins + self.beta_sumo.wins
        self.kills = self.block_sumo.kills + self.beta_sumo.kills
