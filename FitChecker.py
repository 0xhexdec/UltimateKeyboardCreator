# Author-Julian Pleines
# Creates the FitChecker Body for the Keyboard switches

import adsk.fusion
import adsk.core

from .Sketch import createPlateBorder, switchCutout, switchHookCutouts, createSwtichPocket
from .KeyboardData import KeyboardObject


def create(progressDialog: adsk.core.ProgressDialog, rootComponent: adsk.fusion.Component, keyboardObject: KeyboardObject):
    trans = adsk.core.Matrix3D.create()
    occ = rootComponent.occurrences.addNewComponent(trans)

    # get the component from the occurence
    comp = occ.component
    comp.name = "FitChecker"

    sketches = comp.sketches
    xyPlane = comp.xYConstructionPlane

    # --------------------------- FITCHECKER SKETCH CREATION --------------------------------------

    progressDialog.message = "Creating the FitChecker sketch"
    progressDialog.progressValue += 1
    fitChecker = sketches.add(xyPlane)
    fitChecker.name = "FitChecker"
    fitChecker.isLightBulbOn = False
    fitChecker.isComputeDeferred = True
    createFitCheckerSketch(fitChecker, keyboardObject)
    fitChecker.isComputeDeferred = False

    frameSketch = sketches.add(xyPlane)
    frameSketch.name = "Frame"
    frameSketch.isLightBulbOn = False
    cutoutSketch = sketches.add(xyPlane)
    cutoutSketch.name = "Cutout"
    cutoutSketch.isLightBulbOn = False
    hooksSketch = sketches.add(xyPlane)
    hooksSketch.name = "Hooks"
    hooksSketch.isLightBulbOn = False
    frameSketch.isComputeDeferred = True
    cutoutSketch.isComputeDeferred = True
    hooksSketch.isComputeDeferred = True
    createFitCheckerSketches(frameSketch, cutoutSketch, hooksSketch, progressDialog, keyboardObject)
    cutoutSketch.isComputeDeferred = False
    hooksSketch.isComputeDeferred = False
    frameSketch.isComputeDeferred = False

    # --------------------------- FITCHECKER EXTRUDE ----------------------------------------------

    # create the basic frame
    frameProfile = frameSketch.profiles.item(0)

    extInput = comp.features.extrudeFeatures.createInput(frameProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardObject.plateThickness)
    extInput.setDistanceExtent(False, distance)
    extrude = comp.features.extrudeFeatures.add(extInput)
    extrude.bodies.item(0).name = "FitChecker"

    cutouts = cutoutSketch.profiles

    # finding the outer loop thus the profile responsible for the overall shape
    collection = adsk.core.ObjectCollection.create()
    for prof in cutouts:
        profile = adsk.fusion.Profile.cast(prof)
        progressDialog.progressValue += 1
        collection.add(profile)

    extInput = comp.features.extrudeFeatures.createInput(collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardObject.plateThickness)
    extInput.setDistanceExtent(False, distance)
    extrude = comp.features.extrudeFeatures.add(extInput)

    hooks = hooksSketch.profiles
    collection.clear()
    for prof in hooks:
        progressDialog.progressValue += 1
        profile = adsk.fusion.Profile.cast(prof)
        collection.add(profile)

    extInput = comp.features.extrudeFeatures.createInput(collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardObject.plateThickness - keyboardObject.switchHookHeight)
    extInput.setDistanceExtent(False, distance)
    extrude = comp.features.extrudeFeatures.add(extInput)

    occ.isLightBulbOn = False


def createFitCheckerSketch(sketch: adsk.fusion.Sketch, keyboardObject: KeyboardObject):
    createPlateBorder(sketch, 0.505 + (3.75 * keyboardObject.unit),
                      0.505 + keyboardObject.switchHookDepth + (3 * keyboardObject.unit), keyboardObject)
    offset = 0.0
    for y in range(3):
        for x in range(3):
            createSwtichPocket(sketch, 0.505 + (x + offset) * keyboardObject.unit, -(1 + y) * keyboardObject.unit, keyboardObject)
        if offset == 0:
            offset = 0.5
        elif offset == 0.5:
            offset = 0.75


def createFitCheckerSketches(frameSketch: adsk.fusion.Sketch, cutoutSketch: adsk.fusion.Sketch, hooksSketch: adsk.fusion.Sketch, progressDialog: adsk.core.ProgressDialog, keyboardObject: KeyboardObject):
    createPlateBorder(frameSketch, 0.505 + (3.75 * keyboardObject.unit), 0.505 + keyboardObject.switchHookDepth + (3 * keyboardObject.unit), keyboardObject)
    offset = 0.75
    for y in range(3):
        for x in range(3):
            switchCutout(cutoutSketch, 0.505 + (x + offset) * keyboardObject.unit, (1 + y) * keyboardObject.unit, keyboardObject)
            switchHookCutouts(hooksSketch, 0.505 + (x + offset) * keyboardObject.unit, (1 + y) * keyboardObject.unit, keyboardObject)
            progressDialog.progressValue += 1
        if offset == 0.5:
            offset = 0
        elif offset == 0.75:
            offset = 0.5
