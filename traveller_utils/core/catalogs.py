from traveller_utils.core import HexID, SubHID, NonPhysical
from traveller_utils.core.core import Region
from traveller_utils.places.world import World
from traveller_utils.places.system import System
from traveller_utils.places.poi import PointOfInterest
from traveller_utils.ships import ShipSWN
from traveller_utils.ships.starport import StarPort
from traveller_utils.places.trade_route import TradeRoute
from traveller_utils.core import utils
from traveller_utils.enums import SystemNote, PLocationType
from traveller_utils.person import Person
from traveller_utils.tables import passenger_table

import numpy as np 
from collections import deque


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


class RegionCatalog(Catalog):
    token_type=Region
    def __init__(self, draw_function: callable):
        super().__init__(draw_function)
        self._rid_from_hid = {}

    def get(self, shipID) -> Region:
        return super().get(shipID)
    def update(self, token:Region, id):
        """
            Un-assign the old ones, reassign new ones 
        """
        old_token = self.get(id)
        #for hid in old_token.hexIDs:
        #    self._rid_from_hid[hid] = None
        for hid in token.hexIDs:
            self._rid_from_hid[hid] = id

        return super().update(token, id)
    def register(self, region: Region):
        rid =  super().register(region)
        for hid in region.hexIDs:
            self._rid_from_hid[hid] = rid
        return rid 
    def get_rid(self, hid:HexID)->int:
        if hid in self._rid_from_hid:
            return self._rid_from_hid[hid]


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
        this_id  = super().register(ship)
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
        
        return []
        
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
        print("Moving ship {} to {}".format(ship_id, dest))
        old_loc = self.get_loc(ship_id)
        
        # first, for the specific listings 
        if old_loc in self._ships_at:
            if ship_id in self._ships_at[old_loc]:
                self._ships_at[old_loc].remove(ship_id)
        if dest not in self._ships_at:
            self._ships_at[dest] = []
        self._ships_at[dest].append(ship_id)


        # now the general listings 
        if old_loc is not None:
            hid_old_loc = old_loc.downsize()
            if hid_old_loc in self._ships_at_hid:
                if ship_id in self._ships_at_hid[hid_old_loc]:
                    self._ships_at_hid[hid_old_loc].remove(ship_id)  

        hid_dest= dest.downsize()
      
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
    def get_sub(self, subh:SubHID)->PointOfInterest:
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

        for i, hexid in enumerate(hid_route):
            if i==0:
                result.append(self.get(hexid).inflight)
                result.append(NonPhysical())
            else:
                system = self.get(hexid) 
                if system is None:
                    result.append(NonPhysical())
                else:
                    result.append(self.get(hexid).inflight)

                    result.append(self.get(hexid).get_notable(SystemNote.MainPort))
                    if i<len(hid_route)-1:
                        result.append(self.get(hexid).inflight)
                        result.append(NonPhysical())
             
        return result
    
    def reset_wealth(self):
        self._cummulative_wealths = []

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



    def _get_heuristic(self, start:HexID, end:HexID)->float:
        val =  abs(end - start)*6

        return val
    
    def _get_cost_between(self, start_id:HexID, end_id:HexID, ship:ShipSWN):
        """

        """
        # called on any two hexes, really... 
        cost = abs(end_id - start_id)*6/ship.drive_rating

        max_fuel = ship.fuel_max
        have_scoop = ship.has_fuel_scoop

        last_system = self.get(start_id)
        if last_system is None :
            last_scoop = False 
            last_has_station = False
        else:
            last_scoop = last_system.fuel and have_scoop
            last_has_station = last_system.starport is not None     
        
        next_system = self.get(end_id)
        if next_system is None:
            next_scoop = False
            next_has_station = False
        else:
            next_scoop = next_system.fuel and have_scoop
            next_has_station = next_system.starport is not None 

        if not (next_has_station or last_has_station):
            return np.inf

        # fly to a station and back to refuel 
        # two days there and two days back 
        penalty = 4.0/ship.drive_rating 
        if last_has_station and next_has_station:
            pass # both have fuel - no effect
        elif last_has_station or next_has_station:
            # one of the two have no fuel - but you have a scoop 
            if max_fuel==1: # you have only space for one fuel, so you need to refuel
                if ((not last_has_station) and last_scoop) or ((not next_has_station) and next_scoop):
                    penalty += 3.0 # add a few days to fuel-scoop
                else:
                    penalty = 10000
            
        else: # two in a row without stations 
            if max_fuel==1 :
                if last_scoop and next_scoop:
                    penalty += 6.0
                else:
                    penalty = 100000
            elif max_fuel==2:
                if last_scoop or next_scoop:
                    penalty += 3.0
                else:
                    penalty = 1000000 
                
        return cost + penalty

       
    
    def get_route_cost(self, hexIDs:'list[HexID]', ship_used:ShipSWN):
        cost = 0
        for i in range(len(hexIDs)-1):
            cost += self._get_cost_between(hexIDs[i], hexIDs[i+1], ship_used)
        return cost
    
    def get_route_a_star(self, start_id:HexID, end_id:HexID, ship_used:ShipSWN)->'list[HexID]':
        """
        Finds quickest route between two given HexIDs. Both IDs must be on the Hexmap.
        Always steps closer to the target

        Returns ordered list of HexIDs representing shortest found path between start and end (includes start and end)
        """
        # list of hexIDs, sorted by the heuristic calcualted from the destination
        openSet = deque([start_id,])
        sorted_costs = deque([])
        cameFrom = {}

        min_cost_to_hex = {}
        min_cost_to_hex[start_id] = 0.

        pred_cost_from_hex = {}
        pred_cost_from_hex[start_id] = self._get_heuristic(start_id,end_id)


        def reconstruct_path(cameFrom:'dict[HexID]', current:HexID)->'list[HexID]':
            total_path = [current,]
            while current in cameFrom.keys():
                current = cameFrom[current]
                total_path.append(current)
            
            return total_path[::-1]
        
        def add_to_openSet(which_id):
            if len(openSet)==0:
                openSet.append(which_id)
            else:
                # this could be a little faster with a binary search
                iter = 0
                
                # openSet is ordered based off of which one we think is closest 
                while pred_cost_from_hex[which_id] < pred_cost_from_hex[openSet[iter]]:
                    iter += 1
                    if iter==len(openSet):
                        break

                #sorted_costs.insert(iter, pred_cost_from_hex[neighbor])
                openSet.insert(iter,which_id)

        while len(openSet)!=0:
            from_hid = openSet.pop()
            if from_hid == end_id:
                return reconstruct_path(cameFrom, from_hid)

            for next_step in from_hid.in_range(ship_used.drive_rating, False):
                # true cost to here plus the cost to the neighbor 
                next_step_cost = min_cost_to_hex[from_hid] + self._get_cost_between(from_hid, next_step, ship_used)

                use_this_step = False
                if next_step not in min_cost_to_hex:
                    use_this_step = True
                elif next_step_cost < min_cost_to_hex[next_step]:
                    use_this_step = True
                if use_this_step:
                    min_cost_to_hex[next_step] = next_step_cost
                    cameFrom[next_step] = from_hid
                    pred_cost_from_hex[next_step] = min_cost_to_hex[next_step] + self._get_heuristic(next_step, end_id)
                    add_to_openSet(next_step)

        return([])
    
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

            if hexID not in self:
                without = True
            else:
                if self.get(hexID).starport is None:
                    without = True
                elif self.get(hexID).starport.category=="X" or self.get(hexID).starport.category=="E":
                    without = True

            if current > max_without:
                max_without = current

            if not without:
                current = 0 # reset it ! 
        
        # check one last time in case we got to the destination on the last step and still have no fuel (shouldn't happen, but w/e)
        if current > max_without:
            max_without = current
        
        return max_without

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

    def get(self, shipID) -> TradeRoute:
        return super().get(shipID)

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
            wealth_flow+= cost*dtons

        return -1*wealth_flow

    def all_connections(self, start:HexID):
        if start not in self._by_hid:
            return None 
        
        return self._by_hid[start]



    def register(self, route: TradeRoute):
        rid = super().register(route)
        for hid in  route.tons_per_month:
            if hid in self._by_hid:
                self._by_hid[hid].append(rid)
            else:
                self._by_hid[hid] = [rid, ]
            this_syst = self._system_cat.get(hid).starport.add_route(route)
        
        # now actually add the routes to the world
        stops = list(route.tons_per_month.keys())
        start_world = self._system_cat.get(stops[0])
        start_world.starport.add_route(route)
        end_world = self._system_cat.get(stops[1])
        end_world.starport.add_route(route)

        return rid 
    
"""

"""
class PassengerCatalog(Catalog):
    token_type = Person
    def __init__(self, draw_function: callable, trade_cat:TradeCat, systems_cat:SystemCatalog):
        # main one is ( pid -> Person )
        self._locations = {}  # pid -> hid 
        self._location_types = {}  # pid -> hid/shipid/etc
        self._persistent_pids = {} # hid -> { <low/mid/high> : [ pids ] }
        self._
        self._trade_cat = trade_cat
        self._systems_cat = systems_cat

        self._keys=["high", "middle", "basic", "low"]

        super().__init__(draw_function)

    def generate_empty(self):
        return {key:[] for key in self._keys}
    def get(self, pid)->Person:
        return super().get(pid)
    def register(self, person:Person):
        return super().register(person)
    def get_location(self, pid)->'tuple[SubHID, PLocationType]':
        if pid in self._locations:
            return self._locations[pid], self._location_types[pid]
    def get_permanent_at(self, hid):
        pass 

    def sample_passengers(self, hid, steward_mod:int):
        """
            Samples a list of passengers here.

            Numbers should depend on the flow of wealth here.
            And then we should sample passengers based on the world tags. 
        """
        persistent_here = self.get_permanent_at(hid)

        # from 0 to like, 4
        desireability = self._systems_cat.get(hid).mainworld.title.value
        categories = self._systems_cat.get(hid).mainworld.category
        
        empty_dict = self.generate_empty()
        for key in persistent_here:
           
            mod = steward_mod+desireability
            if key=="high":
                mod -= 4
            elif key=="mid":
                mod-=2
            elif key=="low":
                mod+=2
            
            die_roll = utils.roll() + mod 
            if die_roll<=0:
                n_pass = 0
            elif die_roll>len(passenger_table)-1:
                n_pass = sum(np.random.randint(1,7,10))
            else:
                n_pass =  sum(np.random.randint(1,7,passenger_table[die_roll]))
            
            if n_pass>0:
                empty_dict[key] += persistent_here[key]
            
            empty_dict[key] += [Person.generate(*categories) for i in range(n_pass - len(persistent_here[key]))]