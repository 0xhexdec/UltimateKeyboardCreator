from enum import Enum, unique
from typing import List, Tuple


@unique
class SupportType(Enum):
    CHERRYMX = 1
    # add others later


@unique
class SwitchType(Enum):
    CHERRYMX = 1
    # add others later


@unique
class SupportDirection(Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2

    def isSupported(self) -> bool:
        return True if self is SupportDirection.HORIZONTAL or self is SupportDirection.VERTICAL else False


class Frame:
    def __init__(self):
        self.isModule: bool = False
        self.configAvailable: bool = False
        self.filename: str = ""
        self.filePath: str = ""


class KeyboardKey:
    def __init__(self, x: float, y: float, width: float, height: float, isMultiSwitch: bool, support: SupportDirection, switches: List[Tuple[float, float]], supports: List[Tuple[float, float]]):
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.isMultiSwitch: bool = isMultiSwitch
        self.support: SupportDirection = support
        self.switches: List[Tuple[float, float]] = switches
        self.supports: List[Tuple[float, float]] = supports
    
    @classmethod
    def create(self, x: float, y: float, width: float, height: float):
        return self(x, y, width, height, False, SupportDirection.NONE, [], [])
        