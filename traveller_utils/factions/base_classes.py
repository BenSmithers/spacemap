from random import randint
from traveller_utils.factions.enums import AssetTheme, AssetType
from traveller_utils.core.coordinates import HexID
from traveller_utils.world import World



class Roll:
    def __init__(self, roll_str:str):
        self._roll_str = roll_str.lower()
        self._roll_str = self._roll_str.replace(" ","")

        split_plus = self._roll_str.split("+")
        if len(split_plus)==1:
            split_minus = self._roll_str.split("-")
            if len(split_minus)==1:
                self.modifier = 0
                lhalf = self._roll_str
            elif len(split_minus)==2:
                self.modifier = -int(split_minus[1])
                lhalf = split_minus[0]

        elif len(split_plus)==2:
            lhalf = split_plus[0]
            self.modifier = int(split_plus[1])
        else:
            raise ValueError("Error parsing {}".format(roll_str))

        split_roller = lhalf.split("d")
        if len(split_roller)!=2:
            raise ValueError("Error parsing {}".format(roll_str))
        self.n_dice = int(split_roller[0])
        self.d_type = int(split_roller[1])

    def __call__(self):
        total = 0
        for i in range(self.n_dice):
            total += randint(1, self.d_type)

        return total + self.modifier


class Move:
    _free = False 

    def __init__(self, **kwargs):
        self._success = False
        self._actiontype = None

    def __call__(self):
        raise NotImplementedError()

    @property
    def success(self)->bool:
        return self._success

    @property 
    def free(self)->bool:
        return self._free

class Asset:
    counter = 0
    max_hp = 0
    cost = 1
    tl = 1
    rank = 1
    type = AssetType.Special
    theme = AssetTheme.cunning
    defense_theme = AssetTheme.cunning

    stealth = False


    def __init__(self):
        self._hp = self.max_hp

        self._destroyed = False
        self._hasattack = False

        self._special = False

        self._location = None
        self._damage = Roll("0d4")
        self._counter = Roll("0d4")

        self._id = Asset.counter
        Asset.counter += 1

    @property 
    def hp(self):
        return self._hp
    def set_hp(self, new_hp):
        self._hp = new_hp
    def set_hp_and_max(self, new_hp):
        self._hp = new_hp
        self.max_hp = new_hp

    def take_damage(self, damage:int)->bool:
        """
            reduces the hp of the asset by "damage"
            returns True if asset is destroyed 
        """
        self._hp -= damage
        if self._hp<=0:
            self._destroyed = True

        return self._destroyed

    def roll_damage(self):
        """
            Rolls the damage for when this asset attacks
        """
        return self._damage()
    def roll_counter(self):
        """
            Roll the counter-attack damage  
        """
        return self._counter()

    def set_location(self, where:HexID):
        self._location = where
    
    @property
    def location(self)->HexID:
        return self._location

        
    @property
    def attack_theme(self):
        return self.theme

    def get_odds_on_target(self, target:'Asset'):
        defense_mod = target.get_defense_mod(self)
        my_mod = self.parent.get_theme_val(self.attack_theme)

        return defense_mod, my_mod

    @property
    def parent(self):
        return self._parent

    def get_defense_mod(self, attack:Move):
        return self._parent.get_theme_val(attack.defender_theme)

    @property
    def has_attack(self):
        return self._hasattack


class Base_Of_Influence(Asset):
    def __init__(self, parent, cost):
        super().__init__(parent)
        self._max_hp = cost
        self._hp = cost 
        self._cost = cost
        self._type = AssetType.Special