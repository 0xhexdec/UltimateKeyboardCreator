import adsk.core
import adsk.fusion
import adsk.cam

from .KeyboardData import KeyboardData

orientation = adsk.fusion.DimensionOrientations
Point = adsk.core.Point3D.create


def createPlateBorder(sketch: adsk.fusion.Sketch, width: float, height: float, keyboardData: KeyboardData):
    rectangle(sketch, 0, 0, width, height, keyboardData)


# only usabe for "user readable" sketches, not used by the UKC for generating bodies
def createSwtichPocket(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardData: KeyboardData):
    center = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        Point(x, y, 0), Point(x + keyboardData.switchWidth, y + keyboardData.switchDepth, 0))
    # bottom hook cavety
    bottom = sketch.sketchCurves.sketchLines.addTwoPointRectangle(Point(
        x + (keyboardData.switchWidth / 2 - keyboardData.switchHookWidth / 2), y - keyboardData.switchHookDepth, 0), Point(x + keyboardData.switchWidth / 2 + keyboardData.switchHookWidth / 2, y, 0))
    # top hook cavety
    top = sketch.sketchCurves.sketchLines.addTwoPointRectangle(Point(
        x + (keyboardData.switchWidth / 2 - keyboardData.switchHookWidth / 2), y + keyboardData.switchDepth, 0), Point(x + keyboardData.switchWidth / 2 + keyboardData.switchHookWidth / 2, y + keyboardData.switchDepth + keyboardData.switchHookDepth, 0))

    if keyboardData.fixedSketch:
        for line in center:
            line.isFixed = True
        for line in bottom:
            line.isFixed = True
        for line in top:
            line.isFixed = True

    if keyboardData.parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        # defining size for the base Switch Pocket
        dim(center.item(0).startSketchPoint, center.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardData.switchWidth / 2, y + keyboardData.switchDepth / 2, 0))
        dim(center.item(1).startSketchPoint, center.item(1).endSketchPoint,
            orientation.VerticalDimensionOrientation, Point(x, y, 0))
        # defining size for the bottom hook cavety
        dim(bottom.item(0).startSketchPoint, bottom.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardData.switchWidth / 2, y - keyboardData.switchHookDepth / 2, 0))
        dim(bottom.item(1).startSketchPoint, bottom.item(1).endSketchPoint,
            orientation.VerticalDimensionOrientation, Point(x + keyboardData.switchWidth / 4, y - keyboardData.switchHookDepth / 2, 0))
        # defining size for the top hook cavety
        dim(top.item(0).startSketchPoint, top.item(0).endSketchPoint, orientation.HorizontalDimensionOrientation, Point(
            x + keyboardData.switchWidth / 2, y + keyboardData.switchDepth + keyboardData.switchHookDepth / 2, 0))
        dim(top.item(1).startSketchPoint, top.item(1).endSketchPoint, orientation.VerticalDimensionOrientation, Point(
            x + keyboardData.switchWidth / 4, y + keyboardData.switchDepth + keyboardData.switchHookDepth / 2, 0))

        dim(center.item(2).endSketchPoint, top.item(0).startSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardData.switchWidth / 4, y + keyboardData.switchDepth * 0.75, 0))
        dim(center.item(0).startSketchPoint, bottom.item(2).startSketchPoint,
            orientation.HorizontalDimensionOrientation, Point(x + keyboardData.switchWidth / 4, y + keyboardData.switchDepth / 4, 0))

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


def switchCutout(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardData: KeyboardData):
    rectangle(sketch, x - (keyboardData.switchWidth / 2), y - (keyboardData.switchDepth / 2), keyboardData.switchWidth, keyboardData.switchDepth,
              keyboardData)


def switchHookCutouts(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardData: KeyboardData):
    # bottom hook cutout
    bottom = rectangle(sketch, x - (keyboardData.switchHookWidth / 2),
                       y - keyboardData.switchHookDepth - (keyboardData.switchDepth / 2), keyboardData.switchHookWidth, keyboardData.switchHookDepth, keyboardData)
    # top hook cutout
    top = rectangle(sketch, x - (keyboardData.switchHookWidth / 2), y + (keyboardData.switchDepth / 2),
                    keyboardData.switchHookWidth, keyboardData.switchHookDepth, keyboardData)


def rectangle(sketch: adsk.fusion.Sketch, x: float, y: float, width: float, height: float, keyboardData: KeyboardData):
    rectangle = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        Point(x, y, 0), Point(x + width, y + height, 0))

    if keyboardData.fixedSketch:
        for line in rectangle:
            line.isFixed = True

    if keyboardData.parametricModel:
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
