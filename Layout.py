# Author-Julian Pleines
# Creates the Layout Body for the Keyboard

# import math

import adsk.fusion
import adsk.core

from .Sketch import switchCutout, switchHookCutouts, createPlateBorder
from .KeyboardData import KeyboardData

Point = adsk.core.Point3D.create


def create(progressDialog: adsk.core.ProgressDialog, component: adsk.fusion.Component, keyboardData: KeyboardData):
    sketches = component.sketches
    xyPlane = component.xYConstructionPlane

    # ---------------------------- ONE LAYOUT SKETCH ATTEMPT --------------------------------------
    plateSketch = sketches.add(xyPlane)
    plateSketch.name = "Plate"

    cutoutSketch = sketches.add(xyPlane)
    cutoutSketch.name = "Cutout"
    cutoutSketch.isComputeDeferred = True

    hooksSketch = sketches.add(xyPlane)
    hooksSketch.name = "Hooks"
    hooksSketch.isComputeDeferred = True

    createLayoutSketches(plateSketch, cutoutSketch, hooksSketch, progressDialog, keyboardData)

    progressDialog.message = "Recomputing sketches"
    plateSketch.isComputeDeferred = False
    cutoutSketch.isComputeDeferred = False
    hooksSketch.isComputeDeferred = False

    # --------------------------- LAYOUT EXTRUDE --------------------------------------------------

    # create the basic frame
    plateProfile = plateSketch.profiles.item(0)

    progressDialog.message = "Creating Extrusion 1/3"
    extInput = component.features.extrudeFeatures.createInput(plateProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness)
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
    distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness)
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
    distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness - keyboardData.switchHookHeight)
    extInput.setDistanceExtent(False, distance)
    progressDialog.message = "Extruding 3/3"
    extrude = component.features.extrudeFeatures.add(extInput)

    # plateSketch.isLightBulbOn = True
    # cutoutSketch.isLightBulbOn = True
    # hooksSketch.isLightBulbOn = True


def createLayoutSketches(plateSketch: adsk.fusion.Sketch, cutoutSketch: adsk.fusion.Sketch, hooksSketch: adsk.fusion.Sketch, progressDialog: adsk.core.ProgressDialog, keyboardData: KeyboardData):
    maxX = 0.0
    maxY = 0.0
    key = 1
    xOffset = (keyboardData.unit - keyboardData.switchWidth) / 2
    yOffset = (keyboardData.switchDepth / 2) + (keyboardData.unit - keyboardData.switchWidth)
    # creating the switch pockets
    for row in keyboardData.keyboardLayout:
        for entry in row:
            progressDialog.progressValue += 1
            progressDialog.message = "Sketching Keys (" + str(key) + "/" + str(keyboardData.keys) + ")"
            key += 1
            switchCutout(cutoutSketch, (entry[0] * keyboardData.unit) + xOffset, (((keyboardData.keyboardHeightInUnits - 1) - entry[1]) * keyboardData.unit) + yOffset, keyboardData)
            switchHookCutouts(hooksSketch, (entry[0] * keyboardData.unit) + xOffset, (((keyboardData.keyboardHeightInUnits - 1) - entry[1]) * keyboardData.unit) + yOffset, keyboardData)
            if keyboardData.supportKeySize <= entry[2]:
                # means the key needs support
                # TODO add support
                print("creating Support")
            if entry[0] + (entry[2] / 2) > maxX:
                maxX = entry[0] + (entry[2] / 2)
    # creating the outer border
    createPlateBorder(plateSketch, (maxX * keyboardData.unit) + (keyboardData.unit - keyboardData.switchWidth), (keyboardData.keyboardHeightInUnits * keyboardData.unit) + (keyboardData.unit - keyboardData.switchWidth), keyboardData)


def createVoidInfill(voidHeight: float):
    # creates an extrusion for the part of the layout that is not used for keys
    return None
