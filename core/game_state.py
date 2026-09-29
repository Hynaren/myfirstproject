from dataclasses import dataclass
from enum import Enum


class GameScreen(Enum):
    UNKNOWN = "unknown"
    CASTLE = "castle"
    WORLD = "world"


@dataclass
class GameState:
    screen: GameScreen = GameScreen.UNKNOWN
    busy: bool = False