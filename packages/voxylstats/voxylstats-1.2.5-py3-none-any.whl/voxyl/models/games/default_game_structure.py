from dataclasses import dataclass

__all__ = ["WinsFinalsKillsBeds", "WinsKills", "Wins"]


@dataclass
class WinsFinalsKillsBeds:
    wins: int = 0
    finals: int = 0
    kills: int = 0
    beds: int = 0


@dataclass
class WinsKills:
    wins: int = 0
    kills: int = 0


@dataclass
class Wins:
    wins: int = 0
