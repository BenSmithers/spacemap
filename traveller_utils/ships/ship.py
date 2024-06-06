from traveller_utils.core.coordinates import HexID
from traveller_utils.person import Person
from traveller_utils.actions import MapAction, NullAction, EndRecurring
from traveller_utils.name_gen import sample_adjective, sample_noun
from traveller_utils.enums import get_entry_by_name, TradeGood
from traveller_utils.enums import ShipClass, ShipCategory
from traveller_utils.ships import Fitting, ShipDefense, ShipWeapon, hull_data, sample_ships


from PyQt5.QtWidgets import QGraphicsScene
from copy import deepcopy

import random 
import os 
import json 

_sizes = ["small"]*10 + ["medium"]*3 + ["large"]
_kinds = ["freighter"]*10 + ["scout ship"]*3 + ["pleasure yacht"] + ["merchant ship"]*5


class ShipSWN:
    cargo_mult = {
        ShipClass.Fighter:2,
        ShipClass.Frigate:20,
        ShipClass.Cruiser:200,
        ShipClass.Capital:2000
    }
    def __init__(self, shiphull):
        if shiphull not in hull_data:
            raise KeyError("Unknown ship hull {}".format(shiphull))
        data_entry = hull_data[shiphull]
        self._shiphull = shiphull
        self._shipcategory = ShipCategory.Unspecified

        if data_entry["class"]=="fighter":
            self._class = ShipClass.Fighter
        elif data_entry["class"]=="frigate":
            self._class = ShipClass.Frigate
        elif data_entry["class"]=="cruiser":
            self._class = ShipClass.Cruiser
        elif data_entry["class"]=="capital":
            self._class = ShipClass.Capital
        else:
            raise NotImplementedError("Unknown class {}".format(data_entry["class"]))
        
        self._base_speed = data_entry["speed"]
        self._base_cost = data_entry["cost"]
        self._base_armor = data_entry["armor"]
        self._base_hp = data_entry["hp"]
        self._crew_min = data_entry["crew_min"]
        self._crew_max = data_entry["crew_max"]
        self._base_ac = data_entry["ac"]
        self._base_power = data_entry["power"]
        self._base_mass = data_entry["mass"]
        self._max_hardpoints = data_entry["hardpoints"]
        self._template = ""

        self._description = ""
        self._system_drive = False 

        self._fittings = []
        self._defense = []
        self._weapons = []

        self._cargo = {}

    @property
    def template(self):
        return self._template

    def export_template(self):
        items = []
        for fit in self.fittings():
            items.append({
                "type":"shipFitting",
                "name":fit.name
            })
        for weap in self.weapons():
            items.append({
                "type":"shipWeapon",
                "name":weap.name
            })
        for defenses in self.defenses():
            items.append({
                "type":"shipDefense",
                "name":defenses.name
            }) 
        
        return json.dumps({
            "description":self._description,
            "shipHullType":self._shiphull,
            "items":items 
        })

    @property
    def min_crew(self):
        return self._crew_min
    @property
    def max_crew(self):
        double = 1.0 
        for fit in self.fittings():
            if fit.name.lower()=="extended life support":
                double += 1

        return self._crew_max*double 

    def cargo(self):
        return self._cargo
    def add_cargo(self, tg:TradeGood, quantity):
        if tg in self._cargo.keys():
            self._cargo[tg]+=quantity
        else:
            self._cargo[tg] = quantity
    
    def fittings(self)->'list[Fitting]':
        return self._fittings
    
    def weapons(self)->'list[ShipWeapon]':
        return self._weapons
    
    def defenses(self)->'list[ShipDefense]':
        return self._defense

    def add_fitting(self, new_obj:Fitting):
        """
            Checks if the fitting can be added, and then adds it. 
            Works for weapons and defenses as well 

            Raises ValueError if a fitting can not be added.
            Raises TypeError if it's not a fitting, weapon, or defense 
        """

        if self.power_free()>=new_obj.power and self.mass_free()>=new_obj.mass:
            if isinstance(new_obj, ShipWeapon):
                if self.hardpoints_free()>=new_obj.hardpoints:
                    self._weapons.append(new_obj)
                     
                else:
                    raise ValueError("No available hardpoints")
            elif isinstance(new_obj, ShipDefense):
                self._defense.append(new_obj)
            elif isinstance(new_obj, Fitting):
                if new_obj.name.lower() == "system drive":
                    self._system_drive = True
                self._fittings.append(new_obj)
            else:
                raise TypeError("Unknown fitting type: {}".format(type(new_obj)))
        else:
            raise ValueError("Insufficient power or mass")        

    @property
    def shiphull(self)->str:
        """
            Basic Hull Type 
        """
        return self._shiphull

    @property
    def shipclass(self) -> ShipClass:
        """
            Ship Size Class (Fighter / Freighter / Cruiser 
        """
        return self._class
    
    @property
    def shipcategory(self) -> ShipCategory:
        """
            A representation of the ship's purpose 
        """
        return self._shipcategory

    def power_free(self):
        start = self._base_power 
        start -= sum([entry.power for entry in self.fittings()])
        start -= sum([entry.power for entry in self.defenses()])
        start -= sum([entry.power for entry in self.weapons()])
        return start 

    def max_cargo(self):
        mass = self.mass_free()
        return self.cargo_mult[self.shipclass]*mass

    def cargo_free(self):
        max_cargo = self.max_cargo()
        cargo_space =self.cargo()
        for tg in cargo_space:
            max_cargo -= cargo_space[tg] 
        return max_cargo

    def mass_free(self):
        start = self._base_mass 
        start -= sum([entry.mass for entry in self.fittings()])
        start -= sum([entry.mass for entry in self.defenses()])
        start -= sum([entry.mass for entry in self.weapons()])
        return start 
    
    def hardpoints_free(self):
        start = self._max_hardpoints
        for weap in self._weapons:
            start -= weap.hardpoints
        return start 
    
    def cost(self):
        start = self._base_cost 
        if self._system_drive:
            start *= 0.90
        start += sum([entry.cost for entry in self.fittings()])
        start += sum([entry.cost for entry in self.defenses()])
        start += sum([entry.cost for entry in self.weapons()])
        return start 
    
    def annual_maintenance(self):
        return self.cost()/10.0

    @classmethod
    def load_from_template(cls, template_name):
        template_dict=sample_ships[template_name]

        hulltype = template_dict["shipHullType"]
        new_ship = cls(hulltype)
        new_ship._description = template_dict["description"]
        new_ship._template = template_name
        for entry in template_dict["items"]:
            if entry["type"]=="shipFitting":
                item=Fitting(entry["name"], new_ship.shipclass)
            elif entry["type"]=="shipWeapon":
                item=ShipWeapon(entry["name"], new_ship.shipclass)
            elif entry["type"]=="shipDefense":
                item =ShipDefense(entry["name"], new_ship.shipclass)
            new_ship.add_fitting(item)
            
        return new_ship

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
        self._cargo = {}

    def cargo(self):
        return self._cargo
    def add_cargo(self, tg:TradeGood, quantity):
        if tg in self._cargo.keys():
            self._cargo[tg]+=quantity
        else:
            self._cargo[tg] = quantity

    def pack(self):
        packed_cargo = {
            key.name : int(self._cargo[key]) for key in self._cargo 
        }
        return {
            "cargo":packed_cargo,
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
        unpacked = {
            get_entry_by_name(key, TradeGood):pack["cargo"][key] for key in pack["cargo"]
        }
        what._cargo = unpacked
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
        new._description = "A {} {}".format(new._size, random.choice(_kinds))
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
        temp._route = [HexID.unpack(entry) for entry in pack["route"]]
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
        
    @property
    def route(self):
        return self._route


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