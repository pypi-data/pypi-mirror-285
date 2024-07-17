from dataclasses import dataclass, field, InitVar
from typing import List, Dict

from ..constants import *
from .player import (
    StatsLeaderboardPlayer,
    TechniqueLeaderboardPlayer,
    PeriodicLeaderboardPlayer,
)
from .guild import LeaderboardGuild

__all__ = [
    "StatsLeaderboard",
    "LevelLeaderboard",
    "WeightedWinsLeaderboard",
    "TechniqueLeaderboard",
    "PeriodicLeaderboard",
    "GuildLeaderboard",
]


@dataclass
class StatsLeaderboard:
    _data: InitVar[Dict] = None
    players: List[StatsLeaderboardPlayer] = field(default_factory=list)

    def __post_init__(self, _data: dict):
        if not _data:
            return

        for i in _data:
            self.players.append(StatsLeaderboardPlayer(i))


@dataclass
class LevelLeaderboard(StatsLeaderboard):
    leaderboard: str = "level"


@dataclass
class WeightedWinsLeaderboard(StatsLeaderboard):
    leaderboard: str = "weightedwins"


@dataclass
class TechniqueLeaderboard:
    _data: InitVar[Dict] = None
    players: List[StatsLeaderboardPlayer] = field(default_factory=list)

    def __post_init__(self, _data: dict):
        if not _data:
            return

        for i in _data:
            self.players.append(TechniqueLeaderboardPlayer(i))


@dataclass
class PeriodicLeaderboard:
    _data: InitVar[Dict] = None
    game: str = None
    type: str = None
    period: str = None
    players: List[PeriodicLeaderboardPlayer] = field(default_factory=list)

    def __post_init__(self, _data: dict):
        if not _data:
            return

        self.game = VOXYL_GAME_NAMES_LOWER[self.game.lower()]

        for i in range(len(_data)):
            self.players.append(PeriodicLeaderboardPlayer(_data[i], position=i + 1))


@dataclass
class GuildLeaderboard:
    _data: InitVar[Dict] = None
    guilds: List[LeaderboardGuild] = field(default_factory=list)

    def __post_init__(self, _data: dict):
        if not _data:
            return

        for i in _data:
            self.guilds.append(LeaderboardGuild(i))
