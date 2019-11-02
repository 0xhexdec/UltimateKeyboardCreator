import adsk.core
import adsk.fusion

from ...KeyboardData import KeyboardData
from ...Frame import getKeyboardPlateSize, getPossibleSupportLocations
from ... import Sketch
from .AbstractFrame import AbstractFrame


class UKC_Default(AbstractFrame):

    def generateFrame(self, keyboardData: KeyboardData, component: adsk.fusion.Component, joinOption: str):
        # super().generateFrame(keyboardData, component)
        print("generating a UKC Default frame")

        # --------------------------- Creating the inner loop -------------------------------------
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
        for i in range(0, 4):
            j = i + 1 if i < 3 else 0
            baseSketch.sketchCurves.sketchArcs.addFillet(rect.item(i), rect.item(i).endSketchPoint.geometry, rect.item(j), rect.item(j).startSketchPoint.geometry, 0.25)

        curves = baseSketch.findConnectedCurves(rect.item(0))
        dirPoint = adsk.core.Point3D.create(0, 0.0, 0)
        offsetCurves = baseSketch.offset(curves, dirPoint, 0.45)

        profile: adsk.fusion.Profile
        outerProfile: adsk.fusion.Profile
        allProfiles: adsk.core.ObjectCollection = adsk.core.ObjectCollection.create()
        for profile in baseSketch.profiles:
            if profile.profileLoops.count > 1:
                outerProfile = profile
            allProfiles.add(profile)

        extInput = component.features.extrudeFeatures.createInput(outerProfile, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness)
        extInput.setDistanceExtent(False, distance)
        extrude = component.features.extrudeFeatures.add(extInput)
        extrude.bodies.item(0).name = "Top Frame"
        
        # Sidewalls for bottom Frame
        extInput = component.features.extrudeFeatures.createInput(outerProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(-0.7)
        extInput.setDistanceExtent(False, distance)
        extrude = component.features.extrudeFeatures.add(extInput)
        extrude.bodies.item(0).name = "Bottom Frame"

        # Closing bottom Frame
        extInput = component.features.extrudeFeatures.createInput(allProfiles, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        offsetDistance = distance
        distance = adsk.core.ValueInput.createByReal(-0.3)
        extent = adsk.fusion.DistanceExtentDefinition.create(distance)
        startFrom = adsk.fusion.FromEntityStartDefinition.create(baseSketch.referencePlane, offsetDistance)
        extInput.setOneSideExtent(extent, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extInput.startExtent = startFrom
        extrude = component.features.extrudeFeatures.add(extInput)
        self._addMicrocontrollerFrame(1, 1, keyboardData, component)

        # adding Supports
        # supportLocations = getPossibleSupportLocations
        # for support in supportLocations:
        #     self._addLayoutPlateSupport(support[0], support[1], keyboardData, component)

    def getSupportedJoinOptions(self) -> list:
        return ["M3x10 ISO 4762", "M4x10 ISO 4762", "#6-32 1/2\" flat head", "Other Screw", "Glue"]

    def _addMicrocontrollerFrame(self, x: float, y: float, keyboardData: KeyboardData, component: adsk.fusion.Component):
        # here I dont need a specific implementation, I am happy with the default implementation but if you want to
        # do something special with the positioning of the Microcontroller you should rewrite this
        super()._addMicrocontrollerFrame(x, y, keyboardData, component)
        print("HERE")

    def _addLayoutPlateSupport(self, x: float, y: float, keyboardData: KeyboardData, component: adsk.fusion.Component):
        # TODO add method body
        print("adding LayoutPlateSupport")
    
    def splitFrame() -> bool:
        return True

