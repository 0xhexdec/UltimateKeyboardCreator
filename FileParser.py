# Author-Julian Pleines
# Parses LayoutFiles (json) for any keyboard Layout and config files for frames

import io
import json
import os
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

from typing import List

from .KeyboardData import KeyboardObject, KeyboardKey


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
                rawLayoutData = json.loads(data)
                if isinstance(rawLayoutData, list):
                    if isinstance(rawLayoutData[0], dict):
                        for key in rawLayoutData[0]:
                            if key == "name":
                                layouts[rawLayoutData[0][key]] = dirPath + filename

    return layouts


def parseLayoutFile(filename: str, keyboardObject: KeyboardObject):
    # Code to react to the event.
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        with io.open(filename, 'r', encoding='utf-8-sig') as file:
            data = file.read()
            layout: List[List[KeyboardKey]] = []
            rawLayoutData = json.loads(data)
            rowPosition = 0.0
            columnPosition = 0.0
            size = 1.0
            heightOffset = 0.0
            keys = 0
            keyboardObject.layoutName = filename.rpartition("/")[2].rpartition(".")[0]
            if isinstance(rawLayoutData, list):
                for row in rawLayoutData:
                    if isinstance(row, dict):
                        # meta keyboardObject available
                        for key in row:
                            if key == "name":
                                keyboardObject.layoutName = row[key]
                            if key == "author":
                                keyboardObject.author = row[key]
                    elif isinstance(row, list):
                        layoutRow: List[KeyboardKey] = []
                        columnPosition = 0.0
                        for entry in row:
                            if isinstance(entry, str):
                                layoutRow.append(KeyboardKey.create(columnPosition + (size / 2), rowPosition + heightOffset, size))
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
                                        print("w2 argument not handled")
                                    if key == "x":
                                        columnPosition += entry[key]
                                    if key == "x2":
                                        # columnPosition += entry["x"]
                                        print("x2 argument not handled")
                                    if key == "y":
                                        rowPosition += entry[key]
                                    if key == "y2":
                                        # rowPosition += entry["y"]
                                        print("y2 argument not handled")
                                    if key == "h":
                                        heightOffset = (entry[key] - 1.0) / 2.0
                                    if key == "h2":
                                        # rowPosition += entry["y"]
                                        print("h2 argument not handled")
                            else:
                                print("something unknown")
                        rowPosition += 1
                        layout.append(layoutRow)
                    keyboardObject.keys = keys
                    keyboardObject.layoutData = layout
                    keyboardObject.keyboardHeightInUnits = rowPosition
            else:
                if ui:
                    ui.messageBox("Layout JSON not parsable!")
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def parseConfigFile():
    # TODO add the config file system
    return None
