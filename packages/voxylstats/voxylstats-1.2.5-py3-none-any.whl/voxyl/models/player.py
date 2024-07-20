from datetime import datetime
from dataclasses import dataclass, field, InitVar
from typing import List, Dict

from ..constants import *
from .games import *
from .achievements import *

from .utils import (
    calculate_total_stats,
    calculate_total_xp,
    calculate_required_xp,
    alias_convert,
    GAME_ALIASES,
    GAME_STATS,
)

__all__ = [
    "MinecraftPlayer",
    "VoxylPlayer",
    "VoxylPlayerInfo",
    "VoxylPlayerOverall",
    "VoxylPlayerGames",
    "VoxylPlayerGuild",
    "VoxylPlayerAchievements",
    "StatsLeaderboardPlayer",
    "LevelLeaderboardPlayer",
    "WeightedWinsLeaderboardPlayer",
    "TechniqueLeaderboardPlayer",
    "PeriodicLeaderboardPlayer",
    "GuildMember",
    "GuildMemberWithID",
]

games = {
    "bedRush": BedRush,
    "bedwalls": Bedwalls,
    "bedwarsLate": BedwarsLate,
    "bedwarsMega": BedwarsMega,
    "bedwarsNormal": BedwarsNormal,
    "bedwarsRush": BedwarsRush,
    "bowFight": BowFight,
    "bridgeFight": BridgeFight,
    "flatFight": FlatFight,
    "fourWayBridge": FourWayBridge,
    "groundFight": GroundFight,
    "ladderFight": LadderFight,
    "miniwars": Miniwars,
    "obstacles": Obstacles,
    "partyGames": PartyGames,
    "pearlFight": PearlFight,
    "rankedFoursPractice": RankedFoursPractice,
    "resourceCollect": ResourceCollect,
    "resourceOldCollect": ResourceOldCollect,
    "stickFight": StickFight,
    "sumo": Sumo,
    "sumoDuels": SumoDuels,
    "voidFight": VoidFight,
}


@dataclass
class MinecraftPlayer:
    _data: InitVar[Dict] = None
    name: str = None
    uuid: str = None
    formattedUUID: str = None

    def __post_init__(self, _data: dict):
        if not _data:
            return

        self.name = _data.get("username", None)
        self.formattedUUID = _data.get("uuid", None)
        self.uuid = self.formattedUUID.replace("-", "") if self.formattedUUID else None


@dataclass
class GuildMember:
    _data: InitVar[Dict] = None
    uuid: str = None
    role: str = None
    join_date_raw: int = 0
    join_date: datetime = 0

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "GUILD_MEMBER")
        for i in data:
            setattr(self, i, data[i])

        self.join_date = datetime.fromtimestamp(self.join_date_raw).strftime(
            "%I:%M %p on %B %d, %Y"
        )


@dataclass
class GuildMemberWithID(GuildMember):
    guild_id: int = 0


@dataclass
class VoxylPlayer:
    _gen_data: InitVar[Dict] = None
    _over_data: InitVar[Dict] = None
    _game_data: InitVar[Dict] = None
    _guild_data: InitVar[Dict] = None
    _ach_data: InitVar[List] = None
    uuid: str = None
    name: str = None
    last_login_time_raw: int = 0
    last_login_time: datetime = None
    rank: str = None
    level: int = 0
    xp: int = 0
    required_xp: int = 0
    total_xp: int = 0
    weightedwins: int = 0
    wins: int = 0
    finals: int = 0
    kills: int = 0
    beds: int = 0
    guild: GuildMemberWithID = None

    bedRush: BedRush = None
    bedwalls: Bedwalls = None
    bedwarsLate: BedwarsLate = None
    bedwarsMega: BedwarsMega = None
    bedwarsNormal: BedwarsNormal = None
    bedwarsRush: BedwarsRush = None
    bowFight: BowFight = None
    bridgeFight: BridgeFight = None
    flatFight: FlatFight = None
    fourWayBridge: FourWayBridge = None
    groundFight: GroundFight = None
    ladderFight: LadderFight = None
    miniwars: Miniwars = None
    obstacles: Obstacles = None
    partyGames: PartyGames = None
    pearlFight: PearlFight = None
    rankedFoursPractice: RankedFoursPractice = None
    resourceCollect: ResourceCollect = None
    resourceOldCollect: ResourceOldCollect = None
    stickFight: StickFight = None
    sumo: Sumo = None
    sumoDuels: SumoDuels = None
    voidFight: VoidFight = None

    achievements: List[Achievement] = field(default_factory=list)

    def __post_init__(
        self,
        _gen_data: dict,
        _over_data: dict,
        _game_data: dict,
        _guild_data: dict,
        _ach_data: List,
    ):
        if not _gen_data:
            self.guild = GuildMemberWithID(**self.guild) if self.guild else None

            game_data = {game: self.__dict__[game] for game in games}

            for game, model in games.items():
                data = {}
                for i in model.__dataclass_fields__:
                    if "voxyl" not in str(model.__dataclass_fields__[i].type):
                        data[i] = game_data[game][i]
                        continue

                    data[i] = model.__dataclass_fields__[i].type(**game_data[game][i])

                setattr(self, game, model(**data))

            return

        data = alias_convert({**_gen_data, **_over_data}, "PLAYER")
        for i in data:
            setattr(self, i, data[i])

        total = calculate_total_stats(_game_data)
        self.wins = total.get("wins", 0)
        self.finals = total.get("finals", 0)
        self.kills = total.get("kills", 0)
        self.beds = total.get("beds", 0)

        self.required_xp = calculate_required_xp(self.level)
        self.total_xp = calculate_total_xp(self.level, self.xp)

        self.last_login_time = datetime.fromtimestamp(
            self.last_login_time_raw
        ).strftime("%I:%M %p on %B %d, %Y")

        for game, model in games.items():
            data = alias_convert(_game_data, game, model)
            setattr(self, game, model(**data))

        self.achievements = _ach_data

        self.guild = (
            GuildMemberWithID(uuid=self.uuid, _data=_guild_data)
            if _guild_data
            else None
        )


@dataclass
class VoxylPlayerInfo:
    _data: InitVar[Dict] = None
    uuid: str = None
    name: str = None
    last_login_time_raw: int = 0
    last_login_time: datetime = None
    rank: str = None

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "PLAYER")
        for i in data:
            setattr(self, i, data[i])

        self.last_login_time = datetime.fromtimestamp(
            self.last_login_time_raw
        ).strftime("%I:%M %p on %B %d, %Y")


@dataclass
class VoxylPlayerOverall:
    _data: InitVar[Dict] = None
    uuid: str = None
    name: str = None
    level: int = 0
    xp: int = 0
    required_xp: int = 0
    total_xp: int = 0

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "PLAYER")
        for i in data:
            setattr(self, i, data[i])

        self.required_xp = calculate_required_xp(self.level)
        self.total_xp = calculate_total_xp(self.level, self.xp)


@dataclass
class VoxylPlayerGames:
    _data: InitVar[Dict] = None
    uuid: str = None
    name: str = None
    wins: int = 0
    finals: int = 0
    kills: int = 0
    beds: int = 0
    bedRush: BedRush = None
    bedwalls: Bedwalls = None
    bedwarsLate: BedwarsLate = None
    bedwarsMega: BedwarsMega = None
    bedwarsNormal: BedwarsNormal = None
    bedwarsRush: BedwarsRush = None
    bowFight: BowFight = None
    bridgeFight: BridgeFight = None
    flatFight: FlatFight = None
    fourWayBridge: FourWayBridge = None
    groundFight: GroundFight = None
    ladderFight: LadderFight = None
    miniwars: Miniwars = None
    obstacles: Obstacles = None
    partyGames: PartyGames = None
    pearlFight: PearlFight = None
    rankedFoursPractice: RankedFoursPractice = None
    resourceCollect: ResourceCollect = None
    resourceOldCollect: ResourceOldCollect = None
    stickFight: StickFight = None
    sumo: Sumo = None
    sumoDuels: SumoDuels = None
    voidFight: VoidFight = None

    def __post_init__(self, _data: dict):
        if not _data:
            return

        total = calculate_total_stats(_data)
        self.wins = total.get("wins", 0)
        self.finals = total.get("finals", 0)
        self.kills = total.get("kills", 0)
        self.beds = total.get("beds", 0)

        for game, model in games.items():
            data = alias_convert(_data, game, model)
            setattr(self, game, model(**data))


@dataclass
class VoxylPlayerGuild:
    _data: InitVar[Dict] = None
    uuid: str = None
    name: str = None
    guild_id: int = 0
    role: str = None
    join_date_raw: int = 0
    join_date: datetime = None

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "PLAYER")
        for i in data:
            setattr(self, i, data[i])

        self.join_date = datetime.fromtimestamp(self.join_date_raw).strftime(
            "%I:%M %p on %B %d, %Y"
        )


@dataclass
class VoxylPlayerAchievements:
    _data: InitVar[Dict] = None
    uuid: str = None
    name: str = None
    achievements: List[Achievement] = field(default_factory=list)

    def __post_init__(self, _data: dict):
        if not _data:
            return

        self.achievements = _data


@dataclass
class StatsLeaderboardPlayer:
    _data: InitVar[Dict] = None
    uuid: str = None
    level: int = 0
    weightedwins: int = 0
    position: int = 0

    def __post_init__(self, _data: dict):
        data = alias_convert(_data, "LEADERBOARD")
        for i in data:
            setattr(self, i, data[i])


@dataclass
class LevelLeaderboardPlayer(StatsLeaderboardPlayer):
    leaderboard: str = "level"


@dataclass
class WeightedWinsLeaderboardPlayer(StatsLeaderboardPlayer):
    leaderboard: str = "weightedwins"


@dataclass
class TechniqueLeaderboardPlayer:
    _data: InitVar[Dict] = None
    uuid: str = None
    technique_time: float = 0
    date_submitted_raw: int = 0
    date_submitted: datetime = 0
    position: int = 0

    def __post_init__(self, _data: dict):
        data = alias_convert(_data, "LEADERBOARD")
        for i in data:
            setattr(self, i, data[i])

        self.technique_time = int(self.technique_time)
        self.date_submitted = datetime.fromtimestamp(self.date_submitted_raw).strftime(
            "%I:%M %p on %B %d, %Y"
        )


@dataclass
class PeriodicLeaderboardPlayer:
    _data: InitVar[Dict] = None
    uuid: str = None
    wins: int = 0
    position: int = 0

    def __post_init__(self, _data: dict):
        data = alias_convert(_data, "LEADERBOARD")
        for i in data:
            setattr(self, i, data[i])
