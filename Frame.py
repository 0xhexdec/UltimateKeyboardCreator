# Author-Julian Pleines
# Creates the Frame Body for the Keyboard

import os


def getFrames() -> dict:
    dirPath = os.path.dirname(__file__) + "/modules/frames"
    frames: dict = {}
    for filename in os.listdir(dirPath):
        if filename.endswith(".py") and filename != "AbstractFrame.py":
            name = filename.rpartition(".")[0].replace("_", " ")
            frames[name] = filename.replace(".py", "")
    return frames
