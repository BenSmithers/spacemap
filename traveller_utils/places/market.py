from traveller_utils.places.world import World 
from traveller_utils.places.trade_route import TradeRoute
from traveller_utils.core.coordinates import SubHID
from traveller_utils.trade_goods import ALL_GOODS, TradeGoods, get_good
from math import exp, log

class Market:
    def __init__(self, linked_world:World):
        self._linked_world = linked_world
        self._linked_shid = SubHID(0,0,0,0)

        self._supply = {}
        self._demand = {}
        self._trade_routes = {}
        for tg in list(ALL_GOODS.values()):
            self._trade_routes[tg.name] = []
            self._supply[tg.name] = 0 
            self._demand[tg.name] = 0

            scale_factor = 0
            demand_factor = 0
            for cat in self._linked_world.category:
                if cat in tg.available:
                    if scale_factor==0:
                        scale_factor = 1
                    
                    if cat in tg.supply_mod.keys():
                        if tg.supply_mod[cat]>scale_factor:
                            scale_factor+=tg.supply_mod[cat]
                    #print(cat.name, tg.supply_mod.keys())
                if cat in tg.demand_mod.keys():
                    demand_factor += tg.demand_mod[cat] 
            if scale_factor!=0:
                self._supply[tg.name] = scale_factor*tg.extract_base_tonnage()*self._linked_world._population/100000
                self._supply[tg.name] = max([self._supply[tg.name], 1])

            if demand_factor!=0:
                self._demand[tg.name] = demand_factor*tg.extract_base_tonnage()*self._linked_world._population/100000
                self._demand[tg.name] = max([self._demand[tg.name], 1])        

    def link_shid(self, subhid:SubHID):
        self._linked_shid = subhid

    def get_market_price(self, good_name, fudge_supply=0):
        tg = get_good(good_name)
        supply_diff = self._supply[tg.name] - self._demand[tg.name] + fudge_supply
        for route in self.trade_routes:
            if self.linked_shid in route:
                pass 
                

        tonnage = tg.extract_base_tonnage()
        flex = tg.demand_flexibility

        shift = -tonnage*log(0.25)/flex 
        net_cost = 5*tg.base_price/(1+exp( -flex*(-supply_diff  -shift)/tonnage) )
        print(supply_diff)
        return net_cost

    @property
    def trade_routes(self)->'list[TradeRoute]':
        return self._trade_routes

    @property 
    def linked_world(self)->World:
        return self._linked_world