
import os 
import json 
from randomFactory import random

import numpy as np 
from traveller_utils.enums import ShipClass, ShipCategory
from enum import Enum

hull_file = os.path.join(os.path.dirname(__file__),"..", "..", "resources","ship", "ship-hulls.json")
_obj = open(hull_file, 'rt')
hull_data = json.load(_obj)
_obj.close()

hull_file = os.path.join(os.path.dirname(__file__),"..", "..", "resources","ship", "ship-fitting.json")
_obj = open(hull_file, 'rt')
fitting_data = json.load(_obj)
_obj.close()


hull_file = os.path.join(os.path.dirname(__file__),"..", "..", "resources","ship", "ship-weapon.json")
_obj = open(hull_file, 'rt')
weapon_data = json.load(_obj)
_obj.close()

hull_file = os.path.join(os.path.dirname(__file__),"..", "..", "resources","ship", "ship-defense.json")
_obj = open(hull_file, 'rt')
defense_data = json.load(_obj)
_obj.close()

hull_file = os.path.join(os.path.dirname(__file__),"..", "..", "resources","ship", "ships.json")
_obj = open(hull_file, 'rt')
sample_ships = json.load(_obj)
_obj.close()
 

class Contains:
    """
        A struct-like object to easily track if a ship has certain fittings
    """
    extended_stores = False
    hydroponic_production = False 
    mobile_extractor = False
    extended_medbay = False 
    teleportation_pads = False 
    cold_sleep_pods = False 
    automation_support = False  

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
        #self._qualities = self._data_entry["qualities"]
        self._damage = self._data_entry["damage"]

                        
        self._ap = 0
        self._clumsy = False 
        self._flak = False 
        self._consume_ammo = False 
        self._ammo = 0 
        self._cloud = False 
        quals = self._data_entry["qualities"].split(",")
        for qual in quals:
            if "AP" in qual:
                self._ap  = int(qual.split("AP")[1])  
            if "Clumsy" in qual:
                self._clumsy = True 
            if "Flak" in qual:
                self._flak = True 
            if "Cloud" in qual:
                self._cloud = True 
            if "Ammo" in qual:
                self._consume_ammo = True 
                self._ammo = int(qual.split("Ammo")[1])  


        split = self._damage.split("d")

        self._ndice = int(split[0])
        self._dtype = int(split[1])

    @property
    def ap(self):
        """
            Ignores this many points of armor 
        """
        return self._ap

    @property 
    def clumsy(self):
        """
            -4 to hit fighter-class hulls 
        """
        return self._clumsy
    @property
    def flak(self):
        """
            Rolls twice against fighters 
        """
        return self._flak
    @property
    def cloud(self):
        """
            Targets all fighter-class ships that have attacked in the last round 
        """
        return self._cloud
    @property
    def consumes_ammo(self):
        return self._consume_ammo
    

    def roll_damage(self, roll_twice=False):
        """
            Consumes an ammo and returns damage it would deal 
        """
        if self._ammo>0:
            self._ammo-=1 
            
            r1 = np.sum( random.randint(1, self._dtype+1, self._ndice) )
            if roll_twice:
                r2 = np.sum( random.randint(1, self._dtype+1, self._ndice) )
                return max([r1, r2])
            else:
                return r1 

        else:
            return 0

    @property
    def damage_str(self):
        return self._damage



    @property
    def hardpoints(self):
        return self._hardpoints     

    def get_data(self, kind):
        return weapon_data[kind]
        

class ShipDefense(Fitting):
    def __init__(self, kind: str, hull_class: ShipClass):
        super().__init__(kind, hull_class)

        self._effect = self._data_entry["effect"]
        self._uses = 0
        self._maxuses = 0
        self._limited = False  
    
        if "burst" in kind.lower():
            self._maxuses = 1 
            self._limited = True 
        elif "foxer" in kind.lower():
            self._maxuses = 5 
            self._limited = True 
            

    @property
    def uses(self):
        return self._uses
    def reset(self):
        self._uses = self._maxuses 
    def use(self):
        if self._limited and self._uses>0:
            self._uses -= 1

        
        

    @property
    def effect(self):
        return self._effect

    def get_data(self, kind):
        return defense_data[kind]
        
