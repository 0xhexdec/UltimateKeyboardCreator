# Author-Julian Pleines
# Creates the Frame Body for the Keyboard

from typing import Tuple
import os

import adsk.core
import adsk.fusion

from .KeyboardData import KeyboardData


class Frame:
    def __init__(self):
        self.isModule = False
        self.filename = ""


def getFrames() -> dict:
    dirPath = os.path.dirname(__file__) + "/modules/frames"
    frames: dict = {}
    for filename in os.listdir(dirPath):
        if filename.endswith(".py") and filename != "AbstractFrame.py":
            name = filename.rpartition(".")[0].replace("_", " ")
            frame = Frame()
            frame.isModule = True
            frame.filename = filename.replace(".py", "")
            frames[name] = frame
    
    dirPath = os.path.dirname(__file__) + "/resources/models/frames"
    for filename in os.listdir(dirPath):
        if filename.endswith(".f3d") and filename != "Base.f3d":
            name = filename.rpartition(".")[0].replace("_", " ")
            frame = Frame()
            frame.isModule = False
            frame.filename = filename
            frames[name] = frame
    return frames


# returns a tuple with width and height as entries
def getKeyboardPlateSize(keyboardData: KeyboardData, component: adsk.fusion.Component) -> Tuple[float, float]:
    points = component.sketches.itemByName("Plate").sketchPoints
    x = 0.0
    y = 0.0
    point: adsk.fusion.SketchPoint
    for point in points:
        if point.geometry.x > x:
            x = point.geometry.x
        if point.geometry.y > y:
            y = point.geometry.y
    # create points
    return (x, y)


def getPossibleSupportLocations() -> list:
    print("finding possible support locations based on the layout")
    return None
