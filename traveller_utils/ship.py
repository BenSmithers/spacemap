from traveller_utils.coordinates import HexID
from traveller_utils.person import Person
from traveller_utils.actions import MapAction, NullAction, EndRecurring
from traveller_utils.clock import Time
from traveller_utils.name_gen import sample_adjective, sample_noun

from PyQt5.QtWidgets import QGraphicsScene
from copy import deepcopy

import random 

_sizes = ["small"]*3 + ["medium"]*5 + ["large"]
_kinds = ["freighter"]*10 + ["scout ship"]*3 + ["pleasure yacht"] + ["merchant ship"]*5

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
        self._name = ""
        self._size = ""

    def pack(self):
        return {
            "rate":self._rate,
            "icon":self._icon,
            "desc":self._description,
            "dest":"" if self._destination is None else self._destination.pack(),
            "loc":self._location.pack(),
            "name":self._name,
            "size":self._size
        }
    @classmethod
    def unpack(cls, pack):
        what = cls(rate = pack["rate"])
        what._icon = pack["icon"]
        what._description = pack["desc"]
        what._destination = None if pack["dest"]=="" else HexID.unpack(pack["dest"])
        what._location = HexID.unpack(pack["loc"])
        what._name=pack["name"]
        what._size=pack["size"]
        return what 

    @classmethod
    def generate(cls, **kwargs):
        new = cls(**kwargs)
        if "name" not in kwargs:
            noun = sample_noun()
            adj = sample_adjective()
            new._name = "The SS "
            new._name+= adj[0].upper() + adj[1:] +" "
            new._name+= noun[0].upper()+noun[1:]

        
        new._size = random.choice(_sizes)
        new._description = "A {} {} ship".format(new._size, random.choice(_kinds))
        return new

    @property
    def name(self):
        return self._name
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
    def __init__(self, route:'list[HexID]'=[], rate=0.183,**kwargs):
        super().__init__(rate)

        self._route = route[::-1]
        self._captain = Person.generate()
    
    def pack(self):
        inter = Ship.pack(self)
        inter["route"] = [entry.pack() for entry in self._route]
        inter["cpt"] = self._captain.pack()
        return inter
    @classmethod
    def unpack(cls, pack):
        temp = super().unpack(pack)
        temp._route = [HexID.unpack(entry) for entry in temp["route"]]
        temp._captain = Person.unpack(pack["cpt"])
        return temp

    def set_captain(self, who:Person):
        self._captain = who
    @property
    def captain(self)->Person:
        return self._captain

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
        new._route= deepcopy(route)[::-1]
        new.set_captain(Person.generate())
        return new
    

class MoveShipAction(MapAction):
    def __init__(self, ship_id, from_id, to_id, **kwargs):
        self.shipid = ship_id
        self.fromid = from_id
        self.toid = to_id
        MapAction.__init__(**kwargs)
    def __call__(self, map: QGraphicsScene):
        map.move_ship(self.shipid, self.toid)
        return MoveShipAction(self.shipid, self.toid, self.fromid)
    def pack(self):
        inter = MapAction.pack(self)
        inter["ship_id"]=self.shipid
        inter["from_id"]=self.fromid
        inter["to_id"]=self.toid
        return inter

class AIShipMoveEvent(MapAction):
    def __init__(self, ship_id, **kwargs):
        self._ship_id = ship_id

        MapAction.__init__(self, **kwargs)

    def __call__(self, map):
        retval = map.step_ai_ship(self._ship_id)

        if retval==0:
            return NullAction()
        else:
            return EndRecurring()
        
    def pack(self):
        inter = MapAction.pack(self)
        inter["ship_id"]=self._ship_id
        return inter