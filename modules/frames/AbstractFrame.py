# AbstractFrame is the base class for every frame creation module

import adsk.core
import adsk.fusion

from ...KeyboardData import KeyboardData
from ...Frame import getKeyboardPlateSize
from ... import Sketch

from abc import ABC, abstractmethod

# defining some shorter names
Point = adsk.core.Point3D.create


class AbstractFrame(ABC):

    baseSketch: adsk.fusion.Sketch

    @abstractmethod
    def generateFrame(self, keyboardData: KeyboardData, component: adsk.fusion.Component, joinOption: str):
        # creating the sketch for the base form of the Frame
        baseSketch = component.sketches.add(component.xYConstructionPlane)
        baseSketch.name = "Frame"
        
        # getting the size of the generated keyboard plate, we can generate bodies outside of this without having to
        # worry about collisions of the bodies, thus blocking holes and such
        plateSize = getKeyboardPlateSize(keyboardData, component)
        # typing for rect and line
        rect: adsk.fusion.SketchLineList
        line: adsk.fusion.SketchLine
        # adding a rectangle representing the plate to the sketch
        rect = Sketch.rectangle(baseSketch, 0, 0, plateSize[0], plateSize[1], keyboardData)
        # making rect a construction rectangle (dotted line, not usable for extruding)
        for line in rect:
            line.isConstruction = True

    @abstractmethod
    def getSupportedJoinOptions(self) -> list:
        # sorry, that standatization-thing is because I am german...
        return ["M3x10 ISO 4762", "M4x10 ISO 4762", "#6-32 3/8\"", "Other", "Glue"]

    @abstractmethod
    def _addMicrocontrollerFrame(self, x: float, y: float, keyboardData: KeyboardData, component: adsk.fusion.Component):
        # TODO add method body
        print("add Microcontroller Frame")

    @abstractmethod
    def _addLayoutPlateSupport(self, x: float, y: float, keyboardData: KeyboardData, component: adsk.fusion.Component):
        # TODO add method body
        print("adding LayoutPlateSupport")

    # just return True if your Frame doesn't require a specific split location
    # the default split
    @abstractmethod
    def splitFrame() -> bool:
        return True
