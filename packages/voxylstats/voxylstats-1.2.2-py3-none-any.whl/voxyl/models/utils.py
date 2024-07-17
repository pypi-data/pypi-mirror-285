from typing import Any

__all__ = [
    "alias_convert",
    "calculate_total_stats",
    "calculate_total_xp",
    "calculate_required_xp",
]


def alias_convert(data: dict, mode: str, model: Any = None):
    if mode == "PLAYER":
        return {PLAYER_ALIASES[i]: data[i] for i in data if i in PLAYER_ALIASES}

    elif mode == "GUILD":
        return {GUILD_ALIASES[i]: data[i] for i in data if i in GUILD_ALIASES}

    elif mode == "GUILD_MEMBER":
        return {
            GUILD_MEMBER_ALIASES[i]: data[i] for i in data if i in GUILD_MEMBER_ALIASES
        }

    elif mode == "LEADERBOARD":
        return {
            LEADERBOARD_ALIASES[i]: data[i] for i in data if i in LEADERBOARD_ALIASES
        }

    elif mode == "ACHIEVEMENT":
        return {
            ACHIEVEMENTS_ALIASES[i]: data[i] for i in data if i in ACHIEVEMENTS_ALIASES
        }

    elif type(GAME_ALIASES[mode]) == dict:
        return {
            i: (
                model.__dataclass_fields__[i].type(**data[GAME_ALIASES[mode][i]])
                if GAME_ALIASES[mode][i] in data
                else model.__dataclass_fields__[i].type(
                    **GAME_STATS[GAME_ALIASES[mode][i]]
                )
            )
            for i in GAME_ALIASES[mode]
        }

    else:
        if GAME_ALIASES[mode] in data:
            return data[GAME_ALIASES[mode]]

        else:
            return GAME_STATS[GAME_ALIASES[mode]]


def calculate_total_stats(data: dict):
    wins = 0
    finals = 0
    kills = 0
    beds = 0
    for i in data:
        try:
            wins += data[i]["wins"]

        except:
            pass

        try:
            finals += data[i]["finals"]

        except:
            pass

        try:
            kills += data[i]["kills"]

        except:
            pass

        try:
            beds += data[i]["beds"]

        except:
            pass

    return {"wins": wins, "finals": finals, "kills": kills, "beds": beds}


def calculate_total_xp(level: int, xp: float):
    if level < 5:
        return level * (level + 1) * 500 - 1000 + xp

    totalxp = 0

    if level < 100 and level >= 5:
        totalxp = 5000 * (level - 1) - 6000 + xp

    if level >= 100:
        sum = 0
        for p in range((level - 100) // 100):
            sum += (((level - 100 * (p + 1)) // 100) * 500 + 5000) * (
                95 - ((level - 100 * (p + 1)) // 200)
            ) + (
                (5 + ((level - 100 * (p + 1)) // 200))
                * (6 + ((level - 100 * (p + 1)) // 200))
                * 500
            )

        if (level - ((level // 100) * 100)) <= (4 + (round((level // 100) / 2))):
            totalxp = (
                (
                    (level - ((level // 100) * 100))
                    * (level + 1 - ((level // 100) * 100))
                    * 500
                )
                + 489000
                + xp
                + sum
            )

        if (level - ((level // 100) * 100)) > (4 + (round((level // 100) / 2))):
            totalxp = (
                ((level // 100) * 500 + 5000)
                * ((level - ((level // 100) * 100)) - (5 + (((level - 100) // 200))))
                + (((5 + ((level - 100) // 200)) * (6 + ((level - 100) // 200))) * 500)
                + 489000
                + xp
                + sum
            )

    return totalxp


def calculate_required_xp(level: int):
    requiredExp = (level // 100) * 500 + 5000
    onesplayer1level = level - (level // 100 * 100)
    levelXP = onesplayer1level * 1000 + 1000
    if requiredExp > levelXP:
        requiredExp = levelXP

    return requiredExp


PLAYER_ALIASES = {
    "uuid": "uuid",
    "lastLoginName": "name",
    "lastLoginTime": "last_login_time_raw",
    "role": "rank",
    "level": "level",
    "exp": "xp",
    "weightedwins": "weightedwins",
    "guildId": "guild_id",
    "joinTime": "join_date_raw",
    "guildRole": "role",
}

GAME_ALIASES = {
    "bedRush": {"single": "bedRushSingle", "double": "bedRushDouble"},
    "bedwalls": "bedwalls",
    "bedwarsLate": {"single": "bedwarsLateSingle", "double": "bedwarsLateDouble"},
    "bedwarsMega": {"single": "bedwarsMegaSolo", "double": "bedwarsMegaDouble"},
    "bedwarsNormal": {"single": "bedwarsNormalSingle", "double": "bedwarsNormalDouble"},
    "bedwarsRush": {"single": "bedwarsRushSolo", "double": "bedwarsRushDouble"},
    "bowFight": {"single": "bowFightSingle", "double": "bowFightDouble"},
    "bridgeFight": {
        "single": "bridgesSingle",
        "double": "bridgesDouble",
        "comp": "compBridgeSingle",
    },
    "flatFight": {"single": "flatFightSingle", "double": "flatFightDouble"},
    "fourWayBridge": "fourWayBridgeSingle",
    "groundFight": {"single": "groundSingle", "double": "groundDouble"},
    "ladderFight": {"single": "ladderFightSingle", "double": "ladderFightDouble"},
    "miniwars": {"single": "miniwarsSolo", "double": "miniwarsDouble"},
    "obstacles": "obstacleSingle",
    "partyGames": "partyGames",
    "pearlFight": {"single": "pearlFightSingle", "double": "pearlFightDouble"},
    "rankedFoursPractice": "rankedFoursPractice",
    "resourceCollect": {"single": "resourceSingle", "double": "resourceDouble"},
    "resourceOldCollect": {
        "single": "resourceOldSingle",
        "double": "resourceOldDouble",
    },
    "stickFight": {"single": "stickFightSingle", "double": "stickFightDouble"},
    "sumo": {"block_sumo": "sumo", "beta_sumo": "betaSumo"},
    "sumoDuels": {"single": "sumoDuelsSolo", "double": "sumoDuelsDouble"},
    "voidFight": {"single": "voidSingle", "double": "voidDouble"},
}

LEADERBOARD_ALIASES = {
    "uuid": "uuid",
    "position": "position",
    "level": "level",
    "weightedwins": "weightedwins",
    "time": "technique_time",
    "submittime": "date_submitted_raw",
    "value": "wins",
}

GUILD_ALIASES = {
    "id": "guild_id",
    "name": "name",
    "desc": "description",
    "xp": "gxp",
    "num": "member_count",
    "ownerUUID": "org_owner",
    "time": "creation_date_raw",
    "placing": "position",
    "tag": "tag",
}

GUILD_MEMBER_ALIASES = {
    "uuid": "uuid",
    "guildId": "guild_id",
    "guildRole": "role",
    "role": "role",
    "joinTime": "join_date_raw",
    "time": "join_date_raw",
}

GAME_STATS = {
    "bedRushDouble": {"wins": 0, "kills": 0},
    "bedRushSingle": {"wins": 0, "kills": 0},
    "bedwalls": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsLateDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsLateSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsMegaDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsMegaSolo": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsNormalDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsNormalSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsRushDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bedwarsRushSolo": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "betaSumo": {"wins": 0, "kills": 0},
    "bowFightDouble": {"wins": 0, "kills": 0},
    "bowFightSingle": {"wins": 0, "kills": 0},
    "bridgesDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "bridgesSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "compBridgeSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "flatFightDouble": {"wins": 0, "kills": 0},
    "flatFightSingle": {"wins": 0, "kills": 0},
    "fourWayBridgeSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "groundDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "groundSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "ladderFightDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "ladderFightSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "miniwarsDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "miniwarsSolo": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "obstacleSingle": {"wins": 0},
    "partyGames": {"wins": 0},
    "pearlFightDouble": {"wins": 0, "kills": 0},
    "pearlFightSingle": {"wins": 0, "kills": 0},
    "rankedFoursPractice": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "resourceDouble": {"wins": 0, "kills": 0},
    "resourceSingle": {"wins": 0, "kills": 0},
    "resourceOldDouble": {"wins": 0, "kills": 0},
    "resourceOldSingle": {"wins": 0, "kills": 0},
    "stickFightDouble": {"wins": 0, "kills": 0},
    "stickFightSingle": {"wins": 0, "kills": 0},
    "sumoDuelsDouble": {"wins": 0, "kills": 0},
    "sumoDuelsSolo": {"wins": 0, "kills": 0},
    "sumo": {"wins": 0, "kills": 0},
    "voidDouble": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
    "voidSingle": {"wins": 0, "finals": 0, "kills": 0, "beds": 0},
}

ACHIEVEMENTS_ALIASES = {
    "id": "achievement_id",
    "name": "name",
    "desc": "description",
    "xp": "xp",
}
