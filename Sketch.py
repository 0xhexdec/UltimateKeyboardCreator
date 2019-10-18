import adsk.core
import adsk.fusion
import adsk.cam

from .KeyboardData import KeyboardData

orientation = adsk.fusion.DimensionOrientations
point = adsk.core.Point3D.create


def createPlateBorder(sketch: adsk.fusion.Sketch, width: float, height: float, keyboardData: KeyboardData):
    border = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        point(0, -height, 0), point(width, 0, 0))

    if keyboardData.fixedSketch:
        for line in border:
            line.isFixed = True

    if keyboardData.parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        # TODO
        print("NOT IMPLEMENTED YET")


def createSwtichPocket(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardData: KeyboardData):
    # sketch.sketchCurves.sketchLines.addByTwoPoints(point(x,y,0), point(x+10,y+10,0))
    center = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        point(x, y, 0), point(x + keyboardData.switchWidth, y + keyboardData.switchDepth, 0))
    # bottom hook cavety
    bottom = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(
        x + (keyboardData.switchWidth / 2 - keyboardData.switchHookWidth / 2), y - keyboardData.switchHookDepth, 0), point(x + keyboardData.switchWidth / 2 + keyboardData.switchHookWidth / 2, y, 0))
    # top hook cavety
    top = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(
        x + (keyboardData.switchWidth / 2 - keyboardData.switchHookWidth / 2), y + keyboardData.switchDepth, 0), point(x + keyboardData.switchWidth / 2 + keyboardData.switchHookWidth / 2, y + keyboardData.switchDepth + keyboardData.switchHookDepth, 0))

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
            orientation.HorizontalDimensionOrientation, point(x + keyboardData.switchWidth / 2, y + keyboardData.switchDepth / 2, 0))
        dim(center.item(1).startSketchPoint, center.item(1).endSketchPoint,
            orientation.VerticalDimensionOrientation, point(x, y, 0))
        # defining size for the bottom hook cavety
        dim(bottom.item(0).startSketchPoint, bottom.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, point(x + keyboardData.switchWidth / 2, y - keyboardData.switchHookDepth / 2, 0))
        dim(bottom.item(1).startSketchPoint, bottom.item(1).endSketchPoint,
            orientation.VerticalDimensionOrientation, point(x + keyboardData.switchWidth / 4, y - keyboardData.switchHookDepth / 2, 0))
        # defining size for the top hook cavety
        dim(top.item(0).startSketchPoint, top.item(0).endSketchPoint, orientation.HorizontalDimensionOrientation, point(
            x + keyboardData.switchWidth / 2, y + keyboardData.switchDepth + keyboardData.switchHookDepth / 2, 0))
        dim(top.item(1).startSketchPoint, top.item(1).endSketchPoint, orientation.VerticalDimensionOrientation, point(
            x + keyboardData.switchWidth / 4, y + keyboardData.switchDepth + keyboardData.switchHookDepth / 2, 0))

        dim(center.item(2).endSketchPoint, top.item(0).startSketchPoint,
            orientation.HorizontalDimensionOrientation, point(x + keyboardData.switchWidth / 4, y + keyboardData.switchDepth * 0.75, 0))
        dim(center.item(0).startSketchPoint, bottom.item(2).startSketchPoint,
            orientation.HorizontalDimensionOrientation, point(x + keyboardData.switchWidth / 4, y + keyboardData.switchDepth / 4, 0))

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
    rectangle(sketch, x, y, keyboardData.switchWidth, keyboardData.switchDepth,
              keyboardData)


def switchHookCutouts(sketch: adsk.fusion.Sketch, x: float, y: float, keyboardData: KeyboardData):
    # bottom hook cutout
    bottom = rectangle(sketch, x + (keyboardData.switchWidth / 2 - keyboardData.switchHookWidth / 2),
                       y - keyboardData.switchHookDepth, keyboardData.switchHookWidth, keyboardData.switchHookDepth, keyboardData)
    # top hook cutout
    top = rectangle(sketch, x + (keyboardData.switchWidth / 2 - keyboardData.switchHookWidth / 2), y + keyboardData.switchDepth,
                    keyboardData.switchHookWidth, keyboardData.switchHookDepth, keyboardData)


def rectangle(sketch: adsk.fusion.Sketch, x: float, y: float, width: float, height: float, keyboardData: KeyboardData):
    rectangle = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        point(x, y, 0), point(x + width, y + height, 0))

    if keyboardData.fixedSketch:
        for line in rectangle:
            line.isFixed = True

    if keyboardData.parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        # defining size for the base Switch Pocket
        dim(rectangle.item(0).startSketchPoint, rectangle.item(0).endSketchPoint,
            orientation.HorizontalDimensionOrientation, point(x + width / 2, y + height / 2, 0))
        dim(rectangle.item(1).startSketchPoint, rectangle.item(
            1).endSketchPoint, orientation.VerticalDimensionOrientation, point(x, y, 0))

        dim(rectangle.item(0).startSketchPoint, sketch.originPoint,
            orientation.HorizontalDimensionOrientation, point(x + width / 2, y + height, 0))
        dim(rectangle.item(0).startSketchPoint, sketch.originPoint,
            orientation.VerticalDimensionOrientation, point(x + width / 2, y + height, 0))

        geo = sketch.geometricConstraints
        geo.addHorizontal(rectangle.item(0))
        geo.addHorizontal(rectangle.item(2))
        geo.addVertical(rectangle.item(1))
        geo.addVertical(rectangle.item(3))

    return rectangle
