# Author-Julian Pleines
# Parses the LayoutFile (json) for any keyboard Layout

import io
import json
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

from .KeyboardData import KeyboardData


# gets all files from the defaultLayouts folder to populate the Dropdown
def getDefaultLayouts():
    return None


# gets all files from the customLayouts folder to populate the Dropdown
def getCustomLayouts():
    return None


def parseFile(filename: str, keyboardData: KeyboardData):
    # Code to react to the event.
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        with io.open(filename, 'r', encoding='utf-8-sig') as file:
            data = file.read()
            layout = []
            layoutData = json.loads(data)
            rowPosition = 0.0
            columnPosition = 0.0
            size = 1.0
            heightOffset = 0.0
            keys = 0
            for row in layoutData:
                layoutRow = []
                columnPosition = 0.0
                for entry in row:
                    if isinstance(entry, str):
                        layoutRow.append([columnPosition + (size / 2), rowPosition + heightOffset, size])
                        keys += 1
                        columnPosition += size
                        size = 1.0
                        heightOffset = 0.0
                    elif isinstance(entry, dict):
                        for key in entry:
                            if key == "w":
                                size = entry["w"]
                            if key == "w2":
                                # rowPosition += entry["y"]
                                print("Do nothing")
                            if key == "x":
                                columnPosition += entry["x"]
                            if key == "x2":
                                # columnPosition += entry["x"]
                                print("Do nothing")
                            if key == "y":
                                rowPosition += entry["y"]
                            if key == "y2":
                                # rowPosition += entry["y"]
                                print("Do nothing")
                            if key == "h":
                                heightOffset = (entry["h"] - 1.0) / 2.0
                            if key == "h2":
                                # rowPosition += entry["y"]
                                print("Do nothing")
                    else:
                        print("something unknown")
                rowPosition += 1
                layout.append(layoutRow)
            keyboardData.keys = keys
            keyboardData.keyboardLayout = layout
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
