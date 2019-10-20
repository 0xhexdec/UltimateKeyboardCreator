# AbstractFrame is the base class for every frame creation module

from abc import ABC, abstractmethod


class AbstractFrame(ABC):

    @abstractmethod
    def generateFrame(self):
        print("ABSTRACT")
    