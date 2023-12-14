from traveller_utils.coordinates import HexID
from traveller_utils.person import Person
from copy import deepcopy

class Ship:
    def __init__(self, rate=0.183):
        """
            rate - number of hexes / day (should be like 1/6)
        """
        self._rate = rate
        self._icon = ""
        self._description = ""
        self._destination = None
        self._location = None

    @classmethod
    def generate(cls):
        new = Ship()
        size = [
            "small",
            "large",
            "medium",
            "medium"
            "medium"
            "medium"
        ]
        return new

    @property 
    def description(self):
        return self._description

    @property
    def location(self)->HexID:
        return self._location
    def set_location(self, hid:HexID):
        self._location = hid
    
    @property
    def destination(self)->HexID:
        return self._destination
    def clear_destination(self):
        self._destination = None
    def set_destination(self, hid:HexID):
        self._destination = hid

    @property
    def icon(self):
        return self._icon
    
class AIShip(Ship):
    def __init__(self, route:'list[HexID]', rate=0.183,):
        super().__init__(rate)

        self._route = route[::-1]
        self._captain = Person.generate()

    def step(self):
        if len(self._route)==0:
            return
        else:
            return self._route.pop()


    @classmethod
    def generate(cls, route):
        new = super().generate()
        new._route= deepcopy(route)
        return new