# Author-Julian Pleines
# Creates the Layout Body for the Keyboard

import math

import adsk.fusion
import adsk.core

from .Sketch import switchCutout, switchHookCutouts, createPlateBorder
from .KeyboardData import KeyboardData


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

    # plateSketch.isLightBulbOn = False
    # cutoutSketch.isLightBulbOn = False
    # hooksSketch.isLightBulbOn = False
    plateSketch.isComputeDeferred = False
    cutoutSketch.isComputeDeferred = False
    hooksSketch.isComputeDeferred = False
    progressDialog.message = "Recomputing sketches"

    # --------------------------- LAYOUT EXTRUDE --------------------------------------------------

    # create the basic frame
    plateProfile = plateSketch.profiles.item(0)

    progressDialog.message = "Creating Extrusion"
    extInput = component.features.extrudeFeatures.createInput(plateProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness)
    extInput.setDistanceExtent(False, distance)
    extrude = component.features.extrudeFeatures.add(extInput)
    extrude.bodies.item(0).name = "Layout Plate"

    cutouts = cutoutSketch.profiles

    # finding the outer loop thus the profile responsible for the overall shape
    collection = adsk.core.ObjectCollection.create()
    for prof in cutouts:
        progressDialog.progressValue += 1
        profile = adsk.fusion.Profile.cast(prof)
        collection.add(profile)

    extInput = component.features.extrudeFeatures.createInput(collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness)
    extInput.setDistanceExtent(False, distance)
    extrude = component.features.extrudeFeatures.add(extInput)

    hooks = hooksSketch.profiles
    collection.clear()
    for prof in hooks:
        progressDialog.progressValue += 1
        profile = adsk.fusion.Profile.cast(prof)
        collection.add(profile)

    extInput = component.features.extrudeFeatures.createInput(collection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(keyboardData.plateThickness - keyboardData.switchHookHeight)
    extInput.setDistanceExtent(False, distance)
    extrude = component.features.extrudeFeatures.add(extInput)


def createLayoutSketches(plateSketch: adsk.fusion.Sketch, cutoutSketch: adsk.fusion.Sketch, hooksSketch: adsk.fusion.Sketch, progressDialog: adsk.core.ProgressDialog, keyboardData: KeyboardData):
    maxX = 0.0
    maxY = 0.0
    # creating the switch pockets
    progressDialog.message = "Creating Keyboard Layout sketch"
    for row in keyboardData.keyboardLayout:
        for entry in row:
            progressDialog.progressValue += 1
            switchCutout(cutoutSketch, entry[0] * keyboardData.unit, -(entry[1] + 1) * keyboardData.unit, keyboardData)
            switchHookCutouts(hooksSketch, entry[0] * keyboardData.unit, -(entry[1] + 1) * keyboardData.unit, keyboardData)
            if entry[0] > maxX:
                maxX = math.ceil(entry[0])
            if entry[1] > maxY:
                maxY = math.ceil(entry[1])
    # creating the outer border
    createPlateBorder(plateSketch, (maxX + 1) * keyboardData.unit, (maxY + 1) * keyboardData.unit, keyboardData)
