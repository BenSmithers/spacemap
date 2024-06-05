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

        self._xp = 0

        self._hit_points = self.max_hitpoints()

        self._farcreds = 1
        self._experience = 0
        self._tag = choice(list(Faction))

        self._assets = {} # hexid->list[Asset]


        self._aware_of = {} #hexID -> Asset type  

        self._homeworld = homeworld
        self._homeworld_id = world_loc
        self._bases_of_influence = {self._homeworld_id:[Base_Of_Influence(self, self._hit_points), self._homeworld]} # hexIDs 

        self._assets[self._homeworld_id] = []

        self._moving = False
        self._move_turns_remain = 0 

        self._stat_keys = ["force_destroyed", "wealth_destroyed", "cunning_destroyed", 
                           "planets_seized","new_bases","contested_bases", 
                           "turns_without_action", "turns_without_attack", 
                           "hp_damage_done", "factions_destroyed","stealthed_on_enemy_worlds", 
                           "strongest_force_destroyed", "spent_on_bribes"]
        self._stats = {}

    def reset_stats(self):
        self._stats={
            key:0 for key in self._stat_keys
        }

    @property 
    def stats(self):
        return self._stats

    def award_xp(self, xp):
        self._xp = self._xp + xp
    def spend_xp(self, xp):
        if xp > self._xp:
            raise ValueError("Cannot spend more xp than is present")
        self._xp -= xp 

    @property
    def move_turns_remaining(self):
        return self._move_turns_remain
    def step_move(self):
        self._move_turns_remain = self._move_turns_remain - 1
    def start_move(self, distance):
        self._moving = True 
        self._move_turns_remain = distance 
    @property
    def moving(self):
        return self._moving    
    

    @property 
    def awareness(self):
        return self._aware_of

    @property
    def homeworld(self)->World:
        return self._homeworld
    @property
    def homeworld_id(self)->HexID:
        return self._homeworld_id

    def change_homeworld(self, world:World, id:HexID):
        if id in self._bases_of_influence:
            
            # swap the hp for the bases of influence 

            # get the homeworld hp 
            holder = self._bases_of_influence[self._homeworld_id][0].hp 
            # set the homeworld to the base 
            self._bases_of_influence[self._homeworld_id][0].set_hp(
                self._bases_of_influence[id][0]
            )
            # and set the base (new homeworld) to the hoeworld hp 
            self._bases_of_influence[id][0].set_hp(
                holder 
            )
            self._homeworld = world
            self._homeworld_id = id

        else:
            raise ValueError("Cannot change homeworld to one where the faction lacks a base of influence")


    def expand_influence(self, location:World,location_id:HexID, cost:int):
        new_asset = Base_Of_Influence(self, cost)
        if location_id not in self._bases_of_influence:
            self._bases_of_influence[location_id] = [new_asset, location]


            # update assest thingy 

    def buy_asset(self, which:'Asset'):
        which.set_location(self._homeworld)
        self._assets[self._homeworld].append(which)
        self._farcreds = self._farcreds - which.cost
        if self._farcreds<0:
            raise ValueError("Bought asset moving into negative farcreds! Shouldn't be allowed")

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
