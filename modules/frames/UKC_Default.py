from .AbstractFrame import AbstractFrame


class UKC_Default(AbstractFrame):

    def generateFrame(self):
        super().generateFrame()
        print("generating a UKC Default frame")
