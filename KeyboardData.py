

class KeyboardData:
    def __init__(self):
        from .modules.frames.AbstractFrame import AbstractFrame

        self.keyboardLayout: list = []
        self.layoutName: str = "ANSI 104 (100%)"
        self.frame: str = ""
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
        self.parametricModel: bool = False
        self.fixedSketch: bool = True
