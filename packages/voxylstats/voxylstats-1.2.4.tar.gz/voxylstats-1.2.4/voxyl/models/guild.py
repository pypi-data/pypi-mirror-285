from datetime import datetime
from dataclasses import dataclass, field, InitVar
from typing import Dict, List

from ..constants import *
from .utils import alias_convert
from .player import GuildMember
from ..errors import GuildMemberNotFound

__all__ = ["Guild", "GuildInfo", "GuildMembers", "LeaderboardGuild"]


@dataclass
class Guild:
    _info_data: InitVar[Dict] = None
    _member_data: InitVar[Dict] = None
    guild_id: int = 0
    name: str = None
    description: str = None
    gxp: int = 0
    member_count: int = 0
    org_owner: str = None
    creation_date: datetime = 0
    creation_date_raw: int = 0
    all_members: List[GuildMember] = field(default_factory=list)
    owner: GuildMember = None
    admins: List[GuildMember] = field(default_factory=list)
    moderators: List[GuildMember] = field(default_factory=list)
    members: List[GuildMember] = field(default_factory=list)

    def __post_init__(self, _info_data: dict, _member_data: dict):
        if not _info_data:
            return

        data = alias_convert(_info_data, "GUILD")
        for i in data:
            setattr(self, i, data[i])

        self.creation_date = datetime.fromtimestamp(self.creation_date_raw).strftime(
            "%I:%M %p on %B %d, %Y"
        )

        for i in _member_data:
            self.all_members.append(GuildMember(i))

            if i["role"] == "OWNER":
                self.owner = GuildMember(i)

            else:
                self.__dict__[f'{i["role"].lower()}s'].append(GuildMember(i))

    def get_guild_member(self, uuid: str):
        for i in self.all_members:
            if i.uuid.replace("-", "") == uuid.replace("-", ""):
                return i

        raise GuildMemberNotFound(uuid, self.name)


@dataclass
class GuildInfo:
    _data: InitVar[Dict] = None
    guild_id: int = 0
    name: str = None
    description: str = None
    gxp: int = 0
    member_count: int = 0
    org_owner: str = None
    creation_date: datetime = 0
    creation_date_raw: int = 0

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "GUILD")
        for i in data:
            setattr(self, i, data[i])

        self.creation_date = datetime.fromtimestamp(self.creation_date_raw).strftime(
            "%I:%M %p on %B %d, %Y"
        )


@dataclass
class GuildMembers:
    _data: InitVar[Dict] = None
    all_members: List[GuildMember] = field(default_factory=list)
    owner: GuildMember = None
    admins: List[GuildMember] = field(default_factory=list)
    moderators: List[GuildMember] = field(default_factory=list)
    members: List[GuildMember] = field(default_factory=list)

    def __post_init__(self, _data: dict):
        if not _data:
            return

        for i in _data:
            self.all_members.append(GuildMember(i))

        for i in _data:
            if i["role"] == "OWNER":
                self.owner = GuildMember(i)

            else:
                self.__dict__[f'{i["role"].lower()}s'].append(GuildMember(i))

    def get_guild_member(self, uuid: str):
        for i in self.all_members:
            if i.uuid.replace("-", "") == uuid.replace("-", ""):
                return i

        raise GuildMemberNotFound(uuid)


@dataclass
class LeaderboardGuild:
    _data: InitVar[Dict] = None
    guild_id: int = 0
    tag: str = None
    gxp: int = 0
    name: str = None
    position: int = 0

    def __post_init__(self, _data: dict):
        if not _data:
            return

        data = alias_convert(_data, "GUILD")
        for i in data:
            setattr(self, i, data[i])
