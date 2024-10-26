from traveller_utils.places.world import World 
from traveller_utils.places.trade_route import TradeRoute
from traveller_utils.ships.ship import ShipSWN
from traveller_utils.core.coordinates import SubHID, HexID
from traveller_utils.trade_goods import ALL_GOODS, TradeGoods, get_good

from math import exp, log

import numpy as np 

def find_maximum_sale(market_one:'Market', market_two:'Market', good_name):
    """
        Finds the market maximum while still turning a profit
        Goods are bought in market 1 and sold in market 2
    """
    
    # first, get the total supply 
    total_supply = market_one.supply[good_name]
    # check sample 
    checking = np.linspace(total_supply, 0, 1000)
    profit = market_two.get_market_price(good_name, checking) - market_one.get_market_price(good_name, -checking) 

    # find the point where [checking vs profit] crosses the x axis
    # at that point, shipping any more goods will be at a loss 
    return checking[np.argmin(np.abs(profit))-1]

class Market:
    def __init__(self, linked_world:World):
        self._linked_world = linked_world
        self._linked_shid = HexID(0,0)

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
                self._supply[tg.name] = scale_factor*tg.extract_base_tonnage()*(self._linked_world._population/100000)**0.25
                self._supply[tg.name] = max([self._supply[tg.name], 1])

            if demand_factor!=0:
                self._demand[tg.name] = demand_factor*tg.extract_base_tonnage()*(self._linked_world._population/100000)**0.25
                self._demand[tg.name] = max([self._demand[tg.name], 1])        

    @property
    def supply(self):
        return self._supply

    def link_shid(self, subhid:SubHID):
        self._linked_shid = subhid

    def linked_shid(self)->SubHID:
        return self._linked_shid

    def get_market_price(self, good_name, fudge_supply=0):
        """
            We fudge the "supply" by the fudge supply value
        """
        tg = get_good(good_name)
        supply_diff = self._supply[tg.name] - self._demand[tg.name] + fudge_supply
        for route in self.trade_routes[good_name]:                 
            supply_diff += route.tons_per_month[self._linked_shid.downsize()] 

        tonnage = tg.extract_base_tonnage()
        flex = tg.demand_flexibility

        shift = -tonnage*log(0.25)/flex 
        net_cost = 5*tg.base_price/(1+np.exp( -flex*(-supply_diff  -shift)/tonnage) )
        return net_cost
    
    def add_route(self, which:TradeRoute):
        self._trade_routes[which.trade_good].append(which)

    @property
    def trade_routes(self)->'list[TradeRoute]':
        return self._trade_routes

    @property 
    def linked_world(self)->World:
        return self._linked_world
    
    def check_route(self, other_market:'Market', good_name:str):
        examples = [
            "shuttle",
            "hauler",
            "bulk freighter",
            "capital freighter"
        ]
        freighters = {key:ShipSWN.load_from_template(key) for key in examples}

        available = self.supply[good_name]
        # max profit per good shipped - maximum 
        profit = other_market.get_market_price(good_name) - self.get_market_price(good_name)
        if profit<0 or available<1:
            return  
        
        # maximum amount that could feasibly be profitable 
        profitable_amt = 0.98*find_maximum_sale(self, other_market, good_name)
        # recalculate this...
        profit = other_market.get_market_price(good_name, profitable_amt) - self.get_market_price(good_name, -profitable_amt)
        if profit <0:
            return 
        print(profit)
        max_cargo = -1 
        max_margin = -1 
        ship_name = ""
        for entry in freighters:
            this_ship = freighters[entry]
            # profit moving the ship's cargo worth minus the operational costs 
            # so if there isn't a lot of cargo here, it won't be economical to
            margin = profit*min([this_ship.cargo_free(), profitable_amt ]) - this_ship.get_route_cost(other_market._linked_shid - self._linked_shid)
            if margin>max_margin:
                ship_name = entry 
                max_margin = margin 
                max_cargo = min([this_ship.cargo_free(), profitable_amt ])
                if profitable_amt>max_cargo:
                    max_cargo*=int(profitable_amt/max_cargo)
        if ship_name=="":
            return 
        new_route = TradeRoute([self._linked_shid.downsize(), other_market._linked_shid.downsize()], good_name, max_cargo)
        self.add_route(new_route)
        other_market.add_route(new_route)
        print("Generated {} trade route".format(good_name))
        return new_route, freighters[ship_name]