from traveller_utils.factions.faction import Faction 
from traveller_utils.utils import all_subclasses
from traveller_utils.factions.base_classes import Asset
from traveller_utils.factions.enums import asset_appeal_modifier

from traveller_utils.factions.moves import * 

class FactionManager:
    def __init__(self):
        self._factions = []

    def get_available_moves(self, faction:Faction):
        # list all of the things we can buy 
        all_moves_available = [] 
        all_assets = all_subclasses(Asset)
        for entry in all_assets:
            if entry.cost < faction.farcreds:
                appeal = entry.cost*asset_appeal_modifier(entry.theme, faction.tag)
                all_moves_available.append([
                    appeal,PurchaseAsset(faction.homeworld_id, entry)
                ])
        
        # check which attacks are available 
        

        # refit assets 

        # Use asset abilities 

    def add_faction(self, faction:Faction):
        self._factions.append(faction)

    @property
    def factions(self)->'list[Faction]':
        return self._factions