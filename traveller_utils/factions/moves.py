from traveller_utils.factions.base_classes import Move, Asset, Roll
from traveller_utils.factions.enums import AssetTheme
from traveller_utils.coordinates import HexID
from traveller_utils.factions.faction import Faction
from traveller_utils.world import World

class ContinueChangeHomeworld(Move):
    def __init__(self, faction:Faction):
        self._faction  = faction

    def __call__(self):
        self._faction.step_move()
        
class DoNothing(Move):
    def __call__(self):
        return 

class ChangeHomeworld(Move):
    def __init__(self, to_loc:HexID,to_world:World, faction:Faction, **kwargs):
        super().__init__(**kwargs)

        self._from = faction.homeworld_id
        self._to = to_loc
        self._faction = faction 
        self._world = to_world

    @property
    def distance(self):
        return self._from - self._to 
    def __call__(self):
        if self.distance>1:
            self._faction.start_move(self.distance - 1)
        self._faction.change_homeworld(self._world, self._to)
        


class PurchaseAsset(Move):
    def __init__(self, location:HexID, asset_type:Asset, faction:Faction):
        super().__init__(self)
        self._asset_type = asset_type
        self._location=location
        self._faction = faction
    @property
    def location(self)->HexID:
        return self._location
    @property
    def asset_type(self):
        return self._asset_type

    def __call__(self):
        self._faction.buy_asset(self.asset_type())
    


class ExpandInfluence(Move):
    def __init__(self, location:HexID, source:Faction, target:'tuple[Faction]'):
        self._location = location
        self._source = source
        self._targets = target
        Move.__init__(self)


    def is_available(self, faction: Faction) -> bool:
        if self._location in faction.assets.keys():
            return True
        else:
            return False
        

class AttackAction(Move):
    """
        An attack using a series of assets against a target faction 
    """
    def __init__(self, source:list[Asset], target:list[Asset], location:HexID):

        self._source = source
        self._target= target

        self._loc = location

    @property
    def attacker_theme(self):
        return self._atk_theme
    @property
    def defender_theme(self):
        return self._def_theme

    @property
    def source(self):
        return self._source
    @property
    def target(self):
        return self._target

    def get_mods(self,target:Asset):
        defense_mod = target.get_defense_mod(self)
        my_mod = self._source.parent.get_theme_val(self._atk_theme)

        return(defense_mod, my_mod)

class FactionAttack(Move):
    def __init__(self, source:Asset, target:Faction, attacker_theme:AssetTheme, defender_theme:AssetTheme):
        self._source = source
        self._target= target

        self._atk_theme = attacker_theme
        self._def_theme = defender_theme

        Move.__init__(self)

    @property
    def attacker_theme(self):
        return self._atk_theme
    @property
    def defender_theme(self):
        return self._def_theme

    @property
    def source(self):
        return self._source
    @property
    def target(self):
        return self._target