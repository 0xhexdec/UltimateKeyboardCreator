import adsk.core, adsk.fusion, adsk.cam, traceback
import io, json, types, os, sys

orientation = adsk.fusion.DimensionOrientations
point = adsk.core.Point3D.create

def createPlateBorder(sketch: adsk.fusion.Sketch, width:float, height: float, parametricModel: bool, fixedSketch: bool):
    border = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(0, -height, 0), point(width, 0, 0))

    if fixedSketch:
        for line in border:
            line.isFixed = True
    
    if parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        # TODO
        print("NOT IMPLEMENTED YET")
    

def createSwtichPocket(sketch: adsk.fusion.Sketch, x: float, y: float, switchWidth: float, switchDepth: float, switchHookWidth: float, switchHookDepth: float, parametricModel: bool, fixedSketch: bool):
    # sketch.sketchCurves.sketchLines.addByTwoPoints(point(x,y,0), point(x+10,y+10,0))
    center = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(x,y,0),point(x+switchWidth,y+switchDepth,0))
    #bottom hook cavety
    bottom = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(x + (switchWidth/2 - switchHookWidth/2),y - switchHookDepth,0), point(x + switchWidth/2 + switchHookWidth/2, y,0))
    #top hook cavety
    top = sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(x + (switchWidth/2 - switchHookWidth/2),y + switchDepth,0), point(x + switchWidth/2 + switchHookWidth/2, y + switchDepth + switchHookDepth,0))

    if fixedSketch:
        for line in center:
            line.isFixed = True
        for line in bottom:
            line.isFixed = True
        for line in top:
            line.isFixed = True

    if parametricModel:
        dim = sketch.sketchDimensions.addDistanceDimension
        #defining size for the base Switch Pocket
        dim(center.item(0).startSketchPoint, center.item(0).endSketchPoint, orientation.HorizontalDimensionOrientation, point(x + switchWidth/2, y + switchDepth/2,0))
        dim(center.item(1).startSketchPoint, center.item(1).endSketchPoint, orientation.VerticalDimensionOrientation, point(x, y,0))
        #defining size for the bottom hook cavety
        dim(bottom.item(0).startSketchPoint, bottom.item(0).endSketchPoint, orientation.HorizontalDimensionOrientation, point(x + switchWidth/2, y - switchHookDepth/2, 0))
        dim(bottom.item(1).startSketchPoint, bottom.item(1).endSketchPoint, orientation.VerticalDimensionOrientation, point(x + switchWidth/4, y - switchHookDepth/2,0))
        #defining size for the top hook cavety
        dim(top.item(0).startSketchPoint, top.item(0).endSketchPoint, orientation.HorizontalDimensionOrientation, point(x + switchWidth/2, y + switchDepth + switchHookDepth/2, 0))
        dim(top.item(1).startSketchPoint, top.item(1).endSketchPoint, orientation.VerticalDimensionOrientation, point(x + switchWidth/4, y + switchDepth + switchHookDepth/2,0))

        dim(center.item(2).endSketchPoint, top.item(0).startSketchPoint, orientation.HorizontalDimensionOrientation, point(x + switchWidth/4, y + switchDepth*0.75,0))
        dim(center.item(0).startSketchPoint, bottom.item(2).startSketchPoint, orientation.HorizontalDimensionOrientation, point(x + switchWidth/4, y + switchDepth/4,0))

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