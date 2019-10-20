# Author-Julian Pleines
# Parses the LayoutFile (json) for any keyboard Layout

import io
import json
import os
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

from .KeyboardData import KeyboardData


# gets all files from the defaultLayouts folder to populate the Dropdown
def getDefaultLayouts():
    return getLayouts(os.path.dirname(__file__) + "/resources/defaultLayouts/")


# gets all files from the customLayouts folder to populate the Dropdown
def getCustomLayouts():
    return getLayouts(os.path.dirname(__file__) + "/resources/customLayouts/")


def getLayouts(dirPath: str) -> dict:
    layouts: dict = {}
    for filename in os.listdir(dirPath):
        if filename.endswith(".json") or filename.endswith(".JSON"):
            with io.open(dirPath + filename, "r", encoding="utf-8-sig") as file:
                data = file.read()
                layoutData = json.loads(data)
                if isinstance(layoutData, list):
                    if isinstance(layoutData[0], dict):
                        for key in layoutData[0]:
                            if key == "name":
                                layouts[layoutData[0][key]] = dirPath + filename

    return layouts


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
            keyboardData.layoutName = filename.rpartition("/")[2].rpartition(".")[0]
            if isinstance(layoutData, list):
                for row in layoutData:
                    if isinstance(row, dict):
                        # meta object available
                        for key in row:
                            if key == "name":
                                keyboardData.layoutName = row[key]
                            if key == "author":
                                keyboardData.author = row[key]
                    elif isinstance(row, list):
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
                                        size = entry[key]
                                    if key == "w2":
                                        # rowPosition += entry["y"]
                                        print("Do nothing")
                                    if key == "x":
                                        columnPosition += entry[key]
                                    if key == "x2":
                                        # columnPosition += entry["x"]
                                        print("Do nothing")
                                    if key == "y":
                                        rowPosition += entry[key]
                                    if key == "y2":
                                        # rowPosition += entry["y"]
                                        print("Do nothing")
                                    if key == "h":
                                        heightOffset = (entry[key] - 1.0) / 2.0
                                    if key == "h2":
                                        # rowPosition += entry["y"]
                                        print("Do nothing")
                            else:
                                print("something unknown")
                        rowPosition += 1
                        layout.append(layoutRow)
                    keyboardData.keys = keys
                    keyboardData.keyboardLayout = layout
            else:
                if ui:
                    ui.messageBox("Layout JSON not parsable!")
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
