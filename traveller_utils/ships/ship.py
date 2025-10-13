from traveller_utils.person import Person
from traveller_utils.actions import MapAction, NullAction, EndRecurring
from traveller_utils.name_gen import sample_adjective, sample_noun
from traveller_utils.enums import get_entry_by_name, TradeGood
from traveller_utils.enums import ShipClass, ShipCategory
from traveller_utils.ships import Fitting, ShipDefense, ShipWeapon, hull_data, sample_ships
from traveller_utils.core.coordinates import SubHID

from PyQt5.QtWidgets import QGraphicsScene
from copy import deepcopy

from enum import Enum

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
        self._name = ""

        self._description = ""
        self._system_drive = False 
        self._funds = 0

        self._fittings = []
        self._defense = []
        self._weapons = []

        self._fuel_scoop = False 
        self._drive_rating = 1 
        self._fuel = 1
        self._fuel_max = 1

        self._cargo = {}

    def change_funds(self, delta):
        self._funds = self._funds + float(delta)
        if self._funds<0:
            self._funds = 0

    def empty_cargo(self):
        self._cargo = {}

    @property
    def funds(self):
        return self._funds

    @property
    def name(self):
        if self._name == "":
            return "The Nameless"
        else:
            return self._name 

    @property 
    def has_fuel_scoop(self):
        return self._fuel_scoop
    @property
    def fuel_max(self):
        return self._fuel_max
    @property
    def fuel(self):
        return self._fuel

    def add_fuel(self):
        if self._fuel_max>self._fuel:
            self._fuel += 1

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
    def refuel(self):
        self._fuel = self._fuel_max
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

                self._fuel_scoop = self._fuel_scoop or new_obj.name.lower()=="fuel scoop"
                if new_obj.name.lower()=="fuel bunkers":
                    self._fuel_max+=1 

                if "drive-" in new_obj.name.lower():
                    value = int(new_obj.name.lower().split("-")[1][0])
                    self._drive_rating = value
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
    
    def get_route_expenses(self, n_hexes):
        n_jumps = int(n_hexes/self.drive_rating) # round down
        # if it's not perfect, add one extra jump
        if n_hexes%self.drive_rating != 0:
            n_jumps+=1
        
        travel_time = n_hexes*6/self.drive_rating  # spike drill time
        travel_time += n_jumps*2/self.drive_rating # refuel 
        travel_time*=2  # return 

        return travel_time*self.daily_operational
    
    @property
    def daily_operational(self):
        return (1./365)*(self.annual_maintenance() + 0.5*(self.min_crew + self.max_crew)*5.5e4)

    @property
    def drive_rating(self):
        return self._drive_rating

    @classmethod
    def load_from_template(cls, template_name):
        template_dict=sample_ships[template_name]

        hulltype = template_dict["shipHullType"]
        new_ship = cls(hulltype)
        new_ship._load_template(template_dict)
        new_ship._template = template_name
            
        return new_ship
    
    @property
    def description(self):
        return self._description
    
    def _load_template(self, template_dict):
        self._description = template_dict["description"]
        for entry in template_dict["items"]:
            if entry["type"]=="shipFitting":
                item=Fitting(entry["name"], self.shipclass)
            elif entry["type"]=="shipWeapon":
                item=ShipWeapon(entry["name"], self.shipclass)
            elif entry["type"]=="shipDefense":
                item =ShipDefense(entry["name"], self.shipclass)
            self.add_fitting(item)



def sample_ship(ship_class, ship_category):
    """
        returns a template name sampled from the given combination of ship size and purpose 
    """
    if ship_class == ShipClass.Fighter:
        if ship_category==ShipCategory.Warship:
            return random.choice(["Strike Fighter",
                                  "Torpedo Fighter",
                                  "Dog Fighter"])
        elif ship_category==ShipCategory.Freight or  ship_category==ShipCategory.Ferry:
            return "shuttle"
        elif ship_category==ShipCategory.ResourceExtraction:
            return ""
        elif ship_category==ShipCategory.Research: 
            pass
        elif ship_category==ShipCategory.Yacht:
            return "luxury shuttle" 
        else:
            raise ValueError("Unkown cat {}".format(ship_category))

    elif ship_class==ShipClass.Frigate:
        if ship_category==ShipCategory.Freight:
            return "hauler"
        elif ship_category==ShipCategory.ResourceExtraction:
            return "poor miner"
        elif ship_category==ShipCategory.Ferry:
            return "free merchant"
        elif ship_category==ShipCategory.Research: 
            pass
        elif ship_category==ShipCategory.Colony:
            return "colony frigate"
        elif ship_category==ShipCategory.Yacht:
            pass 
        elif ship_category==ShipCategory.Warship:
            return random.choice(["corvette","patrol boat","heavy frigate"])
        else:
            raise ValueError("Unkown cat {}".format(ship_category))

    elif ship_class==ShipClass.Cruiser:
        if ship_category==ShipCategory.Freight:
            return "bulk freighter"
        elif ship_category==ShipCategory.ResourceExtraction:
            return "freighter miner"
        elif ship_category==ShipCategory.Ferry:
            pass
        elif ship_category==ShipCategory.Research: 
            pass
        elif ship_category==ShipCategory.Warship:
            pass
        elif ship_category==ShipCategory.Yacht:
            pass 
        elif ship_category==ShipCategory.Warship:
            return "fleetCruiser"
        elif ship_category==ShipCategory.Colony:
            return "colonyCruiser"
        else:
            raise ValueError("Unkown cat {}".format(ship_category))
    elif ship_class==ShipClass.Capital:
        if ship_category==ShipCategory.Warship:
            return random.choice(["carrier","battleship"])



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
    def add_cargo(self, tg:str, quantity):
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
    def rate(self):
        return self._rate
    @property
    def icon(self):
        return self._icon
    
class AIShip(ShipSWN):
    def __init__(self,shiphull, route=[],**kwargs):
        super().__init__(shiphull)
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
        temp._captain = Person.unpack(pack["cpt"])
        return temp
    
    def set_captain(self, who:Person):
        self._captain = who
    @property
    def captain(self)->Person:
        return self._captain

    def is_done(self):
        return len(self._route)==0

    def step(self)->SubHID:
        if len(self._route)==0:
            return
        else:
            return self._route.pop()

    @property
    def route(self):
        return self._route
    
    def set_route(self, route):
        self._route = route[::-1]


    @classmethod
    def generate(cls, route, shipclass, shipcat):
        new = cls.load_from_template(sample_ship(shipclass, shipcat))
        new._route= deepcopy(route)[::-1]
        new.set_captain(Person.generate())
        new._name = "The {} {}".format(sample_adjective(), sample_noun())
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