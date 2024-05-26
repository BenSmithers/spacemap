from traveller_utils.factions.faction import Faction 
from traveller_utils.utils import all_subclasses
from traveller_utils.factions.base_classes import Asset
from traveller_utils.factions.enums import asset_appeal_modifier, attack_mod

from traveller_utils.factions.moves import * 

class FactionManager:
    def __init__(self):
        # int -> faction
        self._factions = {}


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
        for hid in faction.assets:
            # assets that have an attack 
            attackables = list(filter(lambda x:x.has_attack, faction.assets[hid]))
            for fact_id in self._factions.keys():
                this_fact = self.get_faction(fact_id)
                if hid in this_fact.assets:
                    # okay there are targetable assets here! 

                    def is_targetable(which_asset:Asset):
                        """ 
                            A target is targetable by default. 
                            It is not targetable if the target is stealthed 
                            But then it *is* if this faction is aware of such an asset here. 
                        """
                        target = True 
                        if which_asset.stealth:
                            if type(which_asset) in faction.awareness[hid]:
                                pass
                            else:
                                target=False 
                        return target

                    # filter out the stealth ones 
                    targets_here = list(filter(is_targetable, this_fact.assets[hid]))

                    atk = AttackAction(attackables,targets_here , hid)
                    appeal = 0
                    for attacker in attackables:
                        atk_theme = faction.get_theme_val(attacker.type)
                        def_theme = this_fact.get_theme_val(attacker.defense_theme)
                        appeal += atk_theme/def_theme
                    appeal *= attack_mod(faction.tag)
                    all_moves_available.append([
                        appeal, atk 
                    ])

        # refit assets 

        # Use asset abilities 

    def add_faction(self, faction:Faction):
        fid = 0
        while fid in self._factions:
            fid+=1 
        self._factions[fid] = faction
    
    def get_faction(self, fid)->Faction:
        if fid in self._factions:
            return self._factions[fid]

    @property
    def factions(self)->'list[Faction]':
        return list(self._factions.values())