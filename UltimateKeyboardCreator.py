# Author-Julian Pleines
# Description-Simple Script to create a 3D-Printable Keyboard

import traceback
import importlib
import importlib.util
import math
import os

import adsk.cam
import adsk.core
import adsk.fusion

from .Utils import updateLayoutData
from .FileParser import parseLayoutFile, getDefaultLayouts
from . import FitChecker
from . import Layout
from .KeyboardData import KeyboardObject, microcontrollers, microcontrollerPins
from .Frame import getFrames, getKeyboardPlateSize
from .Sketch import createSplit, createSplitLine

from .modules.frames.AbstractFrame import AbstractFrame


# Global list to keep all event handlers in scope.
handlers = []
progressSteps = 0
keyboardObject: KeyboardObject = KeyboardObject()
# holds all layouts in the layouts folder
layouts: dict = {}
# holds all frame modules
frames: dict = {}


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        keyboardCreator = cmdDefs.addButtonDefinition('KeyboardCreatorButtonId',
                                                      'UltimateKeyboardCreator',
                                                      'this is the tooltip')
        # Connect to the command created event.
        commandCreated = KCCommandCreatedEventHandler()
        keyboardCreator.commandCreated.add(commandCreated)
        handlers.append(commandCreated)

        # ui.messageBox("The UltimateKeyboardCreator is currently in alpha state, please be patient and expect bugs. Some features are missing and some maybe don't behave expected.\nSorry for the inconvenience.", "Notice")

        # Execute the command.
        keyboardCreator.execute()

        # Keep the script running.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class KCCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

        global keyboardObject
        global layouts
        global frames

        # Get the command
        cmd = eventArgs.command
        cmd.setDialogInitialSize(300, 400)
        cmd.setDialogMinimumSize(300, 400)
        cmd.okButtonText = "Create"

        # Get the CommandInputs collection to create new command inputs.
        cmdInputs = cmd.commandInputs

        # ---------------------------------- GENERAL TAB -------------------------------------------
        # set Keyboard specific settings needed to generate the Keyboard
        generalTab = cmdInputs.addTabCommandInput("generalTab", "General")
        generalChildren = generalTab.children

        printableBox = generalChildren.addBoolValueInput("makePrintableBox", "Make Printable", True, "", True)
        printableBox.tooltip = "Slices the Keyboard into printable parts"
        printableBox.tooltipDescription = "The printable Keyboard is sliced into printable sizes. The parts are equipped with alignment pins and split so they fit your printer"

        perspectiveCamerBox = generalChildren.addBoolValueInput("perspectiveCamerBox", "Perspective Camera", True, "", True)
        perspectiveCamerBox.tooltip = "After the Keyboard is created, a perspective camera is used, otherwise an orthographic camera"
        perspectiveCamerBox.tooltipDescription = "The default camera in CAD software is often the orthographic camera. While easier to model with, it doesn't look like the Model you would hold in your hands. The perspective camera is what you expect."

        advancedSettingsBox = generalChildren.addBoolValueInput("advancedSettingsBox", "Advanced Settings", True, "", False)
        advancedSettingsBox.tooltip = "Enables the advanced settings"
        advancedSettingsBox.tooltipDescription = "USE WITH CAUTION! \nThe advanced settings are for finetuning dimensions for the switches you are using, the spacing between switches (to create non-standard Keyboards) and other advanced values."
        
        advancedSettings = generalChildren.addGroupCommandInput("advancedSettings", "Advanced Settings")
        advancedSettings.isExpanded = True
        advancedSettings.isVisible = False
        advancedSettingsGroup = advancedSettings.children
        advancedSettingsGroup.addValueInput("switchWidth", "Switch Width", "mm", adsk.core.ValueInput.createByReal(1.4))
        advancedSettingsGroup.addValueInput("switchDepth", "Switch Depth", "mm", adsk.core.ValueInput.createByReal(1.4))

        parametricBox = advancedSettingsGroup.addBoolValueInput("parametricBox", "Parametric Model", True, "", False)
        parametricBox.tooltip = "Generates the Model as full parametric model"
        parametricBox.tooltipDescription = "Generates the sketches with parametric values, editable in the parameters Window. This makes it easy to tweak some settings, not needed if the general fit is good and you only want to create your own Frame"
        
        fixedSketchBox = advancedSettingsGroup.addBoolValueInput("fixedSketchBox", "Fixed Sketch", True, "", True)
        fixedSketchBox.tooltip = "Makes all sketch lines fixed"
        fixedSketchBox.tooltipDescription = "Generates the Sketches with parametric values, editable in the parameters Window. This makes it Easy to tweak some settings, not needed if the general fit is good and you only want to create your own Frame"
        
        frameBox = advancedSettingsGroup.addBoolValueInput("createFrameBox", "Create Frame", True, "", True)
        frameBox.tooltip = "Creates the frame for the Keyboard"
        frameBox.tooltipDescription = "If you ditch the frame creation, only the layout plate will be generated so it's easy to create your own frame."

        fitCheckerBox = advancedSettingsGroup.addBoolValueInput("fitCheckerBox", "Generate FitChecker", True, "", True)
        fitCheckerBox.tooltip = "Generates a small helper part to check the fit of the Switches"
        fitCheckerBox.tooltipDescription = ""

        # ---------------------------------- 3D PRINTER TAB ----------------------------------------
        printerTab = cmdInputs.addTabCommandInput("printerTab", "3D Printer")
        printerCildren = printerTab.children

        printerSize = printerCildren.addGroupCommandInput("printerSize", "Printer Build Volume")
        printerSize.isExpanded = True
        printerSize.isVisible = True
        printerSizeGroup = printerSize.children
        printerSizeGroup.addValueInput("printerWidthValue", "X", "mm", adsk.core.ValueInput.createByReal(20))
        printerSizeGroup.addValueInput("printerDepthValue", "Y", "mm", adsk.core.ValueInput.createByReal(20))

        # TODO make visible again if the feature exists
        fitOptimizationValue = printerCildren.addValueInput("fitOptimizationValue", "Fit Optimization", "mm", adsk.core.ValueInput.createByReal(0.0))
        fitOptimizationValue.isVisible = False
        fitOptimizationValue.tooltip = "Enlarges or reduces the hole for the switches"
        fitOptimizationValue.tooltipDescription = "Every Printer is different and an exact fit of all components isn't garanteed with a one-fits-all design. Just leave this value as 0mm, print the 'FitChecker' Body and test for the fit (or measure the hole for the Switch, the hole should be between 13.6mm and 13.8mm for a snug fit), than modify this value and check again until you are satisfied with the outcome."

        # ---------------------------------- KEYBOARD LAYOUT TAB -----------------------------------
        layoutTab = cmdInputs.addTabCommandInput("layoutTab", "Layout")
        layoutTab.isVisible = True
        layoutChildren = layoutTab.children

        keyboardLayoutDropdown = layoutChildren.addDropDownCommandInput("keyboardLayoutDropdown", "Keyboard Layout", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        keyboardLayoutDropdown.tooltip = "Select your desired keyboard layout"
        keyboardLayoutDropdown.tooltipDescription = "Select your keyboard layout from the list or choose a custom layout (to do this, go to http://www.keyboard-layout-editor.com and design your own, export it as json and import it here)"
        
        layouts = getDefaultLayouts()
        first = True
        for key in layouts:
            keyboardLayoutDropdown.listItems.add(key, first, "")
            first = False
        keyboardLayoutDropdown.listItems.add("Custom Layout", False, "")
        # TODO ONLY FOR DEBUGGING, DELETE LATER
        for layout in keyboardLayoutDropdown.listItems:
            if layout.name == "ISO 60% (62 Keys)":
                layout.isSelected = True

        fileButton = layoutChildren.addBoolValueInput("fileButton", "Layout JSON", False, "./resources/icons/Folder", False)
        fileButton.isVisible = False

        supportWidth = layoutChildren.addValueInput("supportWidthValue", "Support Keys wider than", "", adsk.core.ValueInput.createByReal(2.0))
        # TODO make visible again if the feature exists
        supportWidth.isVisible = False
        supportWidth.tooltip = "Support Keys that are wider than this value in units with stabilizers"
        supportWidth.tooltipDescription = "If a key is wider than one unit (default key size), jamming could become an issue. Stabilizers are available in 2u, 6.25u and 7u. (1 default unit is 19.05mm or 0.75inches)"

        stabilizersTypeDropdown = layoutChildren.addDropDownCommandInput("stabilizersTypeDropdown", "Support Type", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        # TODO make visible again if the feature exists
        stabilizersTypeDropdown.isVisible = False
        stabilizersTypeDropdown.tooltip = "Select the type of keysupport for long keys"
        stabilizersTypeDropdown.tooltipDescription = "Choose if you want to support keys by aftermarket Stabilizers, printed guide tracks or leave them unsupported"

        doubleSpaceSwitch = layoutChildren.addBoolValueInput("doubleSpaceSwitch", "Double Switch for Space", True, "", False)
        doubleSpaceSwitch.tooltip = "Use two switches for the spacebar instead of stabilizers"
        doubleSpaceSwitch.tooltipDescription = "It is an easy way prevent binding of the spacebar by using two switches instead of one switch with stabilizers. I you have spare switches, this may be cheaper than buying a seperate spacer. This is also a good way to stiffen up the spacebar."

        # keyboardLayoutTable = layoutChildren.addTableCommandInput("keyboardLayoutTable", "defaultLayouts", 3, "1:1:1")
        # keyboardLayoutTable.rowSpacing = 1
        # keyboardLayoutTable.columnSpacing = 1
        # keyboardLayoutTable.hasGrid = True
        # keyboardLayoutTable.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle

        # parse the keyboard layout
        parseLayoutFile(layouts[keyboardLayoutDropdown.selectedItem.name], keyboardObject)

        # ---------------------------------- FRAME TAB ---------------------------------------------
        frameTab = cmdInputs.addTabCommandInput("frameTab", "Frame")
        frameChildren = frameTab.children

        frameDropDown = frameChildren.addDropDownCommandInput("frameDropDown", "Frame Type", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        frames = getFrames()
        for key in frames:
            if frames[key].isModule is True:
                if key == "UKC Default":
                    frameDropDown.listItems.add(key, True, "/resources/icons/ModuleImport")
                else:
                    frameDropDown.listItems.add(key, first, "/resources/icons/ModuleImport")
            else:
                frameDropDown.listItems.add(key, first, "/resources/icons/BooleanNewComponent")
        
        keyboardObject.frameName = frameDropDown.selectedItem.name
        keyboardObject.frame = frames[keyboardObject.frameName]
        loadFrameModule(keyboardObject)

        # TODO implement this functionality
        screwList = keyboardObject.frameModule.getSupportedJoinOptions()
        joiningDropDown = frameChildren.addDropDownCommandInput("joiningDropDown", "Join with", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        for item in screwList:
            joiningDropDown.listItems.add(item, False, "")
        joiningDropDown.listItems.item(0).isSelected = True

        notice = '<font color="red"><b>Notice:</b> Pro Micro only supports 81 Keys</font>'
        controllerWarningText = frameChildren.addTextBoxCommandInput("controllerWarningText", "", notice, 1, True)
        controllerWarningText.isVisible = False

        microControllerDropDown = frameChildren.addDropDownCommandInput("microControllerDropDown", "Controller", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        microControllerDropDown.tooltip = "Choose the Microcontroller you are planning to use"
        for controller in microcontrollers:
            microControllerDropDown.listItems.add(controller, False, "")
        microControllerDropDown.listItems.item(0).isSelected = True

        selectedItem = microControllerDropDown.selectedItem
        if keyboardObject.keys > pinsToMaxSupportedKeys(microcontrollerPins[selectedItem.name]):
            notice = '<font color="red"><b>Notice:</b> ' + selectedItem.name + ' only supports ' + f"{pinsToMaxSupportedKeys(microcontrollerPins[selectedItem.name]):.0f}" + ' Keys</font>'
            controllerWarningText.formattedText = notice
            controllerWarningText.isVisible = True
        else:
            controllerWarningText.isVisible = False

        # ---------------------------------- KEYCAPS TAB -------------------------------------------
        # keycapsTab = cmdInputs.addTabCommandInput("keycapsTab", "Keycaps")
        # keycapsChildren = keycapsTab.children

        # keycapsTab.isVisible = False

        # Connect to the execute event.
        onExecute = KCCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        onChange = KCCommandInputChangedHandler()
        cmd.inputChanged.add(onChange)
        handlers.append(onChange)

        onPreview = KCPreviewHandler()
        cmd.executePreview.add(onPreview)
        handlers.append(onPreview)

        onDestroy = KCDestroyHandler()
        cmd.destroy.add(onDestroy)
        handlers.append(onDestroy)


# Event handler for the inputChanged event
class KCCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)

        app = adsk.core.Application.get()
        ui = app.userInterface
        inputs = adsk.core.CommandInputs.cast(eventArgs.firingEvent.sender.commandInputs)
        
        global keyboardObject
        global frames

        changedInput = eventArgs.input
        if changedInput.id == 'fileButton':
            button = adsk.core.BoolValueCommandInput.cast(inputs.itemById('fileButton'))
            button.isEnabled = False
            openFile()
            button.value = False
            button.isEnabled = True

        elif changedInput.id == "keyboardLayoutDropdown":
            dropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById("keyboardLayoutDropdown"))
            selectedItem = dropdown.selectedItem
            button = adsk.core.BoolValueCommandInput.cast(inputs.itemById("fileButton"))
            if selectedItem.name == "Custom Layout":
                button.isVisible = True
                keyboardObject.layoutName = "Custom Layout"
            else:
                button.isVisible = False
                keyboardObject.layoutName = selectedItem.name
                parseLayoutFile(layouts[selectedItem.name], keyboardObject)

        elif changedInput.id == 'makePrintableBox':
            checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('makePrintableBox'))
            tab = adsk.core.TabCommandInput.cast(inputs.itemById("printerTab"))
            keyboardObject.makePrintable = checkbox.value
            tab.isVisible = checkbox.value

        elif changedInput.id == 'advancedSettingsBox':
            checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById('advancedSettingsBox'))
            group = adsk.core.GroupCommandInput.cast(inputs.itemById("advancedSettings"))
            group.isVisible = checkbox.value

        elif changedInput.id == "frameDropDown":
            dropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById("frameDropDown"))
            selectedItem = dropdown.selectedItem
            keyboardObject.frameName = selectedItem.name
            keyboardObject.frame = frames[selectedItem.name]
            loadFrameModule(keyboardObject)

        elif changedInput.id == "doubleSpaceSwitch":
            checkbox = adsk.core.BoolValueCommandInput.cast(inputs.itemById("doubleSpaceSwitch"))
            keyboardObject.doubleSwitchForSpace = checkbox.value

        # if the layout is updated, maybe the controller isn't sufficent anymore
        if changedInput.id == "microControllerDropDown" or changedInput.id == "keyboardLayoutDropdown":
            dropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById("microControllerDropDown"))
            selectedItem = dropdown.selectedItem
            keyboardObject.microcontroller = selectedItem.name
            controllerWarningText = adsk.core.TextBoxCommandInput.cast(inputs.itemById('controllerWarningText'))
            if keyboardObject.keys > pinsToMaxSupportedKeys(microcontrollerPins[selectedItem.name]):
                notice = '<font color="red"><b>Notice:</b> ' + selectedItem.name + ' only supports ' + f"{pinsToMaxSupportedKeys(microcontrollerPins[selectedItem.name]):.0f}" + ' Keys</font>'
                controllerWarningText.formattedText = notice
                controllerWarningText.isVisible = True
            else:
                controllerWarningText.isVisible = False


class KCDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class KCCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        global keyboardObject

        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
            root = design.rootComponent

            inputs = adsk.core.CommandInputs.cast(eventArgs.command.commandInputs)

            progressDialog = ui.createProgressDialog()
            progressDialog.isBackgroundTranslucent = False
            progressDialog.isCancelButtonShown = False
            updateLayoutData(keyboardObject)
            totalSteps = keyboardObject.keys * 3
            if adsk.core.BoolValueCommandInput.cast(inputs.itemById("fitCheckerBox")).value is True:
                totalSteps += 9 * 3
            progressDialog.show("Keyboard creation in progress", "Percentage: %p, Current Value: %v, Total steps: %m", 0, totalSteps, 1)

            keyboardObject.printerWidth = adsk.core.ValueCommandInput.cast(inputs.itemById("printerWidthValue")).value
            keyboardObject.printerDepth = adsk.core.ValueCommandInput.cast(inputs.itemById("printerDepthValue")).value
            keyboardObject.switchWidth = adsk.core.ValueCommandInput.cast(inputs.itemById("switchWidth")).value
            keyboardObject.switchDepth = adsk.core.ValueCommandInput.cast(inputs.itemById("switchDepth")).value
            keyboardObject.parametricModel = adsk.core.BoolValueCommandInput.cast(inputs.itemById("parametricBox")).value
            keyboardObject.fixedSketch = adsk.core.BoolValueCommandInput.cast(inputs.itemById("fixedSketchBox")).value

            # --------------------------- FITCHECKER CREATION  ------------------------------------
            if adsk.core.BoolValueCommandInput.cast(inputs.itemById("fitCheckerBox")).value is True:
                FitChecker.create(progressDialog, root, keyboardObject)

            # --------------------------- LAYOUT CREATION  ----------------------------------------
            # create new occurence in the root component for a new component
            trans = adsk.core.Matrix3D.create()
            occ = root.occurrences.addNewComponent(trans)

            # get the component from the occurence
            comp = occ.component
            comp.name = keyboardObject.layoutName + " Keyboard"
        
            Layout.create(progressDialog, comp, keyboardObject)

            # --------------------------- FRAME CREATION  -----------------------------------------
            # frame is created by a python module
            if keyboardObject.frame.isModule:
                progressDialog.message = "Creating Frame"
                selectedJoinOption = adsk.core.DropDownCommandInput.cast(inputs.itemById("joiningDropDown")).selectedItem.name
                keyboardObject.frameModule.generateFrame(keyboardObject, comp, selectedJoinOption)
            # frame is based on a master component
            else:
                app = adsk.core.Application.get()
                design = adsk.fusion.Design.cast(app.activeProduct)
                importManager = app.importManager
                archiveFileName = os.path.dirname(__file__) + "/resources/models/frames/" + keyboardObject.frame.filePath
                archiveOptions = importManager.createFusionArchiveImportOptions(archiveFileName)
                success = importManager.importToTarget(archiveOptions, comp)
                if success is not True:
                    ui.messageBox("Importing of the frame was not successful, please check the model!", "Import Error")
                
                occ.isGrounded = True
                proxy = comp.occurrences.itemByName(keyboardObject.frame.filename[:-4] + ":1").createForAssemblyContext(occ)
                proxy.isGrounded = True

                # setting the user Parameters with the right values
                dimension = getKeyboardPlateSize(keyboardObject, comp)
                param1 = design.userParameters.itemByName("LayoutWidth")
                param2 = design.userParameters.itemByName("LayoutHeight")
                param3 = design.userParameters.itemByName("PlateThickness")
                param4 = design.userParameters.itemByName("InfillVoids")
                if param1 is not None and param2 is not None and param3 is not None and param4 is not None:
                    param1.value = dimension[0]
                    param2.value = dimension[1]
                    param3.value = keyboardObject.plateThickness
                else:
                    # TODO create messagebox -> Model does not fulfill requirements
                    print("else")
                
                # create new sketch for the layout plate
                infillVoids = True if design.userParameters.itemByName("InfillVoids").value >= 1 else False
                if infillVoids is True:
                    if design.userParameters.itemByName("VoidHeight") is None:
                        # TODO create messagebox -> Model does not fulfill requirements
                        print("else")
                    else:
                        voidHeight = design.userParameters.itemByName("VoidHeight").value
            # --------------------------- COMBINE BODIES ------------------------------------------
            # If the Frame is created by a Model, combining the Top-Frame and the layoutPlate is done
                plate = comp.bRepBodies.itemByName("Layout Plate")
                if plate is None:
                    print("Plate not found...")
                # topFrame = comp.allOccurrences.itemByName(keyboardObject.frame.filename[:-4]).component.bRepBodies.itemByName("Top")
                topFrame = comp.allOccurrences.itemByName(keyboardObject.frame.filename[:-4] + ":1").bRepBodies.itemByName("Top")
                if topFrame is not None:
                    collection = adsk.core.ObjectCollection.create()
                    collection.add(topFrame)
                    combineFeatureInput = comp.features.combineFeatures.createInput(plate, collection)
                    combineFeatureInput.isKeepToolBodies = True
                    # combineFeatureInput.isNewComponent = False
                    comp.features.combineFeatures.add(combineFeatureInput)
                    topFrame.isLightBulbOn = False
                    plate.name = "Top Frame"
                else:
                    print("Body not found!")

                # occur: adsk.fusion.Occurrence
                # for occur in comp.allOccurrences:
                #     print(occur.name)
                    
            # --------------------------- KEYBOARD SPLITTING --------------------------------------
            # get overall dimension for the keyboard with frame, the height is not considered
            # to be problematic

            box = comp.bRepBodies.itemByName("Top Frame").boundingBox
            width = box.maxPoint.x - box.minPoint.x
            depth = box.maxPoint.y - box.minPoint.y
            leftBorderWidth = - box.minPoint.x
            lowerBorderWith = - box.minPoint.y
            max = width if width >= depth else depth
            min = width if width <= depth else depth
            maxPrinter = keyboardObject.printerDepth if keyboardObject.printerDepth >= keyboardObject.printerWidth else keyboardObject.printerWidth
            minPrinter = keyboardObject.printerDepth if keyboardObject.printerDepth <= keyboardObject.printerWidth else keyboardObject.printerWidth
            if max >= maxPrinter or min >= minPrinter:
                # check how many splits and in wich direction are needed
                longSplit = math.ceil(max / maxPrinter)
                shortSplit = math.ceil(min / minPrinter)
                print("long:" + str(longSplit))
                print("short:" + str(shortSplit))

                if longSplit > 1 or shortSplit > 1:
                    sketches = comp.sketches
                    xyPlane = comp.xYConstructionPlane
                    splitSketch = sketches.add(xyPlane)
                    splitSketch.name = "Split"
                    createSplit(splitSketch, keyboardObject, width, depth, leftBorderWidth, lowerBorderWith)
                    
                    if keyboardObject.frame.isModule:
                        bottomFrame = comp.bRepBodies.itemByName("Bottom Frame")
                    else:
                        bottomFrameOriginal = comp.allOccurrences.itemByName(keyboardObject.frame.filename[:-4] + ":1").bRepBodies.itemByName("Bottom")
                        bottomFrameOriginal.isLightBulbOn = False
                        bottomFrame = bottomFrameOriginal.copyToComponent(occ)

                    bodiesToSplit = adsk.core.ObjectCollection.create()
                    bodiesToSplit.add(comp.bRepBodies.itemByName("Top Frame"))
                    if keyboardObject.splitBottomStraight is False:
                        bodiesToSplit.add(bottomFrame)
                    else:
                        straightSplitSketch = sketches.add(xyPlane)
                        straightSplitSketch.name = "Straight Split"
                        createSplitLine(straightSplitSketch, keyboardObject, width, depth, leftBorderWidth, lowerBorderWith)
                        splittingTool = straightSplitSketch.sketchCurves.sketchLines.item(0)
                        splitBodyFeatureInput = comp.features.splitBodyFeatures.createInput(bottomFrame, splittingTool, True)
                        splitBodyFeature = comp.features.splitBodyFeatures.add(splitBodyFeatureInput)
                        i = 1
                        for body in splitBodyFeature.bodies:
                            body.name = "Bottom Frame (Part " + str(i) + ")"
                            i += 1
                    splittingTool = splitSketch.sketchCurves.sketchLines.item(0)
                    splitBodyFeatureInput = comp.features.splitBodyFeatures.createInput(bodiesToSplit, splittingTool, True)
                    splitBodyFeature = comp.features.splitBodyFeatures.add(splitBodyFeatureInput)
                    body: adsk.fusion.BRepBody
                    i = 1
                    for body in splitBodyFeature.bodies:
                        body.name = "Top Frame (Part " + str(i) + ")"
                        i += 1
                    
            else:
                # no split is needed
                print("no split is needed")
            # --------------------------- KEYCAP CREATION -----------------------------------------
            # This is not part of the first Release-Version

            # --------------------------- ADDING SWITCHES -----------------------------------------
            # this step is only for demonstration purposes
            # importManager = app.importManager
            # archiveFileName = "C:/Users/Julian/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts/UltimateKeyboardCreator/resources/models/Test.f3d"
            # archiveOptions = importManager.createFusionArchiveImportOptions(archiveFileName)
            # importManager.importToTarget(archiveOptions, root)

            progressDialog.hide()
            camera = app.activeViewport.camera
            isPerspectiveCamera = adsk.core.BoolValueCommandInput.cast(inputs.itemById("perspectiveCamerBox")).value
            if isPerspectiveCamera:
                camera.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
            else:
                camera.cameraType = adsk.core.CameraTypes.OrthographicCameraType
            camera.viewOrientation = adsk.core.ViewOrientations.IsoTopRightViewOrientation
            camera.upVector = adsk.core.Vector3D.create(0, 0, 1)
            camera.isFitView = True
            app.activeViewport.camera = camera
            app.activeViewport.fit()
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class KCPreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)


def openFile():
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        dlg = ui.createFileDialog()
        dlg.title = 'Open JSON File'
        dlg.filter = 'JSON File (*.json);;All Files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        global keyboardObject
        parseLayoutFile(dlg.filename, keyboardObject)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def pinsToMaxSupportedKeys(pins: float) -> float:
    # maximum achievable keycount is the square of the half of all pins
    # but reality doesn't let you use half pins, that means if the available
    # pincount is odd we have to do it a little different.
    return math.ceil(pins / 2) * math.floor(pins / 2)


def loadFrameModule(keyboardObject: KeyboardObject):
    if keyboardObject.frame.isModule:
        framename = keyboardObject.frame.filename
        if framename.endswith("_"):
            cls = getattr(importlib.import_module(".modules.frames." + framename, __name__), "Frame")
        else:
            cls = getattr(importlib.import_module(".modules.frames." + framename, __name__), framename)
        keyboardObject.frameModule: AbstractFrame = cls()
    else:
        # nothing to do at this moment
        print("load fusion file")
                
  
def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById('KeyboardCreatorButtonId')
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
