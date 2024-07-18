import asyncio, aiohttp
from typing import Dict, List, Union, TypedDict

from voxyl.models import *

from .constants import *

from .errors import *


class Client:
    def __init__(self, keys: Union[str, List[str]] = None, loop=None, **options):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        if isinstance(keys, str):
            self._keys = [keys]

        elif isinstance(keys, list):
            self._keys = keys

        else:
            raise InvalidAPIKey("Please provide a string or list of api keys")

        self._itr = iter(self._keys)

        self.timeout = options.get("timeout", 10)

        self._session = aiohttp.ClientSession(
            loop=self.loop, timeout=aiohttp.ClientTimeout(total=self.timeout)
        )

    async def __aenter__(self):
        if self._session.closed:
            self._session = aiohttp.ClientSession(loop=self.loop)

        return self

    async def __aexit__(self, *args):
        await self._session.close()

    def _next_key(self) -> str:
        if not self._keys:
            raise KeyRequired("method '_next_key'")

        try:
            return next(self._itr)

        except StopIteration:
            self._itr = iter(self._keys)
            return next(self._itr)

    async def _get(
        self,
        path: str,
        query_params: dict = None,
        path_params: list = None,
        key_required: bool = True,
    ) -> Dict:
        if self._session.closed:
            raise ClosedSession()

        if not query_params:
            query_params = {}

        if not path_params:
            path_params = []

        if key_required:
            if not self._keys:
                raise KeyRequired(path)

            query_params["api"] = self._next_key()

        try:
            response = await self._session.get(
                url=VOXYL_URLS[path] + "/".join(path_params), params=query_params
            )

        except:
            raise TimeoutError("Voxyl API")

        if response.status == 429:
            raise RateLimitError(path, response)

        elif response.status == 200:
            return await response.json(content_type=None)

        elif response.status == 400 or response.status == 403:
            text = await response.json(content_type=None)
            if "api" not in text["reason"].lower():
                raise APIError(resp=text, api=path, message=text["reason"])

            elif key_required:
                if query_params.get("api", None):
                    raise InvalidAPIKey(query_params.get("api"))

                else:
                    raise KeyRequired(path)

            else:
                raise APIError(
                    response,
                    "Voxyl API",
                    f"An unexpected error has occurred with the Voxyl API",
                )

        else:
            try:
                text = (await response.json(content_type=None)).get("reason")

            except:
                raise APIError(response, "Voxyl API")

            else:
                raise APIError(
                    response,
                    "Voxyl API",
                    f"An unexpected error has occurred with the Voxyl API: {text}",
                )

    async def close(self):
        await self._session.close()

    @property
    def keys(self) -> List[str]:
        return self._keys

    def add_key(self, key):
        if isinstance(key, str):
            self._keys.append(key)
            self._itr = iter(self._keys)

        else:
            raise KeyNotFound(key)

    def remove_key(self, key):
        if isinstance(key, str):
            try:
                self._keys.append(key)
                self._itr = iter(self._keys)

            except ValueError:
                pass

        else:
            raise InvalidAPIKey(key)

    def format_uuid(self, uuid: str):
        uuid = self.shorten_uuid(uuid)
        return (
            uuid[:8]
            + "-"
            + uuid[8:12]
            + "-"
            + uuid[12:16]
            + "-"
            + uuid[16:20]
            + "-"
            + uuid[20:]
        )

    def shorten_uuid(self, uuid: str):
        return uuid.replace("-", "")

    def calculate_required_xp(self, level: int):
        return calculate_required_xp(level)

    def calculate_total_xp(self, level: int, xp: int):
        return calculate_total_xp(level, xp / self.calculate_required_xp(level))

    async def _retrieve_minecraft_player(self, player: str) -> MinecraftPlayer:
        try:
            mojdata = await self._get(
                "minecraft", path_params=[player], key_required=False
            )

        except APIError:
            raise PlayerNotFound("minecraft", player)

        return MinecraftPlayer(_data=mojdata)

    async def _retrieve_voxyl_player_data(
        self, path: str, player: MinecraftPlayer
    ) -> dict:
        try:
            return await self._get(path, path_params=[player.formattedUUID])

        except APIError:
            raise PlayerNotFound(
                path,
                player.formattedUUID,
                f"Could not find voxyl player data on '{player.name}'",
            )

    async def _retrieve_historic_leaderboard(
        self, game: str, stat_type: str, period: str
    ):
        try:
            lb_info = await self._get(
                "leaderboard_game",
                path_params=[game],
                query_params={"type": stat_type, "period": period},
            )

        except APIError:
            raise InvalidGameReference(game)

        return PeriodicLeaderboard(
            _data=lb_info["players"], game=game, type=stat_type, period=period
        )

    async def get_minecraft_player(
        self, player: Union[str, MinecraftPlayer]
    ) -> MinecraftPlayer:
        if isinstance(player, str):
            try:
                return await self._retrieve_minecraft_player(player)

            except APIError:
                raise PlayerNotFound("minecraft", player)

        elif isinstance(player, MinecraftPlayer):
            return player

    async def get_voxyl_player(
        self, player: Union[str, MinecraftPlayer]
    ) -> VoxylPlayer:
        minecraft_player = await self.get_minecraft_player(player)

        try:
            info = await self._retrieve_voxyl_player_data(
                "player_info", minecraft_player
            )
            over = await self._retrieve_voxyl_player_data(
                "player_overall", minecraft_player
            )
            game = await self._retrieve_voxyl_player_data(
                "player_game", minecraft_player
            )

        except APIError:
            raise PlayerNotFound(
                "player",
                minecraft_player.formattedUUID,
                f"Could not find voxyl player data on '{minecraft_player.name}'",
            )

        try:
            guild = await self._retrieve_voxyl_player_data(
                "player_guild", minecraft_player
            )

        except APIError:
            guild = None

        try:
            achievements = (
                await self._retrieve_voxyl_player_data(
                    "player_achievements", minecraft_player
                )
            )["achievements"]
            all_achievements = await self.get_achievements()

            for i in range(len(achievements)):
                achievements[i] = next(
                    (x for x in all_achievements if x.achievement_id == achievements[i])
                )

        except APIError:
            achievements = []

        return VoxylPlayer(
            uuid=minecraft_player.formattedUUID,
            _gen_data=info,
            _over_data=over,
            _game_data=game["stats"],
            _guild_data=guild,
            _ach_data=achievements,
        )

    async def get_voxyl_player_info(
        self, player: Union[str, MinecraftPlayer]
    ) -> VoxylPlayerInfo:
        minecraft_player = await self.get_minecraft_player(player)

        try:
            info = await self._retrieve_voxyl_player_data(
                "player_info", minecraft_player
            )

        except APIError:
            raise PlayerNotFound(
                "player_info",
                minecraft_player.formattedUUID,
                f"Could not find voxyl player info data on '{minecraft_player.name}'",
            )

        return VoxylPlayerInfo(uuid=minecraft_player.formattedUUID, _data=info)

    async def get_voxyl_player_overall(
        self, player: Union[str, MinecraftPlayer]
    ) -> VoxylPlayerOverall:
        minecraft_player = await self.get_minecraft_player(player)

        try:
            over = await self._retrieve_voxyl_player_data(
                "player_overall", minecraft_player
            )

        except APIError:
            raise PlayerNotFound(
                "player_overall",
                minecraft_player.formattedUUID,
                f"Could not find voxyl player overall data on '{minecraft_player.name}'",
            )

        return VoxylPlayerOverall(
            uuid=minecraft_player.formattedUUID, name=minecraft_player.name, _data=over
        )

    async def get_voxyl_player_games(
        self, player: Union[str, MinecraftPlayer]
    ) -> VoxylPlayerGames:
        minecraft_player = await self.get_minecraft_player(player)

        try:
            game = await self._retrieve_voxyl_player_data(
                "player_game", minecraft_player
            )

        except APIError:
            raise PlayerNotFound(
                "player_game",
                minecraft_player.formattedUUID,
                f"Could not find voxyl player game data on '{minecraft_player.name}'",
            )

        return VoxylPlayerGames(
            uuid=minecraft_player.formattedUUID,
            name=minecraft_player.name,
            _data=game["stats"],
        )

    async def get_voxyl_player_guild(
        self, player: Union[str, MinecraftPlayer]
    ) -> VoxylPlayerGuild:
        minecraft_player = await self.get_minecraft_player(player)

        try:
            guild = await self._retrieve_voxyl_player_data(
                "player_guild", minecraft_player
            )

        except APIError:
            raise PlayerNotFound(
                "player_guild",
                minecraft_player.formattedUUID,
                f"Could not find voxyl player guild data '{minecraft_player.name}'",
            )

        return VoxylPlayerGuild(
            uuid=minecraft_player.formattedUUID, name=minecraft_player.name, _data=guild
        )

    async def get_voxyl_player_achievements(
        self, player: Union[str, MinecraftPlayer]
    ) -> VoxylPlayerAchievements:
        minecraft_player = await self.get_minecraft_player(player)

        try:
            achievements = (
                await self._retrieve_voxyl_player_data(
                    "player_achievements", minecraft_player
                )
            )["achievements"]
            all_achievements = await self.get_achievements()

            for i in range(len(achievements)):
                achievements[i] = next(
                    (x for x in all_achievements if x.achievement_id == achievements[i])
                )

        except APIError:
            raise PlayerNotFound(
                "player_achievements",
                minecraft_player.formattedUUID,
                f"Could not find voxyl player achievement data on '{minecraft_player.name}'",
            )

        return VoxylPlayerAchievements(
            uuid=minecraft_player.formattedUUID,
            name=minecraft_player.name,
            _data=achievements,
        )

    async def get_guild(self, identifier: str) -> Guild:
        try:
            guild_info = await self._get("guild_info", path_params=[identifier])
            guild_members = await self._get("guild_members", path_params=[identifier])

        except APIError:
            raise GuildNotFound(
                "guild",
                identifier,
                (
                    f"No guild found with id '{identifier[1:]}'"
                    if identifier[1:].isdigit()
                    else f"No guild found with tag '{identifier}'"
                ),
            )

        return Guild(_info_data=guild_info, _member_data=guild_members["members"])

    async def get_guild_info(self, identifier: str) -> GuildInfo:
        try:
            guild_info = await self._get("guild_info", path_params=[identifier])

        except APIError:
            raise GuildNotFound(
                "guild_info",
                identifier,
                (
                    f"No guild found with id '{identifier[1:]}'"
                    if identifier[1:].isdigit()
                    else f"No guild found with tag '{identifier}'"
                ),
            )

        return GuildInfo(_data=guild_info)

    async def get_guild_members(self, identifier: str) -> GuildMembers:
        try:
            guild_members = await self._get("guild_members", path_params=[identifier])

        except APIError:
            raise GuildNotFound(
                "guild_members",
                identifier,
                (
                    f"No guild found with id '{identifier[1:]}'"
                    if identifier[1:].isdigit()
                    else f"No guild found with tag '{identifier}'"
                ),
            )

        return GuildMembers(_data=guild_members["members"])

    async def get_guild_from_player(self, player: Union[str, MinecraftPlayer]) -> Guild:
        player = await self.get_voxyl_player_guild(player)

        try:
            return await self.get_guild(identifier=f"-{player.guild_id}")

        except APIError:
            raise GuildNotFound(
                "guild_player",
                f"-{player.guild_id}",
                f"No guild found with id '{player.guild_id}'",
            )

    async def get_guild_info_from_player(
        self, player: Union[str, MinecraftPlayer]
    ) -> GuildInfo:
        player = await self.get_voxyl_player_guild(player)

        try:
            return await self.get_guild_info(identifier=f"-{player.guild_id}")

        except APIError:
            raise GuildNotFound(
                "guild_info_player",
                f"-{player.guild_id}",
                f"No guild found with id '{player.guild_id}'",
            )

    async def get_guild_members_from_player(
        self, player: Union[str, MinecraftPlayer]
    ) -> GuildMembers:
        player = await self.get_voxyl_player_guild(player)

        try:
            return await self.get_guild_members(identifier=f"-{player.guild_id}")

        except APIError:
            raise GuildNotFound(
                "guild_members_player",
                f"-{player.guild_id}",
                f"No guild found with id '{player.guild_id}'",
            )

    async def get_level_leaderboard(self, num: int = 10) -> LevelLeaderboard:
        try:
            lb_info = await self._get(
                "leaderboard_level", query_params={"type": "level", "num": num}
            )

        except APIError:
            raise InvalidLeaderboardNumber(num)

        return LevelLeaderboard(_data=lb_info["players"])

    async def get_weightedwins_leaderboard(
        self, num: int = 10
    ) -> WeightedWinsLeaderboard:
        try:
            lb_info = await self._get(
                "leaderboard_weightedwins",
                query_params={"type": "weightedwins", "num": num},
            )

        except APIError:
            raise InvalidLeaderboardNumber(num)

        return WeightedWinsLeaderboard(_data=lb_info["players"])

    async def get_guild_leaderboard(self, num: int = 10) -> GuildLeaderboard:
        try:
            lb_info = await self._get("leaderboard_guild", query_params={"num": num})

        except APIError:
            raise InvalidLeaderboardNumber(num)

        return GuildLeaderboard(_data=lb_info["guilds"])

    async def get_technique_leaderboard(
        self, technique: str = "safetower"
    ) -> TechniqueLeaderboard:
        try:
            lb_info = await self._get(
                "leaderboard_technique", query_params={"technique": technique}
            )

        except APIError:
            raise InvalidTechnique(technique)

        return TechniqueLeaderboard(_data=lb_info["guilds"])

    async def get_daily_wins_leaderboard(self, game: str) -> PeriodicLeaderboard:
        return await self._retrieve_historic_leaderboard(
            game=game, stat_type="wins", period="daily"
        )

    async def get_daily_winstreaks_leaderboard(self, game: str) -> PeriodicLeaderboard:
        return await self._retrieve_historic_leaderboard(
            game=game, stat_type="winstreaks", period="daily"
        )

    async def get_weekly_wins_leaderboard(self, game: str) -> PeriodicLeaderboard:
        return await self._retrieve_historic_leaderboard(
            game=game, stat_type="wins", period="weekly"
        )

    async def get_weekly_winstreaks_leaderboard(self, game: str) -> PeriodicLeaderboard:
        return await self._retrieve_historic_leaderboard(
            game=game, stat_type="winstreaks", period="weekly"
        )

    async def get_achievements(
        self, id: int = None, name: str = None, description: str = None, xp: int = None
    ) -> List[Achievement]:
        achievements = (await self._get("achievements"))["info"]

        if (
            id is not None
            or name is not None
            or description is not None
            or xp is not None
        ):
            achievements = [
                ach
                for ach in achievements
                if (
                    id == ach["id"]
                    or (name and name.lower() in ach["name"].lower())
                    or (description and description.lower() in ach["desc"].lower())
                    or xp == ach["xp"]
                )
            ]

        for i in range(len(achievements)):
            achievements[i] = Achievement(achievements[i])

        return achievements

    async def get_announcements(self) -> dict:
        return await self._get("announcements")

    def get_techniques(self, technique: str = None) -> List[str]:
        return (
            VOXYL_TECHNIQUES.index(technique.lower()) if technique else VOXYL_TECHNIQUES
        )

    def get_games(
        self, game: str = None
    ) -> Dict[str, Dict[Dict[str, str], Dict[str, float]]]:
        return (
            VOXYL_GAMES.get(VOXYL_GAME_NAMES_LOWER.get(game.lower(), None), None)
            if game
            else VOXYL_GAMES
        )

    def get_ranks(
        self, rank: str = None
    ) -> Dict[str, Dict[str, Union[str, List[int]]]]:
        return VOXYL_RANKS.get(rank.lower(), None) if rank else VOXYL_RANKS

    def get_stars(
        self, prestige: str = None
    ) -> Dict[str, Dict[str, Union[str, int, List[int]]]]:
        return (
            VOXYL_PRESTIGES.get(prestige.lower(), None) if prestige else VOXYL_PRESTIGES
        )
