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

from .LayoutFileParser import parseFile, getDefaultLayouts
from . import FitChecker
from . import Layout
from .KeyboardData import KeyboardData, microcontrollers, microcontrollerPins
from .Frame import getFrames, getKeyboardPlateSize

from .modules.frames.AbstractFrame import AbstractFrame


# Global list to keep all event handlers in scope.
handlers = []
progressSteps = 0
keyboardData: KeyboardData = KeyboardData()
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

        global keyboardData
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
        # TODO make visible again if the feature exists
        printableBox.isVisible = False
        printableBox.tooltip = "Slices the Keyboard into printable parts"
        printableBox.tooltipDescription = "The printable Keyboard is sliced into printable sizes. The parts are equipped with alignment pins and split so they fit your printer"

        advancedSettingsBox = generalChildren.addBoolValueInput("advancedSettingsBox", "Advanced Settings", True, "", False)
        advancedSettingsBox.tooltip = "Enables the advanced settings"
        advancedSettingsBox.tooltipDescription = "USE WITH CAUTION! \nThe advanced settings are for finetuning dimensions for the switches you are using, the spacing between switches (to create non-standard Keyboards) and other advances values."
        
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
        # TODO make visible again if the feature exists
        printerTab.isVisible = False
        printerCildren = printerTab.children

        printerSize = printerCildren.addGroupCommandInput("printerSize", "Printer Build Volume")
        printerSize.isExpanded = True
        printerSize.isVisible = True
        printerSizeGroup = printerSize.children
        printerSizeGroup.addValueInput("printerWidthValue", "Width", "mm", adsk.core.ValueInput.createByReal(20))
        printerSizeGroup.addValueInput("printerDepthValue", "Depth", "mm", adsk.core.ValueInput.createByReal(20))
        printerSizeGroup.addValueInput("printerHeightValue", "Height", "mm", adsk.core.ValueInput.createByReal(20))

        fitOptimizationValue = printerCildren.addValueInput("fitOptimizationValue", "Fit Optimization", "mm", adsk.core.ValueInput.createByReal(0.0))
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
        # TODO make visible again if the feature exists
        doubleSpaceSwitch.isVisible = False
        doubleSpaceSwitch.tooltip = "Use two switches for the spacebar instead of stabilizers"
        doubleSpaceSwitch.tooltipDescription = "It is an easy way prevent binding of the spacebar by using two switches instead of one switch with stabilizers. I you have spare switches, this may be cheaper than buying a seperate spacer. This is also a good way to stiffen up the spacebar."

        # keyboardLayoutTable = layoutChildren.addTableCommandInput("keyboardLayoutTable", "defaultLayouts", 3, "1:1:1")
        # keyboardLayoutTable.rowSpacing = 1
        # keyboardLayoutTable.columnSpacing = 1
        # keyboardLayoutTable.hasGrid = True
        # keyboardLayoutTable.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle

        # parse the keyboard layout
        parseFile(layouts[keyboardLayoutDropdown.selectedItem.name], keyboardData)

        # ---------------------------------- FRAME TAB ---------------------------------------------
        frameTab = cmdInputs.addTabCommandInput("frameTab", "Frame")
        frameChildren = frameTab.children

        frameDropDown = frameChildren.addDropDownCommandInput("frameDropDown", "Frame Type", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        frames = getFrames()
        for key in frames:
            if key == "UKC Default":
                frameDropDown.listItems.add(key, True, "")
            else:
                frameDropDown.listItems.add(key, first, "")
        
        keyboardData.frameName = frameDropDown.selectedItem.name
        keyboardData.frame = frames[keyboardData.frameName]
        loadFrameModule(keyboardData)

        # TODO implement this functionality
        screwList = keyboardData.frameModule.getSupportedJoinOptions()
        joiningDropDown = frameChildren.addDropDownCommandInput("joiningDropDown", "Join with", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        for item in screwList:
            joiningDropDown.listItems.add(item, False, "")
        joiningDropDown.listItems.item(0).isSelected = True

        # TODO show this kind of Notice only if the selected keyboard has mor keys than the controller supports without extensions
        notice = '<font color="red"><b>Notice:</b> Pro Micro only supports 81 Keys</font>'
        controllerWarningText = frameChildren.addTextBoxCommandInput("controllerWarningText", "", notice, 1, True)
        controllerWarningText.isVisible = False

        microControllerDropDown = frameChildren.addDropDownCommandInput("microControllerDropDown", "Controller", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        microControllerDropDown.tooltip = "Choose the Microcontroller you are planning to use"
        for controller in microcontrollers:
            microControllerDropDown.listItems.add(controller, False, "")
        microControllerDropDown.listItems.item(0).isSelected = True

        selectedItem = microControllerDropDown.selectedItem
        if keyboardData.keys > pinsToMaxSupportedKeys(microcontrollerPins[selectedItem.name]):
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
        
        global keyboardData
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
                keyboardData.layoutName = "Custom Layout"
            else:
                button.isVisible = False
                keyboardData.layoutName = selectedItem.name
                parseFile(layouts[selectedItem.name], keyboardData)

        elif changedInput.id == 'makePrintableBox':
            button = adsk.core.BoolValueCommandInput.cast(inputs.itemById('makePrintableBox'))
            tab = adsk.core.TabCommandInput.cast(inputs.itemById("printerTab"))
            if changedInput.value:
                tab.isVisible = True
            else:
                tab.isVisible = False

        elif changedInput.id == 'advancedSettingsBox':
            button = adsk.core.BoolValueCommandInput.cast(inputs.itemById('advancedSettingsBox'))
            group = adsk.core.GroupCommandInput.cast(inputs.itemById("advancedSettings"))
            if changedInput.value:
                group.isVisible = True
            else:
                group.isVisible = False

        elif changedInput.id == "frameDropDown":
            dropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById("frameDropDown"))
            selectedItem = dropdown.selectedItem
            keyboardData.frameName = selectedItem.name
            keyboardData.frame = frames[selectedItem.name]
            loadFrameModule(keyboardData)

        elif changedInput.id == "microControllerDropDown":
            dropdown = adsk.core.DropDownCommandInput.cast(inputs.itemById("microControllerDropDown"))
            selectedItem = dropdown.selectedItem
            keyboardData.microcontroller = selectedItem.name
            controllerWarningText = adsk.core.TextBoxCommandInput.cast(inputs.itemById('controllerWarningText'))
            if keyboardData.keys > pinsToMaxSupportedKeys(microcontrollerPins[selectedItem.name]):
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

        global keyboardData

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
            totalSteps = keyboardData.keys * 3
            if adsk.core.BoolValueCommandInput.cast(inputs.itemById("fitCheckerBox")).value is True:
                totalSteps += 9 * 3
            progressDialog.show("Keyboard creation in progress", "Percentage: %p, Current Value: %v, Total steps: %m", 0, totalSteps, 1)

            keyboardData.switchWidth = adsk.core.ValueCommandInput.cast(inputs.itemById("switchWidth")).value
            keyboardData.switchDepth = adsk.core.ValueCommandInput.cast(inputs.itemById("switchDepth")).value
            keyboardData.parametricModel = adsk.core.BoolValueCommandInput.cast(inputs.itemById("parametricBox")).value
            keyboardData.fixedSketch = adsk.core.BoolValueCommandInput.cast(inputs.itemById("fixedSketchBox")).value

            # --------------------------- FITCHECKER CREATION  ------------------------------------
            if adsk.core.BoolValueCommandInput.cast(inputs.itemById("fitCheckerBox")).value is True:
                FitChecker.create(progressDialog, root, keyboardData)

            # --------------------------- LAYOUT CREATION  ----------------------------------------
            # create new occurence in the root component for a new component
            trans = adsk.core.Matrix3D.create()
            occ = root.occurrences.addNewComponent(trans)

            # get the component from the occurence
            comp = occ.component
            comp.name = keyboardData.layoutName + " Keyboard"
        
            Layout.create(progressDialog, comp, keyboardData)

            # --------------------------- FRAME CREATION  -----------------------------------------
            if keyboardData.frame.isModule:
                progressDialog.message = "Creating Frame"
                selectedJoinOption = adsk.core.DropDownCommandInput.cast(inputs.itemById("joiningDropDown")).selectedItem.name
                keyboardData.frameModule.generateFrame(keyboardData, comp, selectedJoinOption)
            else:
                app = adsk.core.Application.get()
                design = adsk.fusion.Design.cast(app.activeProduct)
                # root = design.rootComponent
                root = comp
                importManager = app.importManager
                archiveFileName = os.path.dirname(__file__) + "/resources/models/frames/" + keyboardData.frame.filename
                archiveOptions = importManager.createFusionArchiveImportOptions(archiveFileName)
                importManager.importToTarget(archiveOptions, root)

                # setting the user Parameters with the right values
                dimension = getKeyboardPlateSize(keyboardData, comp)
                param1 = design.userParameters.itemByName("LayoutWidth")
                param2 = design.userParameters.itemByName("LayoutHeight")
                param3 = design.userParameters.itemByName("PlateThickness")
                param4 = design.userParameters.itemByName("InfillVoids")
                if param1 is not None and param2 is not None and param3 is not None and param4 is not None:
                    param1.value = dimension[0]
                    param2.value = dimension[1]
                    param3.value = keyboardData.plateThickness
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
                # topFrame = comp.allOccurrences.itemByName(keyboardData.frame.filename[:-4]).component.bRepBodies.itemByName("Top")
                topFrame = comp.allOccurrences.itemByName(keyboardData.frame.filename[:-4] + ":1").bRepBodies.itemByName("Top")
                if topFrame is not None:
                    collection = adsk.core.ObjectCollection.create()
                    collection.add(topFrame)
                    combineFeatureInput = comp.features.combineFeatures.createInput(plate, collection)
                    combineFeatureInput.isKeepToolBodies = True
                    # combineFeatureInput.isNewComponent = False
                    comp.features.combineFeatures.add(combineFeatureInput)
                    topFrame.isLightBulbOn = False
                    plate.name = "Plate"
                else:
                    print("Body not found!")

                occ: adsk.fusion.Occurrence
                for occ in comp.allOccurrences:
                    print(occ.name)
                    
            # --------------------------- FRAME SPLITTING -----------------------------------------
            # TODO split the frame and any other body neccessary

            # --------------------------- KEYCAP CREATION -----------------------------------------
            # This is not part of the first Release-Version

            # --------------------------- ADDIND SWITCHES -----------------------------------------
            # this step is only for demonstration purposes
            # importManager = app.importManager
            # archiveFileName = "C:/Users/Julian/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts/UltimateKeyboardCreator/resources/models/Test.f3d"
            # archiveOptions = importManager.createFusionArchiveImportOptions(archiveFileName)
            # importManager.importToTarget(archiveOptions, root)

            progressDialog.hide()
            app.activeViewport.fit()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        adsk.terminate()


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
        global keyboardData
        parseFile(dlg.filename, keyboardData)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def pinsToMaxSupportedKeys(pins: float) -> float:
    # maximum achievable keycount is the square of the half of all pins
    # but reality doesn't let you use half pins, that means if the available
    # pincount is odd we have to do it a little different.
    return math.ceil(pins / 2) * math.floor(pins / 2)


def loadFrameModule(keyboardData: KeyboardData):
    if keyboardData.frame.isModule:
        framename = keyboardData.frame.filename
        if framename.endswith("_"):
            cls = getattr(importlib.import_module(".modules.frames." + framename, __name__), "Frame")
        else:
            cls = getattr(importlib.import_module(".modules.frames." + framename, __name__), framename)
        keyboardData.frameModule: AbstractFrame = cls()
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
