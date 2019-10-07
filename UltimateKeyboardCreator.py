#Author-Julian Pleines
#Description-Simple Script to create a 3D-Printable Keyboard

# from sketchCreation import *
from .sketchCreation import *
from .parser import *
import adsk.core, adsk.fusion, adsk.cam, traceback
import io, json, types, os, sys, math

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []
layout = []
layoutName = "ANSI 104 (100%)"

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
#        sel = ui.activeSelections.item(0).entity.objectType
#        ui.messageBox("Type: " + sel)

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

        global layout
        
        # Get the command
        cmd = eventArgs.command
        cmd.okButtonText = "Create"
        
        #cmd.setDialogInitialSize()
        
        # Get the CommandInputs collection to create new command inputs.
        cmdInputs = cmd.commandInputs

        
        #---------------------------------- GENERAL TAB -------------------------------------------
        #set Keyboard specific settings needed to generate the Keyboard
        generalTab = cmdInputs.addTabCommandInput("generalTab", "General")
        generalChildren = generalTab.children

        printableBox = generalChildren.addBoolValueInput("makePrintableBox", "Make Printable", True, "", True)
        printableBox.tooltip = "Slices the Keyboard into printable parts"
        printableBox.tooltipDescription = "The printable Keyboard is sliced into printable sizes. The parts are equipped with alignment pins and split so they fit your printer"

        expertModeBox = generalChildren.addBoolValueInput("expertModeBox", "Expert Mode", True, "", False)
        expertModeBox.tooltip = "Enables the Expert mode"
        expertModeBox.tooltipDescription = "USE WITH CAUTION! \nThe Expert mode lets you finetune dimensions for the switches you are using, the spacing between switches (to create non-standard Keyboards) and other advances values."
        
        expertSettings = generalChildren.addGroupCommandInput("expertSettings", "Expert Settings")
        expertSettings.isExpanded = True
        expertSettings.isVisible = False
        expertSettingsGroup = expertSettings.children
        expertSettingsGroup.addValueInput("switchWidth", "Switch Width","mm",  adsk.core.ValueInput.createByReal(1.4))
        expertSettingsGroup.addValueInput("switchDepth", "Switch Depth","mm",  adsk.core.ValueInput.createByReal(1.4))
        
        parametricBox = expertSettingsGroup.addBoolValueInput("parametricBox", "Parametric Model", True, "", False)
        parametricBox.tooltip = "Generates the Model as full parametric model"
        parametricBox.tooltipDescription = "Generates the sketches with parametric values, editable in the parameters Window. This makes it easy to tweak some settings, not needed if the general fit is good and you only want to create your own Frame"
        
        fixedSketchBox = expertSettingsGroup.addBoolValueInput("fixedSketchBox", "Fixed Sketch", True, "", True)
        fixedSketchBox.tooltip = "Makes all sketch lines fixed"
        # fixedSketchBox.tooltipDescription = "Generates the Sketches with parametric values, editable in the parameters Window. This makes it Easy to tweak some settings, not needed if the general fit is good and you only want to create your own Frame"
        
        frameBox = expertSettingsGroup.addBoolValueInput("createFrameBox", "Create Frame", True, "", True)
        frameBox.tooltip = "Creates the frame for the Keyboard"
        frameBox.tooltipDescription = "If you ditch the frame creation, only the layout plate will be generated so it's easy to create your own frame."

        fitCheckerBox = expertSettingsGroup.addBoolValueInput("fitCheckerBox", "Generate FitChecker", True, "", True)
        fitCheckerBox.tooltip = "Generates a small helper part to check the fit of the Switches"
        fitCheckerBox.tooltipDescription = ""

        #---------------------------------- 3D PRINTER TAB ----------------------------------------
        printerTab = cmdInputs.addTabCommandInput("printerTab", "3D Printer")
        printerCildren = printerTab.children

        printerSize = printerCildren.addGroupCommandInput("printerSize", "Printer Build Volume")
        printerSize.isExpanded = True
        printerSize.isVisible = True
        printerSizeGroup = printerSize.children
        printerSizeGroup.addValueInput("printerWidthValue", "Width","mm",  adsk.core.ValueInput.createByReal(20))
        printerSizeGroup.addValueInput("printerDepthValue", "Depth","mm",  adsk.core.ValueInput.createByReal(20))
        printerSizeGroup.addValueInput("printerHeightValue", "Height","mm",  adsk.core.ValueInput.createByReal(20))
        
        fitOptimizationValue = printerCildren.addValueInput("fitOptimizationValue", "Fit Optimization", "mm", adsk.core.ValueInput.createByReal(0.0))
        fitOptimizationValue.tooltip = "Enlarges or reduces the hole for the switches"
        fitOptimizationValue.tooltipDescription = "Every Printer is different and an exact fit of all components isn't garanteed with a one-fits-all design. Just leave this value as 0mm, print the 'FitChecker' Body and test for the fit (or measure the hole for the Switch, the hole should be between 13.6mm and 13.8mm for a snug fit), than modify this value and check again until you are satisfied with the outcome."
        

        #---------------------------------- KEYBOARD LAYOUT TAB -----------------------------------
        layoutTab = cmdInputs.addTabCommandInput("layoutTab", "Layout")
        layoutTab.isVisible = True
        layoutChildren = layoutTab.children
        
        keyboardLayoutDropdown = layoutChildren.addDropDownCommandInput("keyboardLayoutDropdown", "Keyboard Layout", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        keyboardLayoutDropdown.tooltip = "Select your desired keyboard layout"
        keyboardLayoutDropdown.tooltipDescription = "Select your keyboard layout from the list or choose a custom layout (to do this, go to http://www.keyboard-layout-editor.com and design your own, export it as json and import it here)"
        keyboardLayoutDropdown.listItems.add("ISO 105 (100%)", False, "")
        keyboardLayoutDropdown.listItems.add("ANSI 104 (100%)", True, "")
        keyboardLayoutDropdown.listItems.add("ANSI 104 Big-Ass (100%)", False, "")
        keyboardLayoutDropdown.listItems.add("ISO 88 (80%)", False, "")
        keyboardLayoutDropdown.listItems.add("ANSI 87 (80%)", False, "")
        keyboardLayoutDropdown.listItems.add("Keycool 84 (75%)", False, "")
        keyboardLayoutDropdown.listItems.add("ISO 62 (60%)", False, "")
        keyboardLayoutDropdown.listItems.add("ANSI 61 (60%)", False, "")
        keyboardLayoutDropdown.listItems.add("Custom Layout", False, "")

        fileButton = layoutChildren.addBoolValueInput("fileButton","Layout JSON", False, "./resources/Icons/Folder", False)
        fileButton.isVisible = False

        doubleSpaceSwitch = layoutChildren.addBoolValueInput("doubleSpaceSwitch", "Double Switch for Space", True, "", False)
        doubleSpaceSwitch.tooltip = "Use two switches for the spacebar instead of stabilizers"
        doubleSpaceSwitch.tooltipDescription = "It is an easy way prevent binding of the spacebar by using two switches instead of one switch with stabilizers. I you have spare switches, this may be cheaper than buying a seperate spacer. This is also a good way to stiffen up the spacebar."

        # keyboardLayoutTable = layoutChildren.addTableCommandInput("keyboardLayoutTable", "Layouts", 3, "1:1:1")
        # keyboardLayoutTable.rowSpacing = 1
        # keyboardLayoutTable.columnSpacing = 1
        # keyboardLayoutTable.hasGrid = True
        # keyboardLayoutTable.tablePresentationStyle = adsk.core.TablePresentationStyles.itemBorderTablePresentationStyle

        #---------------------------------- FRAME TAB ---------------------------------------------
        frameTab = cmdInputs.addTabCommandInput("frameTab", "Frame")
        frameChildren = frameTab.children

        frameDropDown = frameChildren.addDropDownCommandInput("frameDropDown", "Frame Type", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
        frameDropDown.listItems.add("UKC Default", True, "")
        
        #---------------------------------- KEYCAPS TAB -------------------------------------------
        keycapsTab = cmdInputs.addTabCommandInput("keycapsTab", "Keycaps")
        keycapsChildren = keycapsTab.children

        keycapsTab.isVisible = False
        
        

        layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ANSI104.json")


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


        ######################### ONLY FOR DEBUGGING ##################################
        #openFile()
        
 
# Event handler for the inputChanged event
class KCCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)
        
        app = adsk.core.Application.get()
        ui  = app.userInterface
        inputs = adsk.core.CommandInputs.cast(eventArgs.firingEvent.sender.commandInputs)

        global layoutName
        global layout

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
                layoutName = "Custom Layout"
            else:
                button.isVisible = False
                layoutName = selectedItem.name


            if selectedItem.name == "ISO 105 (100%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ISO105.json")
            if selectedItem.name == "ANSI 104 (100%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ANSI104.json")
            if selectedItem.name == "ANSI 104 Big-Ass (100%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ANSI104BIGASS.json")
            if selectedItem.name == "ISO 88 (80%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ISO88.json")
            if selectedItem.name == "ANSI 87 (80%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ANSI87.json")
            if selectedItem.name == "Keycool 84 (75%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/KEYCOOL84.json")
            if selectedItem.name == "ISO 62 (60%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ISO62.json")
            if selectedItem.name == "ANSI 61 (60%)":
                layout = parseFile(os.path.dirname(__file__) + "/resources/Layouts/ANSI61.json")

        elif changedInput.id == 'makePrintableBox':
            button = adsk.core.BoolValueCommandInput.cast(inputs.itemById('makePrintableBox'))
            tab = adsk.core.TabCommandInput.cast(inputs.itemById("printerTab"))
            if changedInput.value == True:
                tab.isVisible = True
            else:
                tab.isVisible = False
        
        elif changedInput.id == 'expertModeBox':
            button = adsk.core.BoolValueCommandInput.cast(inputs.itemById('expertModeBox'))
            group = adsk.core.GroupCommandInput.cast(inputs.itemById("expertSettings"))
            if changedInput.value == True:
                group.isVisible = True
            else:
                group.isVisible = False      

                
class KCDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
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

        global layoutName
        global layout
        
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            progressDialog = ui.createProgressDialog()
            progressDialog.isBackgroundTranslucent = False
            progressDialog.isCancelButtonShown = False
            progressDialog.show("Keyboard creation in progress", "Percentage: %p, Current Value: %v, Total steps: %m", 0,100, 1)
            

            design.designType = adsk.fusion.DesignTypes.ParametricDesignType

            inputs = adsk.core.CommandInputs.cast(eventArgs.command.commandInputs)
            root = design.rootComponent
            
            #create new occurence in the root component for a new component
            trans = adsk.core.Matrix3D.create()
            occ = root.occurrences.addNewComponent(trans)

            #get the component from the occurence
            comp = occ.component
            comp.name = layoutName + " Keyboard"

            #create a new sketch on the xyPlane and draw a circle
            sketches = comp.sketches
            xyPlane = comp.xYConstructionPlane
            rowNumber = 1
            switchWidth = adsk.core.ValueCommandInput.cast(inputs.itemById("switchWidth"))
            switchDepth = adsk.core.ValueCommandInput.cast(inputs.itemById("switchDepth"))
            parametricModel = adsk.core.BoolValueCommandInput.cast(inputs.itemById("parametricBox"))
            fixedSketch = adsk.core.BoolValueCommandInput.cast(inputs.itemById("fixedSketchBox"))


            # --------------------------- MULTY LAYOUT SKETCH ATTEMPT -----------------------------
            # for row in layout:
            #     sketch = sketches.add(xyPlane)
            #     sketch.name = "Layout plate with " + layoutName + " Layout - (Layer " + str(rowNumber) + ")"
            #     sketch.isComputeDeferred = True
            #     for entry in row:
            #         createSwtichPocket(sketch, entry[0]*19.05, -entry[1]*19.05, switchWidth.value, switchDepth.value, 0.5, 0.15, parametricModel.value, fixedSketch.value)
            #     rowNumber += 1
            #     sketch.isComputeDeferred = False


            # ---------------------------- ONE LAYOUT SKETCH ATTEMPT ------------------------------
            sketch = sketches.add(xyPlane)
            sketch.name = "Layout plate with " + layoutName + " Layout - (Layer " + str(rowNumber) + ")"
            sketch.isComputeDeferred = True

            maxX = 0.0
            maxY = 0.0
            # creating the switch pockets
            for row in layout:
                for entry in row:
                    createSwtichPocket(sketch, entry[0]*1.905, -(entry[1] + 1)*1.905, switchWidth.value, switchDepth.value, 0.5, 0.15, parametricModel.value, fixedSketch.value)
                    if entry[0] > maxX:
                        maxX = math.ceil(entry[0])
                    if entry[1] > maxY:
                        maxY = math.ceil(entry[1])
                rowNumber += 1
                print(rowNumber)
            # creating the outer border
            print(maxX)
            createPlateBorder(sketch, (maxX+1)*1.905, (maxY+1)*1.905, parametricModel.value, fixedSketch.value)
            sketch.isComputeDeferred = False

            # --------------------------------- EXTRUDE TESTS ------------------------------------
            # extInput = comp.features.extrudeFeatures.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            # distance = adsk.core.ValueInput.createByReal(10.0)
            # extInput.setDistanceExtent(False, distance)
            # ext = comp.features.extrudeFeatures.add(extInput)
               
            progressDialog.hide()
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
        ui  = app.userInterface
        
        dlg = ui.createFileDialog()
        dlg.title = 'Open JSON File'
        dlg.filter = 'JSON File (*.json);;All Files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK :
            return
        global layout
        layout = parseFile(dlg.filename)
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
           
def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById('KeyboardCreatorButtonId')
        if cmdDef:
            cmdDef.deleteMe()            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))