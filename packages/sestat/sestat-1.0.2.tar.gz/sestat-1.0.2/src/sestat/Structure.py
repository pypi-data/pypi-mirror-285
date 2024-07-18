from itertools import zip_longest
from enum import Enum


class Structure:
    def __init__(self):
        self.parent: Structure | None = None
        self.elements: list[Structure | str] = []

    def __eq__(self, other):
        if type(other) is type(self) and type(other.parent) is type(self.parent):
            return all(
                [i == j for i, j in zip_longest(self.elements, other.elements, fillvalue=None)])
        return False


class Circle(Structure):
    def __init__(self):
        Structure.__init__(self)
        self.parent: Rail | None = None
        self.elements: list[Rail | str] = []


class RailState(Enum):
    ADDING = 1
    FINISHING = 2


class Rail(Structure):
    def __init__(self, state: RailState = RailState.ADDING):
        Structure.__init__(self)
        self.parent: Circle | None = None
        self.elements: list[Circle | str] = []

        self.state: RailState = state
        self.can_contain = 0
