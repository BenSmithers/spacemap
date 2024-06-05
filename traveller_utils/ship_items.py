
import os 
import json 
import random 

from traveller_utils.enums import ShipClass, ShipCategory


hull_file = os.path.join(os.path.dirname(__file__), "..", "resources","ship", "ship-hulls.json")
_obj = open(hull_file, 'rt')
hull_data = json.load(_obj)
_obj.close()

hull_file = os.path.join(os.path.dirname(__file__), "..", "resources","ship", "ship-fitting.json")
_obj = open(hull_file, 'rt')
fitting_data = json.load(_obj)
_obj.close()


hull_file = os.path.join(os.path.dirname(__file__), "..", "resources","ship", "ship-weapon.json")
_obj = open(hull_file, 'rt')
weapon_data = json.load(_obj)
_obj.close()

hull_file = os.path.join(os.path.dirname(__file__), "..", "resources","ship", "ship-defense.json")
_obj = open(hull_file, 'rt')
defense_data = json.load(_obj)
_obj.close()

hull_file = os.path.join(os.path.dirname(__file__), "..", "resources","ship", "ships.json")
_obj = open(hull_file, 'rt')
sample_ships = json.load(_obj)
_obj.close()

def sample_ship(ship_class, ship_category):
    """
        returns a template name sampled from the given combination of ship size and purpose 
    """
    if ship_class == ShipClass.Fighter:
        if ship_category==ShipCategory.Warship:
            return random.choice(["Strike Fighter",
                                  "Torpedo Fighter",
                                  "Dog Fighter"])
        else:
            return "Shuttle"


class Fitting:
    cost_mult = {
        ShipClass.Fighter:1,
        ShipClass.Frigate:10,
        ShipClass.Cruiser:25,
        ShipClass.Capital:100
    }
    mass_mult = {
        ShipClass.Fighter:1,
        ShipClass.Frigate:2,
        ShipClass.Cruiser:3,
        ShipClass.Capital:4
    }
    def __init__(self, kind:str, shipclass:ShipClass):
        if not isinstance(shipclass, ShipClass):
            raise TypeError("wrong ship class type")
        self._data_entry = self.get_data(kind)

        self._cost = self._data_entry["cost"]
        if self._data_entry["costMultiplier"] and shipclass in Fitting.cost_mult:
            self._cost *= Fitting.cost_mult[shipclass]
        
        self._mass = self._data_entry["mass"]
        if self._data_entry["massMultiplier"] and shipclass in Fitting.mass_mult:
            self._mass *= Fitting.mass_mult[shipclass]

        self._power = self._data_entry["power"]
        if self._data_entry["powerMultiplier"] and shipclass in Fitting.mass_mult:
            self._power *= Fitting.mass_mult[shipclass]

        self._description = self._data_entry["description"]
        
        self._broken = False 

        self._name = kind
    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._name

    def get_data(self, kind):
        return fitting_data[kind.lower()]

    @property
    def power(self):
        if self._broken:
            return False
        else:
            return self._power
    @property
    def mass(self):
        return self._mass 
    @property 
    def cost(self):
        return self._cost 
    
class ShipWeapon(Fitting):
    def __init__(self, kind: str, hull_class: ShipClass):
        super().__init__(kind, hull_class)

        self._hardpoints = self._data_entry["hardpoint"]
        self._qualities = self._data_entry["hardpoint"]
        self._damage = self._data_entry["damage"]
    @property
    def damage(self):
        return self._damage
    @property 
    def qualities(self):
        return self._qualities
    @property
    def hardpoints(self):
        return self._hardpoints     

    def get_data(self, kind):
        return weapon_data[kind]
        

class ShipDefense(Fitting):
    def __init__(self, kind: str, hull_class: ShipClass):
        super().__init__(kind, hull_class)

        self._effect = self._data_entry["effect"]

    @property
    def effect(self):
        return self._effect

    def get_data(self, kind):
        return defense_data[kind]
        
