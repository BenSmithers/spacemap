from traveller_utils.factions.faction import Faction 
from traveller_utils.factions.enums import AssetTheme



class FactionGoal:
    def __init__(self, **kwargs):
        self._difficulty = 1
    
    @property
    def difficulty(self)->int:
        return self._difficulty

    def is_complete(self, stats):
        raise NotImplementedError()
    
class Conquest(FactionGoal):
    def __init__(self, faction:'Faction'):
        self._difficulty = int(faction.get_theme_val(self.theme)/2)
    @property 
    def theme(self)->AssetTheme:
        return NotImplementedError()
    def is_complete(self, stats:dict):
        raise NotImplementedError()
    
class MilitaryConquest(Conquest):
    @property
    def theme(self):
        return AssetTheme.force
    def is_complete(self, stats: dict):
        return stats["force_destroyed"]>(2*self._difficulty)
        
class CommercialExpansion(Conquest):
    @property
    def theme(self):
        return AssetTheme.wealth
    def is_complete(self, stats: dict):
        return stats["wealth_destroyed"]>(2*self._difficulty)
     
class PlanetarySeizure(FactionGoal):
    pass

class IntelligenceCoup(Conquest):
    @property
    def theme(self):
        return AssetTheme.cunning
    def is_complete(self, stats: dict):
        return stats["cunning_destroyed"]>(2*self._difficulty)

class ExpandInfluenceGoal(FactionGoal):
    def __init__(self):
        self._difficulty = 1

    def is_complete(self, stats:dict):
        if stats["contested_bases"]>0:
            self._difficulty = 2
        return stats["new_bases"]>0