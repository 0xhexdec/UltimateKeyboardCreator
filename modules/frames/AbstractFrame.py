# AbstractFrame is the base class for every frame creation module

import adsk.core
import adsk.fusion

from ...KeyboardData import KeyboardData
from ... import Frame
from ... import Sketch

from abc import ABC, abstractmethod

# defining some shorter names
Point = adsk.core.Point3D.create


class AbstractFrame(ABC):

    baseSketch: adsk.fusion.Sketch

    @abstractmethod
    def generateFrame(self, keyboardData: KeyboardData, component: adsk.fusion.Component):
        # create a sketch and add the outline of the layout plate
        baseSketch = component.sketches.add(component.xYConstructionPlane)
        baseSketch.name = "Frame"
        
        plateSize = Frame.getKeyboardPlateSize(keyboardData, component)
        Sketch.rectangle(baseSketch, 0, 0, plateSize[0], plateSize[1], keyboardData)
        # baseSketch.sketchCurves.sketchLines.addTwoPointRectangle(Point(0, 0, 0), Point(plateSize[0], plateSize[1], 0))
