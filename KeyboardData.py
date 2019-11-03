# Keyboard Data

from typing import List


microcontrollers = ["Arduino Pro Micro", "Arduino Micro", "Arduino Uno", "Arduino Leonardo", "Teensy 2.0"]
microcontrollerPins = {"Arduino Pro Micro": 18, "Arduino Micro": 20, "Arduino Uno": 20, "Arduino Leonardo": 20, "Teensy 2.0": 25}


class KeyboardObject:
    def __init__(self):
        from .modules.frames.AbstractFrame import AbstractFrame
        from .Types import Frame, KeyboardKey, SupportType

        self.layoutData: List[List[KeyboardKey]] = []
        self.layoutName: str = "ANSI 104 (100%)"
        self.microcontroller: str = microcontrollers[0]
        self.frameName: str = ""
        self.frame: Frame = None
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
        self.supportKeySize: float = 2.0
        self.supportSizes: dict = {2.0: 1.2 / self.unit, 2.25: 1.2 / self.unit, 2.75: 1.2 / self.unit, 6.0: 4.9 / self.unit, 6.25: 5.0 / self.unit, 6.5: 5.25 / self.unit}
        self.supportType: SupportType = SupportType.CHERRYMX
        self.doubleSwitchForSpace: bool = False
        self.makePrintable: bool = True
        self.splitFair: bool = True     # split model to equaly sized parts
        self.splitBottomStraight: bool = True       # use the same top split or not
        self.parametricModel: bool = False
        self.fixedSketch: bool = True
