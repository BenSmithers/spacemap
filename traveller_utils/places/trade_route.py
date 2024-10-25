from traveller_utils.core.coordinates import SubHID, HexID
from traveller_utils.trade_goods import TradeGoods

class TradeRoute:
    """
        Class used to contain information about existing trade routes. 
        These don't actually contain full path information, just the SubHID stops
        and the differences
        
    """
    def __init__(self, route:'list[HexID]', good_name:str, tonnage:int):
        self._route = route 
        self._tonnages = {
            route[0]: -tonnage,
            route[1]: tonnage
        }
        self._full_route = []

        self._trade_good_name = good_name

    def set_full_route(self, full_route):
        self._full_route = full_route
    @property
    def full_route(self)->'SubHID':
        return self._full_route

    @property
    def trade_good(self):
        return self._trade_good_name

    @property
    def tons_per_month(self)->'dict[HexID, int]':
        return self._tonnages
    
    