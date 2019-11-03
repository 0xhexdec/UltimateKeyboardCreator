import adsk.core
import adsk.fusion
import adsk.cam

from .KeyboardData import KeyboardObject
from .Types import SupportType, SupportDirection

orientation = adsk.fusion.DimensionOrientations
Point = adsk.core.Point3D.create


def createPlateBorder(sketch: adsk.fusion.Sketch, width: float, height: float, keyboardObject: KeyboardObject):
    rectangle(sketch, 0, 0, width, height, keyboardObject)


def createSplit(sketch: adsk.fusion.Sketch, keyboardObject: KeyboardObject, width: float, depth: float, leftBorderWidth: float, lowerBorderWith: float):
    # finding split points that match the required size

    # TODO currently only able to split in half and only widthwise
    # TODO handle key.switches and key.supports
    splitFair = True
    widthToSplit = width / 2 if splitFair else keyboardObject.printerWidth
    splitPoints = []

    for row in keyboardObject.layoutData:
        splitPoints.append(0.0)
        for entry in row:
            pos = (entry.x + 0.5) * keyboardObject.unit + (keyboardObject.unit - keyboardObject.switchWidth) / 2
            if pos >= widthToSplit - leftBorderWidth:
                print(splitPoints[len(splitPoints) - 1])
                break
            else:
                splitPoints[len(splitPoints) - 1] = pos

    lowest = width
    for point in splitPoints:
        lowest = point if point < lowest else lowest
    
    # TODO this if is relatively senseless...
    if width - lowest >= keyboardObject.printerWidth:
        print("Shit, that does not fit on the printer")
    i = len(splitPoints) * keyboardObject.unit + (keyboardObject.unit - keyboardObject.switchWidth) / 2
    lastPoint = None
    for point in splitPoints:
        if lastPoint is not None:
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(lastPoint, Point(point, i, 0))
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(line.endSketchPoint, Point(point, i - keyboardObject.unit, 0))
        else:
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(Point(point, i, 0), Point(point, i - keyboardObject.unit, 0))
        lastPoint = line.endSketchPoint
        i -= keyboardObject.unit
    sketch.isLightBulbOn = False


def createSplitLine(sketch: adsk.fusion.Sketch, keyboardObject: KeyboardObject, width: float, depth: float, leftBorderWidth: float, lowerBorderWith: float):
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
