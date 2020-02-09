import webbrowser
import math
from typing import List

import adsk.core
import adsk.fusion
import adsk.cam

from .KeyboardData import KeyboardObject
from .Types import SupportType, SupportDirection

orientation = adsk.fusion.DimensionOrientations
Point = adsk.core.Point3D.create


def createPlateBorder(sketch: adsk.fusion.Sketch, width: float, height: float, keyboardObject: KeyboardObject):
    rectangle(sketch, 0, 0, width, height, keyboardObject)


def createSplit(sketch: adsk.fusion.Sketch, box: adsk.core.BoundingBox3D, keyboardObject: KeyboardObject):
    # definitions for the split
    minBridgeWidth = (keyboardObject.unit - keyboardObject.switchWidth) / 2
    minBridgeHeight = (keyboardObject.unit - keyboardObject.switchDepth) / 2

    width = box.maxPoint.x - box.minPoint.x
    depth = box.maxPoint.y - box.minPoint.y
    leftBorderWidth = - box.minPoint.x
    lowerBorderWith = - box.minPoint.y
    # TODO currently only able to split in half and only widthwise
    # TODO handle key.switches and key.supports
    if depth > keyboardObject.printerDepth and depth > keyboardObject.printerWidth:
        # TODO check for the better dimension to split
        print("Needs to split in 2 Dimensions...")
    elif depth < keyboardObject.printerDepth and depth > keyboardObject.printerWidth:
        print("use printer depth as Y axis")
        dimensionX = keyboardObject.printerWidth
        dimensionY = keyboardObject.printerDepth
    elif depth > keyboardObject.printerDepth and depth < keyboardObject.printerWidth:
        print("use printer width as Y axis")
        dimensionX = keyboardObject.printerDepth
        dimensionY = keyboardObject.printerWidth
    elif depth < keyboardObject.printerDepth and depth < keyboardObject.printerWidth:
        print("both dimensions are possible")
        # TODO use the better one
        dimensionX = keyboardObject.printerDepth
        dimensionY = keyboardObject.printerWidth
    else:
        print("The splitted objects are exactly the printer size, treated as smaller printer. If the printer is a little bigger, change the value in the input")
    
    numberOfYSplits = math.ceil(width / dimensionX)
    widthToSplit: float = width / numberOfYSplits if keyboardObject.splitFair else keyboardObject.printerWidth
    print("Splitting this keyboard to " + str(widthToSplit * 10) + "mm parts")
    splitXPosition = widthToSplit
    splitPointsList: List[List[float]] = []
    lowestX = width
    done: bool = False
    # TODO do this more advanced by checking for supports and key distances
    while not done:
        splitPoints: List[float] = []
        for row in keyboardObject.layoutData:
            # splitPoints.append(0.0)
            matchingSwitchFound: bool = False
            for entry in row:
                pos = (entry.x + 0.5) * keyboardObject.unit + minBridgeWidth
                if pos >= splitXPosition - leftBorderWidth:
                    matchingSwitchFound = True
                    if keyboardObject.splitCenteredBetweenSwitches:
                        # TODO add this
                        print("Do something here")
                    else:
                        if splitXPosition - leftBorderWidth > pos - keyboardObject.unit:
                            splitPoints.append(pos - keyboardObject.unit)
                        else:
                            splitPoints.append(splitXPosition - leftBorderWidth)
                    print(str((splitPoints[len(splitPoints) - 1] + leftBorderWidth) * 10) + "mm")
                    lowestX = splitPoints[len(splitPoints) - 1] if lowestX > splitPoints[len(splitPoints) - 1] else lowestX
                    break
            if not matchingSwitchFound:
                splitPoints.append(splitXPosition - leftBorderWidth)
        splitPointsList.append(splitPoints)
        if lowestX + widthToSplit > width:
            done = True
        else:
            print("lowest x is: " + str(lowestX * 10) + "mm")
            splitXPosition = lowestX + widthToSplit
            lowestX = width

    # lowest = width
    # for point in splitPoints:
    #     lowest = point if point < lowest else lowest
    # # show user this message if splitting wasn't successful
    # if width - lowest >= keyboardObject.printerWidth:
    #     print("Shit, that does not fit on the printer")
    #     app = adsk.core.Application.get()
    #     ui = app.userInterface
    #     text = "UKC was unable to slice the Keyboard to fit your printer.\nIf you think this should be possible, please try to recreate this error (using same inputs) and create an issue here: https://github.com/0xhexdec/UltimateKeyboardCreator/issues/\nPress OK to open this URL in your browser."
    #     button = ui.messageBox(text, "Slicing Error", 1)
    #     if button == adsk.core.DialogResults.DialogCancel:
    #         print("canceled")
    #     elif button == adsk.core.DialogResults.DialogOK:
    #         webbrowser.open_new("https://github.com/0xhexdec/UltimateKeyboardCreator/issues/")

    # create splitline
    for splitPoints in splitPointsList:
        i = len(splitPoints) * keyboardObject.unit + (keyboardObject.unit - keyboardObject.switchWidth) / 2
        lastPoint: adsk.fusion.SketchPoint = None
        for point in splitPoints:
            if lastPoint is not None:
                if lastPoint.geometry.x != point:
                    line = sketch.sketchCurves.sketchLines.addByTwoPoints(lastPoint, Point(point, i, 0))
                line = sketch.sketchCurves.sketchLines.addByTwoPoints(line.endSketchPoint, Point(point, i - keyboardObject.unit, 0))
            else:
                line = sketch.sketchCurves.sketchLines.addByTwoPoints(Point(point, i, 0), Point(point, i - keyboardObject.unit, 0))
            lastPoint = line.endSketchPoint
            i -= keyboardObject.unit
    # sketch.isLightBulbOn = False


def createSplitLine(sketch: adsk.fusion.Sketch, box: adsk.core.BoundingBox3D, keyboardObject: KeyboardObject):
    width = box.maxPoint.x - box.minPoint.x
    depth = box.maxPoint.y - box.minPoint.y
    leftBorderWidth = - box.minPoint.x
    lowerBorderWith = - box.minPoint.y
    sketch.sketchCurves.sketchLines.addByTwoPoints(Point(width / 2 - leftBorderWidth, depth - lowerBorderWith, 0), Point(width / 2 - leftBorderWidth, -lowerBorderWith, 0))
    sketch.isLightBulbOn = False


# only usabe for "user readable" sketches, not used by the UKC for generating bodies
def createSwtichPocket(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardObject: KeyboardObject):
    center = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        Point(x, y, 0), Point(x + keyboardObject.switchWidth, y + keyboardObject.switchDepth, 0))
    # bottom hook cavety
    bottom = sketch.sketchCurves.sketchLines.addTwoPointRectangle(Point(
        x + (keyboardObject.switchWidth / 2 - keyboardObject.switchHookWidth / 2), y - keyboardObject.switchHookDepth, 0), Point(x + keyboardObject.switchWidth / 2 + keyboardObject.switchHookWidth / 2, y, 0))
    # top hook cavety
    top = sketch.sketchCurves.sketchLines.addTwoPointRectangle(Point(
        x + (keyboardObject.switchWidth / 2 - keyboardObject.switchHookWidth / 2), y + keyboardObject.switchDepth, 0), Point(x + keyboardObject.switchWidth / 2 + keyboardObject.switchHookWidth / 2, y + keyboardObject.switchDepth + keyboardObject.switchHookDepth, 0))

    if keyboardObject.fixedSketch:
        for line in center:
            line.isFixed = True
        for line in bottom:
            line.isFixed = True
        for line in top:
            line.isFixed = True

    if keyboardObject.parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        # defining size for the base Switch Pocket
        dim(center.item(0).startSketchPoint, center.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardObject.switchWidth / 2, y + keyboardObject.switchDepth / 2, 0))
        dim(center.item(1).startSketchPoint, center.item(1).endSketchPoint,
            orientation.VerticalDimensionOrientation, Point(x, y, 0))
        # defining size for the bottom hook cavety
        dim(bottom.item(0).startSketchPoint, bottom.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardObject.switchWidth / 2, y - keyboardObject.switchHookDepth / 2, 0))
        dim(bottom.item(1).startSketchPoint, bottom.item(1).endSketchPoint,
            orientation.VerticalDimensionOrientation, Point(x + keyboardObject.switchWidth / 4, y - keyboardObject.switchHookDepth / 2, 0))
        # defining size for the top hook cavety
        dim(top.item(0).startSketchPoint, top.item(0).endSketchPoint, orientation.HorizontalDimensionOrientation, Point(
            x + keyboardObject.switchWidth / 2, y + keyboardObject.switchDepth + keyboardObject.switchHookDepth / 2, 0))
        dim(top.item(1).startSketchPoint, top.item(1).endSketchPoint, orientation.VerticalDimensionOrientation, Point(
            x + keyboardObject.switchWidth / 4, y + keyboardObject.switchDepth + keyboardObject.switchHookDepth / 2, 0))

        dim(center.item(2).endSketchPoint, top.item(0).startSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardObject.switchWidth / 4, y + keyboardObject.switchDepth * 0.75, 0))
        dim(center.item(0).startSketchPoint, bottom.item(2).startSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardObject.switchWidth / 4, y + keyboardObject.switchDepth / 4, 0))

        geo = sketch.geometricConstraints
        geo.addHorizontal(center.item(0))
        geo.addHorizontal(center.item(2))
        geo.addVertical(center.item(1))
        geo.addVertical(center.item(3))

        geo.addHorizontal(bottom.item(0))
        geo.addHorizontal(bottom.item(2))
        geo.addVertical(bottom.item(1))
        geo.addVertical(bottom.item(3))

        geo.addHorizontal(top.item(0))
        geo.addHorizontal(top.item(2))
        geo.addVertical(top.item(1))
        geo.addVertical(top.item(3))

        geo.addCoincident(center.item(0).startSketchPoint, bottom.item(2))
        geo.addCoincident(center.item(2).endSketchPoint, top.item(0))


def switchCutout(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardObject: KeyboardObject):
    rectangle(sketch, x - (keyboardObject.switchWidth / 2), y - (keyboardObject.switchDepth / 2), keyboardObject.switchWidth, keyboardObject.switchDepth,
              keyboardObject)


def switchHookCutouts(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardObject: KeyboardObject):
    # bottom hook cutout
    bottom = rectangle(sketch, x - (keyboardObject.switchHookWidth / 2),
                       y - keyboardObject.switchHookDepth - (keyboardObject.switchDepth / 2), keyboardObject.switchHookWidth, keyboardObject.switchHookDepth, keyboardObject)
    # top hook cutout
    top = rectangle(sketch, x - (keyboardObject.switchHookWidth / 2), y + (keyboardObject.switchDepth / 2),
                    keyboardObject.switchHookWidth, keyboardObject.switchHookDepth, keyboardObject)


def supportCutout(cutThroughSketch: adsk.fusion.Sketch, cutLipSketch: adsk.fusion.Sketch, x: float, y: float, supportDirection: SupportDirection, keyboardObject: KeyboardObject):
    if keyboardObject.supportType == SupportType.CHERRYMX:
        if supportDirection is SupportDirection.HORIZONTAL:
            rectangle(cutThroughSketch, x - 0.165, y - 0.7, 0.33, 1.4, keyboardObject)
            rectangle(cutLipSketch, x - 0.25, y - 0.85, 0.5, 1.7, keyboardObject)
        elif supportDirection is SupportDirection.VERTICAL:
            rectangle(cutThroughSketch, x - 0.7, y - 0.165, 1.4, 0.33, keyboardObject)
            rectangle(cutLipSketch, x - 0.85, y - 0.25, 1.7, 0.5, keyboardObject)
        else:
            print("Direction Unknown")


def rectangle(sketch: adsk.fusion.Sketch, x: float, y: float, width: float, height: float, keyboardObject: KeyboardObject):
    rectangle = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        Point(x, y, 0), Point(x + width, y + height, 0))

    if keyboardObject.fixedSketch:
        for line in rectangle:
            line.isFixed = True

    if keyboardObject.parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        # defining size for the base Switch Pocket
        dim(rectangle.item(0).startSketchPoint, rectangle.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + width / 2, y + height / 2, 0))
        dim(rectangle.item(1).startSketchPoint, rectangle.item(
            1).endSketchPoint, orientation.VerticalDimensionOrientation, Point(x, y, 0))

        dim(rectangle.item(0).startSketchPoint, sketch.originPoint,
            orientation.HorizontalDimensionOrientation, Point(x + width / 2, y + height, 0))
        dim(rectangle.item(0).startSketchPoint, sketch.originPoint,
            orientation.VerticalDimensionOrientation, Point(x + width / 2, y + height, 0))

        geo = sketch.geometricConstraints
        geo.addHorizontal(rectangle.item(0))
        geo.addHorizontal(rectangle.item(2))
        geo.addVertical(rectangle.item(1))
        geo.addVertical(rectangle.item(3))

    return rectangle
