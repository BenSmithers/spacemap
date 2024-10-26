from traveller_utils.core import HexID, SubHID
from traveller_utils.places.world import World
from traveller_utils.places.system import System
from traveller_utils.ships import ShipSWN
from traveller_utils.ships.starport import StarPort
from traveller_utils.places.trade_route import TradeRoute
from traveller_utils.core import utils

import numpy as np 

class Catalog:
    token_type = int
    def __init__(self, draw_function:callable):
        self._entries = {}

        self._function = draw_function

    def __in__(self, what):
        return what in self._entries

    def __iter__(self):
        return self._entries.__iter__()

    def update(self, token, id):
        """
            Updates the object with the id 'id' 
        """
        self._entries[id] = token 
        self.draw(id)
    
    def draw(self, location:token_type):
        """
            Re-draws whatever is at the token type
        """
        return self._function(location)
    
             
    def get(self, shipID)->token_type:
        if shipID in self._entries:
            return self._entries[shipID]

    def register(self, ship:token_type):
        ship_id = 0
        while ship_id in self._entries:
            ship_id+=1
        self._entries[ship_id] = ship 

        return ship_id

    def delete(self, id):
        if id in self._entries:
            del self._entries[id]

        self.draw(id)



class ShipCatalog(Catalog):
    token_type = int
    def __init__(self, draw_function:callable):
        Catalog.__init__(self, draw_function)
        self._ship_locations = {} #ship_id -> SubHID
        self._ships_at = {} # SubHID -> list[ship_ids]
        self._ships_at_hid = {} # HexID -> list[ship_ids]

        self._function = draw_function

    def delete(self, id):
        location = self.get_loc(id)
        
        self.get_at(location).remove(id)
        Catalog.delete(self, id)

        self.draw(location)

    def update(self, token, id):
        """
            Updates the object with the id 'id' 
        """
        Catalog.update(self, token, id)

        # now we need to re-draw thing, whereever it is 
        location = self.get_loc(id)
        if location is not None:
            self.draw(location)

    def register(self, ship:token_type, location:SubHID):
        this_id  = Catalog.register(ship)
        self.move(this_id, location)
        return this_id


    def get_loc(self, shipID)->SubHID:
        if shipID in self._ship_locations:
            return self._ship_locations[shipID]

    def get_at(self, hid:HexID)->list:
        if isinstance(hid, SubHID):
            use_dict =self._ships_at
        elif isinstance(hid, HexID):
            use_dict = self._ships_at_hid
        else:
            raise TypeError("Unknown ID type {}".format(type(hid)))

        if hid in use_dict:
            return use_dict[hid] 
        
    def draw(self, location):
        """
            If we're given a SubHID, we downsize to a HexID and draw
            If it's a HexID, we just draw
            If it's neither, we assume it's a ship id, get its location, and draw
        """
        if isinstance(location, SubHID):
            use_id = location.downsize()
        elif isinstance(location,HexID):
            use_id = location 
        else:
            use_id = self.get_loc(location)
        self._function(use_id)


    def move(self, ship_id, dest:SubHID):
        """
            Updates internal maps to represent the new ship location
            Then call 
        """
        old_loc = self.get_loc(ship_id)
        
        # first, for the specific listings 
        if ship_id in self._ships_at[old_loc]:
            self._ships_at[old_loc].remove(ship_id)
        if dest not in self._ships_at:
            self._ships_at[dest] = []
        self._ships_at[dest].append(ship_id)


        # now the general listings 
        hid_old_loc = old_loc.downsize()
        hid_dest= dest.downsize()
        if ship_id in self._ships_at_hid[hid_old_loc]:
            self._ships_at_hid[hid_old_loc].remove(ship_id)        
        if hid_dest not in self._ships_at_hid:
            self._ships_at_hid[hid_dest] = []
        self._ships_at_hid[hid_dest].append(ship_id)

        self._ship_locations[ship_id] = dest

        self.draw(old_loc)
        self.draw(dest)

class SystemCatalog(Catalog):
    token_type=HexID
    def __init__(self, draw_function: callable):
        super().__init__(draw_function)
        self._cummulative_wealths = []

    def update(self, token, id):
        self._cummulative_wealths = []
        return super().update(token, id)
    
    def register(self, system: System, location: HexID):
        self._entries[location] = system
        self._cummulative_wealths = []
        
    def get(self, hid:HexID)->System:
        return super().get(hid)
    def getworld(self, subh:SubHID)->World:
        system = self.get(subh.downsize())
        return system.get(subh)
    
    def has_fuel(self, hID:HexID):
        this_system = self.get(hID)
        return this_system.fuel 
     
    def main_world(self, hID:HexID)->World:
        this_system = self.get(hID)
        return this_system.mainworld
      
    def star_port(self, hID:HexID)->StarPort:
        this_system = self.get(hID)
        return this_system.starport
    
    def insert_world(self, hID, world:World):
        this_system = self.get(hID)
        this_system.append(world)
        self.update(this_system, hID)

    def expand_route(self, hid_route:'list[HexID]')->'list[SubHID]':
        """
            Takes a list of HexIDs and expands it out to include stops at each starport (or a gas giant)
        """
        result = []

        for i, hexid in hid_route:
            this_port = self.star_port(hexid)

            if i==0:
                pass 
        raise NotImplementedError()
    
    def sample_from_wealth(self):
        # get all of the wealths and accumulate them. Only do this if it hasn't been done already
        all_keys = list(self._entries.keys())
        if len(self._cummulative_wealths)==0:
            self._cummulative_wealths = [self.get(key).mainworld.wealth for key in all_keys]
            self._cummulative_wealths = np.cumsum(self._cummulative_wealths).tolist()
        

        sampled = np.random.rand()*self._cummulative_wealths[-1]
        index = utils.get_loc(sampled, self._cummulative_wealths)[0]
        return all_keys[index]    
    
    def choose_dest(self, source:HexID, samples=1)->HexID:
        """
        Uses desireability of worlds around a given HexID to sample `samples` destinations 
        Punishes distant destinations
        """

        max_dist = 6
        all_possible = source.in_range(6)
        all_possible = list(filter(lambda x:x in self, all_possible))
        all_possible = list(filter(lambda entry:entry!=source, all_possible))

        distance_weight = np.array([source.distance(entry)**2 for entry in all_possible])
        desireability = np.array([self.get(hid).mainworld.desireability for hid in all_possible])
        desireability += min(desireability)

        total_weights = desireability.astype(float)**2 / distance_weight
 
        total_weights+=np.min(total_weights)
        total_weights /= np.sum(total_weights)

        dests = [np.random.choice(all_possible,size=1, p = total_weights)[0] for i in range(samples)]

        return dests 

class TradeCat(Catalog):
    """
        Contains all of the trade routes, interfaces with a systems catalog to then access flow of wealth across the systems 

        So, practically 
    """
    token_type=TradeRoute 
    def __init__(self, draw_function: callable, systems:SystemCatalog):
        Catalog.__init__(self, draw_function)
        self._system_cat = systems

        self._by_hid = {} # hexID -> list(route IDs)

    def get_routes(self, superHID:SubHID)->'list[int]':
        if isinstance(superHID, SubHID):
            index = superHID.downsize()
        else: 
            index = superHID

        if index in self._by_hid:
            return self._by_hid[index]


    def wealth_flow(self, hid:HexID):
        """
            Get all the routes starting/stopping here. 
            For each one, get the prices for the starting and stopping system
                purchase price * tonnage --> 

            Returns the wealth flowing in or out of this system
        """
        related_routes = self.get_routes(hid)
        market = self._system_cat.get(hid).starport
        if related_routes is None:
            return 0.0 

        wealth_flow = 0.0
        for routeid in related_routes:
            route = self.get(routeid)
            dtons = route.tons_per_month[hid]
            cost = market.get_market_price(route.trade_good)
            # negative because an outflow of goods is an inflow of cash
            wealth_flow+= -1*cost*dtons

        return wealth_flow


    def register(self, route: TradeRoute):
        rid = super().register(route)
        for hid in  route.tons_per_month:
            if hid in self._by_hid:
                self._by_hid[hid].append(rid)
            else:
                self._by_hid[hid] = [rid, ]
        
        return rid 
    
    def get_route_level(self, route:'list[HexID]')->int:
        """
            Returns the "level" of a route 
                level 1 means there is a fuel source for every jump
                level 2 means there may be stops without fuel, but no two consequtively 
                level 3 means there may be two consequtive stps without fuel, but not three
                etc etc
        """
        max_without = 0
        current = 0

        # current will keep growing for each step as long as 
        for hexID in route:
            current += 1
            without = False

            if hexID not in self._system_cat:
                without = True
            else:
                if self._system_cat.get(hexID).starport.category=="X" or self._system_cat.get(hexID).starport.category=="E":
                    without = True

            if current > max_without:
                max_without = current

            if not without:
                current = 0 # reset it ! 
        
        # check one last time in case we got to the destination on the last step and still have no fuel (shouldn't happen, but w/e)
        if current > max_without:
            max_without = current
        
        return max_without