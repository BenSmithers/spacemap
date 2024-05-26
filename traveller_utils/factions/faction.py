from traveller_utils.factions.enums import AssetTheme, FactionTag, asset_appeal_modifier
from traveller_utils.coordinates import HexID
from traveller_utils.world import World

from traveller_utils.factions.base_classes import Base_Of_Influence, Asset
from random import choice
from traveller_utils.utils import all_subclasses

# hit point values of the attributes 
hpv = [0,1,2,4,6,9,12,16,20]

class Faction:
    def __init__(self, name:str, homeworld:World, world_loc:HexID)->None:
        self._name = name

        # attributes 
        self._force_rating = 1
        self._cunning = 1
        self._wealth = 1

        self._hit_points = self.max_hitpoints()

        self._farcreds = 1
        self._experience = 0
        self._tag = choice(list(Faction))

        self._assets = {} # hexid->list[Asset]


        self._aware_of = {} #hexID -> Asset type  

        self._homeworld = homeworld
        self._homeworld_id = world_loc
        self._bases_of_influence = [] # hexIDs 

        self._assets[self._homeworld] = []

    @property 
    def awareness(self):
        return self._aware_of

    @property
    def homeworld(self)->World:
        return self._homeworld
    @property
    def homeworld_id(self)->HexID:
        return self._homeworld_id

    def change_homeworld(self, world):
        if world in self._bases_of_influence:
            self._homeworld = world


    def expand_influence(self, location:World, cost:int):
        new_asset = Base_Of_Influence(self, cost)
        if location not in self._bases_of_influence:
            self._bases_of_influence.append(new_asset)


            # update assest thingy 

    def buy_asset(self, which:'Asset'):
        which.set_location(self._homeworld)
        self._assets[self._homeworld].append(which)

    @property
    def assets(self)->'dict[HexID]':
        return self._assets
    
    @property
    def asset_list(self)->'list[Asset]':
        all_assets = []
        for hid in self._assets.keys():
            all_assets += self._assets[hid]
        return all_assets
        
    def max_hitpoints(self)->int:
        return 4 + hpv[self._force_rating] + hpv[self._cunning] + hpv[self._wealth]

    @property
    def hit_points(self)->int:
        return self._hit_points
    @property
    def force_rating(self)->int:
        return self._force_rating

    def get_theme_val(self, theme:AssetTheme):
        if theme==AssetTheme.cunning:
            return self.cunning
        elif theme==AssetTheme.force:
            return self.force_rating
        elif theme==AssetTheme.wealth:
            return self.wealth
        else:
            raise ValueError(theme) 

    @property
    def cunning(self)->int:
        return self._cunning
    @property
    def wealth(self)->int:
        return self._wealth
    @property
    def farcreds(self)->int:
        return self._farcreds
    @property
    def experience(self)->int:
        return self._experience

    @property
    def tag(self)->FactionTag:
        return self._tag
