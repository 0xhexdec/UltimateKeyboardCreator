# Keyboard Data

from typing import List, Tuple

microcontrollers = ["Arduino Pro Micro", "Arduino Micro", "Arduino Uno", "Arduino Leonardo", "Teensy 2.0"]
microcontrollerPins = {"Arduino Pro Micro": 18, "Arduino Micro": 20, "Arduino Uno": 20, "Arduino Leonardo": 20, "Teensy 2.0": 25}


class KeyboardKey:
    def __init__(self, x: float, y: float, width: float, isMultiSwitch: bool, isSupported: bool, switches: List[Tuple[float, float]], supports: List[Tuple[float, float]]):
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.isMultiSwitch: bool = isMultiSwitch
        self.isSupported: bool = isSupported
        self.switches: List[Tuple[float, float]] = switches
        self.supports: List[Tuple[float, float]] = supports
    
    @classmethod
    def create(self, x: float, y: float, width: float):
        return self(x, y, width, False, False, [], [])


class KeyboardObject:
    def __init__(self):
        from .modules.frames.AbstractFrame import AbstractFrame
        # from Frame import Frame

        self.layoutData: List[List[KeyboardKey]] = []
        self.layoutName: str = "ANSI 104 (100%)"
        self.microcontroller: str = microcontrollers[0]
        self.frameName: str = ""
        self.frame = None
        self.frameModule: AbstractFrame
        self.author: str = ""
        self.keys: int = 104
        self.switchWidth: float = 1.4
        self.switchDepth: float = 1.4
        self.switchHookWidth: float = 0.5
        self.switchHookDepth: float = 0.15
        self.switchHookHeight: float = 0.14
        self.plateThickness: float = 0.4
        self.frameOverPlateHeight: float = 0.6
        self.unit: float = 1.905
        self.keyboardHeightInUnits: float = 0
        self.printerWidth: float = 20
        self.printerDepth: float = 20
        self.supportKeySize = 2.0
        self.doubleSwitchForSpace = False
        self.makePrintable = True
        self.splitFair: bool = True     # split model to equaly sized parts
        self.splitBottomStraight: bool = True       # use the same top split or not
        self.parametricModel: bool = False
        self.fixedSketch: bool = True
