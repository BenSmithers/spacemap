from traveller_utils.places.world import World 
from traveller_utils.core.coordinates import SubHID, HexID
from traveller_utils.trade_goods import TradeGoods

class TradeRoute:
    """
        Class used to contain information about existing trade routes. 
        These don't actually contain full path information, just the SubHID stops
        and the differences
        
    """
    def __init__(self, route:'list[SubHID]'):
        self._route = route 
        self._tons_per_month = 100

        self._cargo_data = {}

    def __contains__(self, hid):
        return hid in self._cargo_data

    @property
    def cargo_data(self)->'dict[SubHID, list[TradeGoods]]':
        return self._cargo_data
    @property
    def tons_per_month(self):
        return self._tons_per_month
    
    