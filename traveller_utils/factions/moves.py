from traveller_utils.factions.base_classes import Move, Asset, Roll
from traveller_utils.factions.enums import AssetTheme
from traveller_utils.coordinates import HexID
from traveller_utils.factions.faction import Faction

class PurchaseAsset(Move):
    def __init__(self, location:HexID, asset_type=Asset):
        super().__init__(self)
        self._asset_type = asset_type
        self._location=location
    @property
    def location(self)->HexID:
        return self._location
    @property
    def asset_type(self):
        return self._asset_type

    
"""
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
            return False"""

class AttackAction(Move):
    def __init__(self, source:Asset, target:Asset, attacker_theme:AssetTheme, defender_theme:AssetTheme):
        self._source = source
        self._target= target

        self._atk_theme = attacker_theme
        self._def_theme = defender_theme

        

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