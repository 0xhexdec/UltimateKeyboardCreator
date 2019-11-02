# Author-Julian Pleines
# Creates the Layout Body for the Keyboard

# import math

import adsk.fusion
import adsk.core

from .Sketch import switchCutout, switchHookCutouts, createPlateBorder
from .KeyboardData import KeyboardObject

Point = adsk.core.Point3D.create


def create(progressDialog: adsk.core.ProgressDialog, component: adsk.fusion.Component, keyboardObject: KeyboardObject):
    sketches = component.sketches
    xyPlane = component.xYConstructionPlane

    # ---------------------------- LAYOUT SKETCH --------------------------------------------------
    plateSketch = sketches.add(xyPlane)
    plateSketch.name = "Plate"

    cutoutSketch = sketches.add(xyPlane)
    cutoutSketch.name = "Cutout"
    cutoutSketch.isComputeDeferred = True

    hooksSketch = sketches.add(xyPlane)
    hooksSketch.name = "Hooks"
    hooksSketch.isComputeDeferred = True

    createLayoutSketches(plateSketch, cutoutSketch, hooksSketch, progressDialog, keyboardObject)

    progressDialog.message = "Recomputing sketches"
    plateSketch.isComputeDeferred = False
    cutoutSketch.isComputeDeferred = False
    hooksSketch.isComputeDeferred = False

    # --------------------------- LAYOUT EXTRUDE --------------------------------------------------

    # create the basic frame
    plateProfile = plateSketch.profiles.item(0)

    progressDialog.message = "Creating Extrusion 1/3"
    extInput = component.features.extrudeFeatures.createInput(plateProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardObject.plateThickness)
    extInput.setDistanceExtent(False, distance)
    progressDialog.message = "Extruding 1/3"
    extrude = component.features.extrudeFeatures.add(extInput)
    extrude.bodies.item(0).name = "Layout Plate"

    cutouts = cutoutSketch.profiles

    # finding the outer loop thus the profile responsible for the overall shape
    progressDialog.message = "Creating Extrusion 2/3"
    collection = adsk.core.ObjectCollection.create()
    for prof in cutouts:
        progressDialog.progressValue += 1
        profile = adsk.fusion.Profile.cast(prof)
        collection.add(profile)

    extInput = component.features.extrudeFeatures.createInput(collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardObject.plateThickness)
    extInput.setDistanceExtent(False, distance)
    progressDialog.message = "Extruding 2/3"
    extrude = component.features.extrudeFeatures.add(extInput)

    progressDialog.message = "Creating Extrusion 3/3"
    hooks = hooksSketch.profiles
    collection.clear()
    for prof in hooks:
        progressDialog.progressValue += 1
        profile = adsk.fusion.Profile.cast(prof)
        collection.add(profile)

    extInput = component.features.extrudeFeatures.createInput(collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardObject.plateThickness - keyboardObject.switchHookHeight)
    extInput.setDistanceExtent(False, distance)
    progressDialog.message = "Extruding 3/3"
    extrude = component.features.extrudeFeatures.add(extInput)

    # plateSketch.isLightBulbOn = True
    # cutoutSketch.isLightBulbOn = True
    # hooksSketch.isLightBulbOn = True


def createLayoutSketches(plateSketch: adsk.fusion.Sketch, cutoutSketch: adsk.fusion.Sketch, hooksSketch: adsk.fusion.Sketch, progressDialog: adsk.core.ProgressDialog, keyboardObject: KeyboardObject):
    maxX = 0.0
    maxY = 0.0
    key = 1
    xOffset = (keyboardObject.unit - keyboardObject.switchWidth) / 2
    yOffset = (keyboardObject.switchDepth / 2) + (keyboardObject.unit - keyboardObject.switchWidth)
    # creating the switch pockets
    for row in keyboardObject.layoutData:
        for entry in row:
            progressDialog.progressValue += 1
            progressDialog.message = "Sketching Keys (" + str(key) + "/" + str(keyboardObject.keys) + ")"
            key += 1
            if entry.isMultiSwitch:
                for switch in entry.switches:
                    switchCutout(cutoutSketch, (switch[0] * keyboardObject.unit) + xOffset, (((keyboardObject.keyboardHeightInUnits - 1) - switch[1]) * keyboardObject.unit) + yOffset, keyboardObject)
                    switchHookCutouts(hooksSketch, (switch[0] * keyboardObject.unit) + xOffset, (((keyboardObject.keyboardHeightInUnits - 1) - switch[1]) * keyboardObject.unit) + yOffset, keyboardObject)
                
            else:
                switchCutout(cutoutSketch, (entry.x * keyboardObject.unit) + xOffset, (((keyboardObject.keyboardHeightInUnits - 1) - entry.y) * keyboardObject.unit) + yOffset, keyboardObject)
                switchHookCutouts(hooksSketch, (entry.x * keyboardObject.unit) + xOffset, (((keyboardObject.keyboardHeightInUnits - 1) - entry.y) * keyboardObject.unit) + yOffset, keyboardObject)
            
            if entry.isSupported:
                # means the key needs support
                # TODO add support
                print("creating Support")
            
            if entry.x + (entry.width / 2) > maxX:
                maxX = entry.x + (entry.width / 2)
    # creating the outer border
    createPlateBorder(plateSketch, (maxX * keyboardObject.unit) + (keyboardObject.unit - keyboardObject.switchWidth), (keyboardObject.keyboardHeightInUnits * keyboardObject.unit) + (keyboardObject.unit - keyboardObject.switchWidth), keyboardObject)


def createVoidInfill(voidHeight: float):
    # creates an extrusion for the part of the layout that is not used for keys
    return None
