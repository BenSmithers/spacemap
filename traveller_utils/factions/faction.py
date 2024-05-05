from traveller_utils.factions.enums import AssetTheme, FactionTag, asset_appeal_modifier
from traveller_utils.coordinates import HexID
from traveller_utils.world import World

from traveller_utils.factions.base_classes import Base_Of_Influence, Asset
from traveller_utils.factions.moves import *
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

        self._aware_of = {} #Faction -> list of assets 

        self._homeworld = homeworld
        self._homeworld_id = world_loc
        self._bases_of_influence = [] # hexIDs 

        self._assets[self._homeworld] = []


    def get_available_moves(self):
        # list all of the things we can buy 
        all_moves_available = [] 
        all_assets = all_subclasses(Asset)
        for entry in all_assets:
            if entry.cost < self._farcreds:
                appeal = entry.cost*asset_appeal_modifier(entry.theme, self._tag)
                all_moves_available.append([
                    appeal,PurchaseAsset(self._homeworld_id, entry)
                ])
        

        # check which attacks are available 

        # refit assets 

        # Use asset abilities 

    @property
    def homeworld(self)->World:
        return self._homeworld

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

    def assets(self)->'dict[HexID]':
        return self._assets
        
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

