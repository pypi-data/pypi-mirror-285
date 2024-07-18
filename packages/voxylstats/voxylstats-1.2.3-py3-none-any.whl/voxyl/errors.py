from typing import Union


class VoxylException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class APIError(VoxylException):
    def __init__(self, resp: dict, api: str, message: str = None):
        if not message:
            message = f"An unknown error has occurred in the {api} API"

        self.resp = resp
        self.api = api
        super().__init__(message)


class ArgumentError(VoxylException):
    def __init__(self, message: str):
        super().__init__(message)


class ClosedSession(VoxylException):
    def __init__(self, message=None):
        if not message:
            message = "Session closed"

        super().__init__(message)


class GuildMemberNotFound(ArgumentError):
    def __init__(self, member: str, guild_name: str = None):
        super().__init__(
            f"'{member}' was not found in the guild '{guild_name}'"
            if guild_name
            else f"'{member}' was not found in the guild"
        )


class GuildNotFound(APIError):
    def __init__(self, api: str, guild: str, message: str = None):
        super().__init__(
            resp=None,
            api=api,
            message=message if message else f"Guild not found: '{guild}'",
        )


class InvalidAPIKey(ArgumentError):
    def __init__(self, api_key: str, message: str = None):
        if not message:
            message = f"Invalid API Key: '{api_key}'"

        super().__init__(message)


class InvalidGameReference(ArgumentError):
    def __init__(self, game: str, message: str = None):
        super().__init__(message if message else f"Invalid game: '{game}'")


class InvalidLeaderboardNumber(ArgumentError):
    def __init__(self, num: Union[int, str], message: str = None):
        super().__init__(
            message
            if message
            else f"Invalid number for leaderboard player amount: '{num}'"
        )


class InvalidTechnique(ArgumentError):
    def __init__(self, technique: str, message: str = None):
        super().__init__(message if message else f"Invalid technique: '{technique}'")


class KeyNotFound(ArgumentError):
    def __init__(self, key: str):
        super().__init__(f"The key, '{key}', was not found")


class KeyRequired(InvalidAPIKey):
    def __init__(self, path=None):
        super().__init__(f"{path} requires an API Key")


class PlayerNotFound(APIError):
    def __init__(self, api: str, player: str, message: str = None):
        super().__init__(
            resp=None,
            api=api,
            message=message if message else f"Player not found: '{player}'",
        )


class RateLimitError(APIError):
    def __init__(self, api: str, resp: dict):
        super().__init__(
            resp=resp, api=api, message=f"You are being rate limited ({api})"
        )


class TimeoutError(APIError):
    def __init__(self, api: str):
        super().__init__(resp=None, api=api, message=f"API Timeout {api}")
