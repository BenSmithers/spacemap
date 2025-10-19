from traveller_utils.places.world import World 
from traveller_utils.places.trade_route import TradeRoute
from traveller_utils.ships.ship import ShipSWN
from traveller_utils.core.coordinates import SubHID, HexID
from traveller_utils.trade_goods import ALL_GOODS, TradeGoods, get_good

from math import exp, log
from random import choice 
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
        self._stock = {}
        self._price = {}
        self._normalization = {}
        self._population_scale_factor = (self._linked_world._population/100000)**0.5
        self._population_scale_factor = max([1, self._population_scale_factor])
        self._shortfall_tracker = {}

        for tg in list(ALL_GOODS.values()):
            self._trade_routes[tg.name] = []
            self._supply[tg.name] = 0 
            self._demand[tg.name] = 0
            self._stock[tg.name] = 0
            self._price[tg.name] = tg._price
            self._normalization[tg.name] = tg.extract_base_tonnage()

            scale_factor = 0
            demand_factor = 0
            self._shortfall_tracker[tg.name] = 0.0
            
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
                self._supply[tg.name] = scale_factor*tg.extract_base_tonnage()*self._population_scale_factor
                self._supply[tg.name] = max([self._supply[tg.name], 1])
                self._stock[tg.name] = 1*self._supply[tg.name]
                self._shortfall_tracker[tg.name] = -2

            if demand_factor!=0:
                self._demand[tg.name] = demand_factor*tg.extract_base_tonnage()*self._population_scale_factor
                self._demand[tg.name] = max([self._demand[tg.name], 1])  
                self._shortfall_tracker[tg.name] = 2
            
    def vend(self, this_ship:ShipSWN, tg_name:str, qty:int):
        """
            sells the given ship the `qty` of the trade good 

            The market vends to the ship
                - ship lose money
                - ship get cargo
                - stock go down
        """
        cost = qty*self.get_market_price(tg_name)
        if this_ship.funds < cost:
            return 
        if tg_name not in self._stock:
            return 
        if self._stock[tg_name] < qty: # set qty to the stock if it's more than what's available
            qty =  self._stock[tg_name]
        self._stock[tg_name] -= qty 

        this_ship.add_cargo(tg_name, qty)
        this_ship.change_funds(-cost)
        

    def purchase(self, this_ship:ShipSWN, tg_name, qty=-1):
        """
            The market buys some of the ship's cargo.
                - ship gets money
                - ship cargo go down
                - market get cargo 
        """
        if tg_name not in this_ship.cargo():
            return 
        count = this_ship.cargo()[tg_name]
        if qty==-1:
            qty = count # default to max
        if qty > count:
            qty = count # set to max if more than available were requested 
        
        cost = qty*self.get_market_price(tg_name)
        this_ship.add_cargo(tg_name, -qty)
        this_ship.change_funds(cost)
        if tg_name not in self._stock:
            self._stock[tg_name] = qty
        else:
            self._stock[tg_name] += qty 


    def update_stock(self):
        """
            If there consistently is an overabundance of supply, then the price will drop
            If there consistently is a shortfall, then the price will climb 
        """
        #print(self.linked_world.name)
        for tg in self._stock:
            self._stock[tg] += self._supply[tg] - self._demand[tg]
            #print("    Normalized Stock Factor {} {}".format(tg,self._stock[tg]/(self._population_scale_factor*self._normalization[tg])))

            self._shortfall_tracker[tg] += -1*int(self._stock[tg]/(5*self._population_scale_factor*self._normalization[tg]))
            if self._stock[tg]<0: 
                self._stock[tg] = 0

        


    def available(self, tg_name):
        return self._stock[tg_name] > 0


    def sample_good(self):
        tg_name = choice( list(filter(lambda x: self.available(x), self._supply.keys() )))
        return tg_name

    @property
    def supply(self):
        return self._stock

    def link_shid(self, subhid:SubHID):
        self._linked_shid = subhid

    def linked_shid(self)->SubHID:
        return self._linked_shid


    def get_market_price(self, good_name, fudge_supply=0):
        """
            We fudge the "supply" by the fudge supply value
        """
        fudge_shift = np.round(fudge_supply/(5*self._population_scale_factor*self._normalization[good_name]))

        return self._price[good_name]*(1.10**(self._shortfall_tracker[good_name] - fudge_shift))
    
    def add_route(self, which:TradeRoute):
        self._trade_routes[which.trade_good].append(which)

    @property
    def trade_routes(self)->'list[TradeRoute]':
        return self._trade_routes

    @property 
    def linked_world(self)->World:
        return self._linked_world
    
    def check_route(self, other_market:'Market', good_name:str, debug=False):
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
            return  None, None

        # recalculate this...
        profit = other_market.get_market_price(good_name, available) - self.get_market_price(good_name, -available)
        if profit <0:
            return None, None
        max_cargo = -1 
        max_margin = -1 
        ship_name = ""
        #print("checking route") 
        for entry in freighters:
            this_ship = freighters[entry]
            
            # profit moving the ship's cargo worth minus the operational costs 
            # so if there isn't a lot of cargo here, it won't be economical to
            margin = profit*min([this_ship.cargo_free(), available ]) - this_ship.get_route_expenses(other_market._linked_shid - self._linked_shid)
            if margin>max_margin:
                ship_name = entry 
                max_margin = margin 
                max_cargo = min([this_ship.cargo_free(), available ])
                if available>max_cargo:
                    max_cargo*=int(available/max_cargo)
                #print("    ", entry, margin)
                    
        if ship_name=="":
            return None, None
        new_route = TradeRoute([self._linked_shid.downsize(), other_market._linked_shid.downsize()], good_name, max_cargo)
        #self.add_route(new_route)
        #other_market.add_route(new_route)
        return new_route, freighters[ship_name], available