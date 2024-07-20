VOXYL_BASE = "https://api.voxyl.net"
VOXYL_URLS = {
    "minecraft": "https://api.ashcon.app/mojang/v2/user/",
    "player_info": VOXYL_BASE + "/player/info/",
    "player_overall": VOXYL_BASE + "/player/stats/overall/",
    "player_game": VOXYL_BASE + "/player/stats/game/",
    "player_guild": VOXYL_BASE + "/player/guild/",
    "player_achievements": VOXYL_BASE + "/achievements/player/",
    "guild_info": VOXYL_BASE + "/guild/info/",
    "guild_members": VOXYL_BASE + "/guild/members/",
    "leaderboard_guild": VOXYL_BASE + "/guild/top/",
    "leaderboard_level": VOXYL_BASE + "/leaderboard/normal/",
    "leaderboard_weightedwins": VOXYL_BASE + "/leaderboard/normal/",
    "leaderboard_technique": VOXYL_BASE + "/leaderboard/technique/",
    "leaderboard_game": VOXYL_BASE + "/leaderboard/game/",
    "announcements": VOXYL_BASE + "/announcement/all/",
    "achievements": VOXYL_BASE + "/achievements/info/",
}

VOXYL_TECHNIQUES = [
    "wallclutch",
    "highclutch",
    "sideclutch",
    "knockbackclutch",
    "jumparound",
    "safetower",
    "speedclutch",
    "ladderclutch",
    "hitclutch",
    "brokenwallrun",
    "bridgestart",
    "knockbackwallclutch",
]

VOXYL_GAMES = {
    "bridgesSingle": {
        "formatted_name": "1v1 Bed Bridge Fight",
        "max_players": 2,
        "weight": 0.55,
    },
    "bridgesDouble": {
        "formatted_name": "2v2 Bed Bridge Fight",
        "max_players": 4,
        "weight": 0.69,
    },
    "compBridgeSingle": {
        "formatted_name": "Competitive Bed Bridge Fight",
        "max_players": 2,
        "weight": 1.24,
    },
    "sumo": {"formatted_name": "Block Sumo", "max_players": 12, "weight": 3.93},
    "betaSumo": {"formatted_name": "Beta Block Sumo", "max_players": 16, "weight": 5.0},
    "sumoDuelsSolo": {
        "formatted_name": "1v1 Block Sumo Duels",
        "max_players": 2,
        "weight": 0.92,
    },
    "sumoDuelsDouble": {
        "formatted_name": "2v2 Block Sumo Duels",
        "max_players": 4,
        "weight": 1.26,
    },
    "obstacleSingle": {"formatted_name": "Obstacles", "max_players": 2, "weight": 1.2},
    "resourceSingle": {
        "formatted_name": "1v1 Resource Collect",
        "max_players": 2,
        "weight": 1.2,
    },
    "resourceDouble": {
        "formatted_name": "2v2 Resource Collect",
        "max_players": 4,
        "weight": 2.17,
    },
    "resourceOldSingle": {
        "formatted_name": "1v1 Old Resource Collect",
        "max_players": 2,
        "weight": 1.2,
    },
    "resourceOldDouble": {
        "formatted_name": "2v2 Old Resource Collect",
        "max_players": 4,
        "weight": 2.69,
    },
    "groundSingle": {
        "formatted_name": "1v1 Ground Fight",
        "max_players": 2,
        "weight": 0.46,
    },
    "groundDouble": {
        "formatted_name": "2v2 Ground Fight",
        "max_players": 4,
        "weight": 0.38,
    },
    "voidSingle": {
        "formatted_name": "1v1 Void Fight",
        "max_players": 2,
        "weight": 0.73,
    },
    "voidDouble": {
        "formatted_name": "2v2 Void Fight",
        "max_players": 4,
        "weight": 0.98,
    },
    "bedwarsNormalSingle": {
        "formatted_name": "1v1 Bedwars Normal",
        "max_players": 2,
        "weight": 1.0,
    },
    "bedwarsNormalDouble": {
        "formatted_name": "2v2 Bedwars Normal",
        "max_players": 4,
        "weight": 1.19,
    },
    "bedwarsMegaSolo": {
        "formatted_name": "Bedwars Mega Solo",
        "max_players": 8,
        "weight": 4.77,
    },
    "bedwarsMegaDouble": {
        "formatted_name": "Bedwars Mega Doubles",
        "max_players": 16,
        "weight": 4.84,
    },
    "bedwarsLateSingle": {
        "formatted_name": "1v1 Bedwars Late Game",
        "max_players": 2,
        "weight": 1.09,
    },
    "bedwarsLateDouble": {
        "formatted_name": "2v2 Bedwars Late Game",
        "max_players": 4,
        "weight": 1.26,
    },
    "bedwarsRushSolo": {
        "formatted_name": "1v1 Bedwars Rush Duels",
        "max_players": 2,
        "weight": 1.09,
    },
    "bedwarsRushDouble": {
        "formatted_name": "2v2 Bedwars Rush Duels",
        "max_players": 4,
        "weight": 1.26,
    },
    "stickFightSingle": {
        "formatted_name": "1v1 Stick Fight",
        "max_players": 2,
        "weight": 0.61,
    },
    "stickFightDouble": {
        "formatted_name": "2v2 Stick Fight",
        "max_players": 4,
        "weight": 0.66,
    },
    "flatFightSingle": {
        "formatted_name": "1v1 Flat Fight",
        "max_players": 2,
        "weight": 0.68,
    },
    "flatFightDouble": {
        "formatted_name": "2v2 Flat Fight",
        "max_players": 4,
        "weight": 0.88,
    },
    "ladderFightSingle": {
        "formatted_name": "1v1 Ladder Fight",
        "max_players": 2,
        "weight": 0.67,
    },
    "ladderFightDouble": {
        "formatted_name": "2v2 Ladder Fight",
        "max_players": 4,
        "weight": 0.8,
    },
    "partyGames": {"formatted_name": "Party Games", "max_players": 12, "weight": 7.92},
    "rankedFoursPractice": {
        "formatted_name": "4v4 Ranked Practice",
        "max_players": 8,
        "weight": 1.27,
    },
    "bowFightSingle": {
        "formatted_name": "1v1 Bow Fight",
        "max_players": 2,
        "weight": 0.55,
    },
    "bowFightDouble": {
        "formatted_name": "2v2 Bow Fight",
        "max_players": 4,
        "weight": 0.62,
    },
    "pearlFightSingle": {
        "formatted_name": "1v1 Pearl Fight",
        "max_players": 2,
        "weight": 0.5,
    },
    "pearlFightDouble": {
        "formatted_name": "2v2 Pearl Fight",
        "max_players": 4,
        "weight": 0.62,
    },
    "bedRushSingle": {
        "formatted_name": "1v1 Bed Rush",
        "max_players": 2,
        "weight": 0.75,
    },
    "bedRushDouble": {
        "formatted_name": "2v2 Bed Rush",
        "max_players": 4,
        "weight": 0.9,
    },
    "bedwalls": {"formatted_name": "Bedwalls", "max_players": 64, "weight": 20.0},
    "bedwarsEightSolo": {
        "formatted_name": "Bedwars Eight Solo",
        "max_players": 8,
        "weight": 1.21,
    },
    "miniwarsSolo": {
        "formatted_name": "Miniwars Solo",
        "max_players": 4,
        "weight": 2.79,
    },
    "miniwarsDouble": {
        "formatted_name": "Miniwars Double",
        "max_players": 8,
        "weight": 4.22,
    },
    "fourWayBridgeSingle": {
        "formatted_name": "Four Way Bridge Fight",
        "max_players": 4,
        "weight": 0.84,
    },
}

VOXYL_GAME_NAMES_LOWER = {
    "bedrushdouble": "bedRushDouble",
    "bedrushsingle": "bedRushSingle",
    "bedwalls": "bedwalls",
    "bedwarslatedouble": "bedwarsLateDouble",
    "bedwarslatesingle": "bedwarsLateSingle",
    "bedwarsmegadouble": "bedwarsMegaDouble",
    "bedwarsmegasolo": "bedwarsMegaSolo",
    "bedwarsnormaldouble": "bedwarsNormalDouble",
    "bedwarsnormalsingle": "bedwarsNormalSingle",
    "bedwarsrushdouble": "bedwarsRushDouble",
    "bedwarsrushsolo": "bedwarsRushSolo",
    "betasumo": "betaSumo",
    "bowfightdouble": "bowFightDouble",
    "bowfightsingle": "bowFightSingle",
    "bridgesdouble": "bridgesDouble",
    "bridgessingle": "bridgesSingle",
    "compbridgesingle": "compBridgeSingle",
    "flatfightdouble": "flatFightDouble",
    "flatfightsingle": "flatFightSingle",
    "fourwaybridgesingle": "fourWayBridgeSingle",
    "grounddouble": "groundDouble",
    "groundsingle": "groundSingle",
    "ladderfightdouble": "ladderFightDouble",
    "ladderfightsingle": "ladderFightSingle",
    "miniwarsdouble": "miniwarsDouble",
    "miniwarssolo": "miniwarsSolo",
    "obstaclesingle": "obstacleSingle",
    "partygames": "partyGames",
    "pearlfightdouble": "pearlFightDouble",
    "pearlfightsingle": "pearlFightSingle",
    "rankedfourspractice": "rankedFoursPractice",
    "resourcedouble": "resourceDouble",
    "resourcesingle": "resourceSingle",
    "resourceolddouble": "resourceOldDouble",
    "resourceoldsingle": "resourceOldSingle",
    "stickfightdouble": "stickFightDouble",
    "stickfightsingle": "stickFightSingle",
    "sumoduelsdouble": "sumoDuelsDouble",
    "sumoduelssolo": "sumoDuelsSolo",
    "sumo": "sumo",
    "voiddouble": "voidDouble",
    "voidsingle": "voidSingle",
}

VOXYL_RANKS = {
    "default": {
        "rgb": [85, 85, 85],
        "hex": "#555555",
    },
    "adept": {
        "rgb": [5, 172, 32],
        "hex": "#05ac20",
    },
    "expert": {
        "rgb": [7, 121, 209],
        "hex": "#0779d1",
    },
    "master": {
        "rgb": [247, 182, 15],
        "hex": "#f7b60f",
    },
    "youtube": {
        "rgb": [230, 3, 3],
        "hex": "#e60303",
    },
    "builder": {
        "rgb": [221, 101, 221],
        "hex": "#dd65dd",
    },
    "appeal": {
        "rgb": [245, 187, 187],
        "hex": "#f5bbbb",
    },
    "dev": {
        "rgb": [85, 255, 85],
        "hex": "#55ff55",
    },
    "helper": {
        "rgb": [90, 209, 90],
        "hex": "#5ad15a",
    },
    "trainee": {
        "rgb": [90, 209, 90],
        "hex": "#5ad15a",
    },
    "mod": {
        "rgb": [250, 241, 107],
        "hex": "#faf16b",
    },
    "srmod": {
        "rgb": [255, 163, 67],
        "hex": "#ffa343",
    },
    "manager": {
        "rgb": [220, 16, 16],
        "hex": "#dc1010",
    },
    "admin": {
        "rgb": [221, 64, 65],
        "hex": "#dd4041",
    },
    "owner": {"rgb": [252, 119, 126], "hex": "#fc777e"},
}

VOXYL_PRESTIGES = {
    "none": {"star": 0, "rgb": [48, 48, 48], "hex": "#303030"},
    "iron": {"star": 100, "rgb": [64, 64, 64], "hex": "#404040"},
    "gold": {"star": 200, "rgb": [62, 46, 4], "hex": "#3e2e04"},
    "diamond": {"star": 300, "rgb": [0, 64, 64], "hex": "#004040"},
    "emerald": {"star": 400, "rgb": [14, 44, 24], "hex": "#0e2c18"},
    "sapphire": {"star": 500, "rgb": [0, 43, 43], "hex": "#002b2b"},
    "ruby": {"star": 600, "rgb": [43, 0, 0], "hex": "#2b0000"},
    "crystal": {"star": 700, "rgb": [64, 21, 64], "hex": "#401540"},
    "opal": {"star": 800, "rgb": [21, 21, 64], "hex": "#151540"},
    "amethyst": {"star": 900, "rgb": [43, 0, 0], "hex": "#2b0000"},
}
