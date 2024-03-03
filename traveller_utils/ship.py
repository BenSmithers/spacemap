from traveller_utils.coordinates import HexID
from traveller_utils.person import Person
from traveller_utils.actions import MapAction, NullAction, EndRecurring
from traveller_utils.clock import Time

from PyQt5.QtWidgets import QGraphicsScene
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
    def generate(cls, **kwargs):
        new = cls(**kwargs)
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
    def rate(self):
        return self._rate
    @property
    def icon(self):
        return self._icon
    
class AIShip(Ship):
    def __init__(self, route:'list[HexID]', rate=0.183,):
        super().__init__(rate)

        self._route = route[::-1]
        self._captain = Person.generate()
    

    def is_done(self):
        return len(self._route)==0

    def step(self):
        if len(self._route)==0:
            return
        else:
            return self._route.pop()


    @classmethod
    def generate(cls, route):
        new = super().generate(route=route)
        new._route= deepcopy(route)
        return new
    

class MoveShipAction(MapAction):
    def __init__(self, ship_id, from_id, to_id):
        self.shipid = ship_id
        self.fromid = from_id
        self.toid = to_id
    def __call__(self, map: QGraphicsScene):
        map.move_ship(self.shipid, self.toid)
        return MoveShipAction(self.shipid, self.toid, self.fromid)

class AIShipMoveEvent(MapAction):
    def __init__(self, frequency:Time,n_events:int, ship_id):
        self._ship_id = ship_id

        MapAction.__init__(self, frequency, n_events=n_events)

    def __call__(self, map):
        retval = map.step_ai_ship(self._ship_id)

        if retval==0:
            return NullAction()
        else:
            return EndRecurring()
        