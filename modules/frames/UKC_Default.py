import adsk.core
import adsk.fusion

from ...KeyboardData import KeyboardData
from ... import Frame
from .AbstractFrame import AbstractFrame


class UKC_Default(AbstractFrame):

    def generateFrame(self, keyboardData: KeyboardData, component: adsk.fusion.Component):
        super().generateFrame(keyboardData, component)
        print("generating a UKC Default frame")
