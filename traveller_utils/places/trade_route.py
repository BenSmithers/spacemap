from traveller_utils.places.world import World 
from traveller_utils.core.coordinates import SubHID, HexID

class TradeRoute:
    def __init__(self, route:'list[SubHID]'):
        self._route = route 
        self._tons_per_month = 100

    @property
    def tons_per_month(self):
        return self._tons_per_month
    
    