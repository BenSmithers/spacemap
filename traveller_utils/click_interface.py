from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QMainWindow
from traveller_utils.actions import ActionManager, unpack_event, MonthlyEvent

from traveller_utils.enums import Title, Bases, ShipCategory, ShipClass, SystemNote
from traveller_utils.tables import wealth_tbl
from traveller_utils.clock import minutes_in_day
from traveller_utils.core.coordinates import HexID, DRAWSIZE, screen_to_hex, hex_to_screen, SubHID, NonPhysical
from traveller_utils.ships.ship import Ship, AIShip, AIShipMoveEvent, sample_ship
from traveller_utils.core.core import Hex, Region, Route
from traveller_utils.places.world import World
from traveller_utils.places.poi import PointOfInterest, InFlight
from traveller_utils.places.system import generate_system, System
from traveller_utils.core import utils
from traveller_utils.core.catalogs import ShipCatalog, SystemCatalog, TradeCat, RegionCatalog


import numpy as np
import os 
import json
from random import choice
from traveller_utils.clock import Time, Clock
water_color = (92, 157, 214)
no_water = (38, 38, 38)

WORLD_PATH = os.path.join(os.path.dirname(__file__), "..","galaxy.json")


class Clicker(QGraphicsScene,ActionManager):
    def __init__(self, parent, parent_window:QMainWindow, clock:Clock):
        QGraphicsScene.__init__(self, parent=parent, clock=clock)
        ActionManager.__init__(self, clock=clock)

        self._parent_window = parent_window
        #self.parent().scale( 0.8, 0.8 )

        self.pmap = utils.IconLib(os.path.join(os.path.dirname(__file__), "..","images","planets"))
        self.icon_map = utils.IconLib(os.path.join(os.path.dirname(__file__),"..","images","icons"), ext="svg")


        self._drawn_systems = {}

        self._regions = RegionCatalog(self.draw_region)
        self._drawn_regions = {}

        self._routes = {}
        self._drawn_routes = {}

        # -> hexID -> sid
        self._ship_sids = {} 

        self._ship_catalog = ShipCatalog(self.draw_ships_hex)
        self._system_catalog = SystemCatalog(self.draw_hex)
        self._trade_cat = TradeCat(self.draw_route, self._system_catalog)

        self._alt_select = None
        self._alt_route_sid = None

        self._pen = QtGui.QPen() # STROKE EFFECTS
        self._pen.setColor(QtGui.QColor(240,240,240))
        self._pen.setStyle(Qt.PenStyle.SolidLine )
        self._pen.setWidth(5)
        self._brush = QtGui.QBrush() 
        self._brush.setStyle(0)

        self.font=QtGui.QFont()
        self.font.setBold(True)


        self._selected_sid = None
        self._selected_hid = None

        if False:# os.path.exists(WORLD_PATH):
            _obj = open(WORLD_PATH, 'rt')
            data = json.load(_obj)
            _obj.close()
            self.unpack(data)
        else:
            self.initialize_systems()
            self.initialize_routes()
            self.initialize_regions()
            n_ships = 1

            for i in range(n_ships):
                self._initialize_ship()

        self.draw_all_hexes()

        self._parent_window._calendar_widget.signals.signal.connect(self.skip_to_time)

        self.update()        


        self.add_event(
            MonthlyEvent(),
            Time(0,0, 0, self.clock._time.month+1,self.clock._time.year)
        )
        

        all_ts = []
        for hid in self._system_catalog:
            world = self.get_system(hid).mainworld
            #ts = world.wealth
            ts = self._trade_cat.wealth_flow(hid)
            all_ts.append(ts)

        if False:
            import matplotlib.pyplot as plt 
            plt.hist(all_ts, bins=np.linspace(min(all_ts), max(all_ts), 100))
            plt.xlabel("Wealth Score")
            plt.ylabel("Count")
            plt.show()


    def update_prices(self):
        print("One month has passed")
        return
        for hid in self._system_catalog:
            world = self.get_world(hid)
            # clear out the passenger lists
            for p_class in world._passengers:
                world._passengers[p_class] = []
            world._generated = False
            
            for retail in world._retailers:
                retail.clear()
        if self._selected_hid is not None:
            self._parent_window._pass_widget.clear_pass()
            self._parent_window.planet_selected(self._systems[self._selected_hid], self._selected_hid )
            

    def get_ship(self, ship_id)->Ship:
        return self._ship_catalog.get(ship_id)

    def closeEvent(self, event):
        return 
        packed= self.pack()
        _obj = open(WORLD_PATH, 'wt')
        json.dump(packed, _obj, indent=4)
        _obj.close()

    @property
    def systems(self)->SystemCatalog:
        return self._system_catalog
    
    @property
    def regions(self)->RegionCatalog:
        return self._regions

    def pack(self)->dict:
        return {
            "time":self.clock.time.pack(),
            "ships":{
                ship_id:self._ships[ship_id].pack() for ship_id in self._ships.keys()
            },
            "queue":[[entry[0].pack(), entry[1].pack()] for entry in self.queue],
            "systems":{key.pack():self.systems[key].pack() for key in self.systems.keys()},
            "regions":{rkey.pack():self._regions[rkey].pack() for rkey in self._regions.keys()},
            "routes":{
                key.pack():{
                    subkey.pack():self._routes[key][subkey].pack() for subkey in self._routes[key]
                } for key in self._routes
            }
        }
    
    def unpack(self, packed:dict):
        if "time" in packed:
            self.clock._time = Time.unpack(packed["time"])
        
        
        self._parent_window._calendar_widget.set_time(self.clock._time)

        if "queue" in packed:
            self._queue = [[Time.unpack(entry[0]), unpack_event(entry[1])] for entry in packed["queue"]]
            
        for i in range(30):
            for j in range(15):
                shift = int(i/2)
                loc = HexID(i ,j-shift)
                if loc.pack() in packed["systems"]:
                    self._systems[loc] = World.unpack(packed["systems"][loc.pack()])
          
        for key in packed["regions"]:
            id_unpacked = HexID.unpack(key)
            self._regions[id_unpacked] = Region.unpack(packed["regions"][key])
            self.draw_region(id_unpacked)
            
        for key in self._system_catalog:
            world = self.get_world(key)
            if world._liege is not None:
                world.set_liege(key, self.get_system(world.liege))

            # we gotta be bad
            vassal_ids = world.vassals
            world._vassals = []

            for entry in vassal_ids:
                world.add_vassal(entry, self.get_system(entry))
        
        for key in packed["routes"]:
            keyunpack = HexID.unpack(key)
            self._routes[keyunpack] = {}
            for subkey in packed["routes"][key]:
                subkey_unpack = HexID.unpack(subkey)
                self._routes[keyunpack][subkey_unpack] = Route.unpack(packed["routes"][key][subkey])
        self.draw_routes()

        for _ship_id in packed["ships"].keys():
            ship_id=int(_ship_id)
            self._ship_catalog.update(AIShip.unpack(packed["ships"][_ship_id]), ship_id)
            self._ship_catalog.move(ship_id, 0)
            print("NEED TO GET LOCATION")

    def draw_alt(self, hexID:HexID):
        if self._alt_select is not None:
            self.removeItem(self._alt_select)
        center = hex_to_screen(hexID)

        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor( 118, 219, 216 ))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        self._alt_select = self.addPolygon(this_hex, self._pen, self._brush)
        self._alt_select.setZValue(99)

    def draw_selection(self, hex_id):
        """
            Draw a blue hexagon on the planet you selected
        """
        if self._selected_sid is not None:
            self.removeItem(self._selected_sid)


        center = hex_to_screen(hex_id)
        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor(118, 216, 219))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        self._selected_sid = self.addPolygon(this_hex, self._pen, self._brush)
        self._selected_sid.setZValue(100)

    def _route_present(self, start:SubHID, end:SubHID):
        if start not in self._routes and end not in self._routes:
            return False
        # a route exists with either start or end as the start point
        elif start in self._routes:
            if end in self._routes[start]:
                return True #start->end
        else: #end is the actual start in some route 
            if start in self._routes[end]:
                return True #end->start
            
        return False 
    
    def generate_passengers(self, hexID, mod=0):
        system = self.get_system(hexID)
        skip = False
        if system is None:
            skip = True 
        starport = system.starport
        if starport is None:
            skip = True 
        if skip:
            return {
                    "high":[],
                    "middle":[],
                    "basic":[],
                    "low":[], 
                }
        
        now_skip = starport.generated

        all_passengers = starport.generate_passengers(mod)
        if now_skip:
            return all_passengers


        n_gen = 0
        for berth_key in all_passengers.keys():
            n_gen+= len(all_passengers[berth_key])
        destinations = self._system_catalog.choose_dest(hexID, n_gen)

        item = 0
        for berth_key in all_passengers.keys():
            for ip, passenger in enumerate(all_passengers[berth_key]):
                passenger.set_destination(destinations[item])
                all_passengers[berth_key][ip] = passenger
                item += 1

        return all_passengers
    

                
    def step_ai_ship(self, ship_id)->bool:
        """
            Gets the AI ship, makes sure it's an AI-ship type
            Then steps it to the next place, updates the map, and deletes it in the case that it is now done moving 

            returns True if it deleted the ship
            returns False otherwise
        """
        this_ship = self.get_ship(ship_id)
        assert isinstance(this_ship, AIShip), "Ship was not an AIShip! it's a {}".format(type(this_ship))
        if this_ship is None:
            return 0
        else:
            moving_from = self._ship_catalog.get_loc(ship_id)
            next_step = this_ship.step()            
            self._ship_catalog.move(ship_id, next_step)

            if this_ship.is_done(): # no more steps after this 
                self._ship_catalog.delete(ship_id)    
                self._initialize_ship()    
                return 1 
            else:
                new_event = AIShipMoveEvent(
                    ship_id
                )
                
                """
                    Station->Inflight 8 hours (refuel) 
                    InFlight->NonPhysical  48 hours
                    NonPhysical->Inflight  6 days per hex
                    InFlight->Starport  48 hours
                """
                                    
                if isinstance(next_step, NonPhysical):
                    time_minutes = 2*24*60/this_ship.drive_rating # time to fly to the edge of system
                elif isinstance(moving_from, NonPhysical):
                    # six days per hex
                    # TODO actually make this per hex and not per-jump
                    time_minutes = 6*24*60/this_ship.drive_rating
                else:
                    next_place = self.get_sub(next_step)
                    if isinstance(next_place, InFlight):
                        time_minutes = 8*60 
                        this_ship.refuel()
                    else:
                        time_minutes = 2*24*60/this_ship.drive_rating

                next_time = self.clock.time +  Time(minute=int(time_minutes))
                self.add_event(new_event, next_time)

                return 0
            
    def _initialize_ship(self, start_hex=None):
        """
            samples a ship's origin from the wealth distribution of worlds in the sector
            Chooses a route for the ship to follow: if this is an endpoint for a route, use one of the routes
            otherwise sample the endpoint from the same wealth distribution 

            Then make a ship and queue its travel
        """

        new_ship = AIShip.generate([], ShipClass.Frigate, ShipCategory.Freight)

        if start_hex is None:
            loc = self._system_catalog.sample_from_wealth()
        else:
            assert isinstance(start_hex, HexID), "Received non-HexID start hex: {}".format(type(start_hex))
            loc = start_hex
        
        while True:
            print("looping")
            loc = self._system_catalog.sample_from_wealth()
            if loc is None:
                raise ValueError()
            if self._system_catalog.get(loc) is None:
                continue
            starport = self._system_catalog.get(loc).get_notable(SystemNote.MainPort)
            if starport is None:
                continue
            else:
                break


        ## TODO sample routes from the known routes

        other = self._system_catalog.sample_from_wealth()
        route = self._system_catalog.get_route_a_star(loc, other, new_ship)

        expanded = self._system_catalog.expand_route(route)

        new_ship.set_route(expanded)


        print(self._system_catalog.get(loc).get_notable(SystemNote.MainPort))
        sid = self._ship_catalog.register(new_ship, self._system_catalog.get(loc).get_notable(SystemNote.MainPort))
        move = AIShipMoveEvent(
            ship_id=sid
        )
        
        time_minutes = 60*np.random.randint(1,240)

        next_time = self.clock.time +  Time(minute=time_minutes)
        self.add_event(move, next_time)


    def initialize_routes(self):
        """
            See if there are profitable trade routes within 4 hexes of the current system

        """

        print("... Finding Trade Routes")
        for system_key in self._system_catalog:
            this_world = self.get_system(system_key)
            market = this_world.starport
            if market is None:
                continue
            for good_name in market.supply:
                if "illegal" in good_name.lower():
                    continue

                modified_supply = market.get_modified_supply(good_name)
                if modified_supply<1:
                    continue

                in_range = system_key.in_range(8, False)
                in_range = list(filter(lambda x:x in self._system_catalog, in_range))

                for other_key in in_range:
                    other_system = self.get_system(other_key)
                    if other_system is None:
                        continue
                    other_market = other_system.starport
                    if other_market is None:
                        continue

                    result = market.check_route(other_market, good_name)
                    if result is None:
                        continue

                    new_route, ship_template = result

                    route = self._system_catalog.get_route_a_star(system_key, other_key, ship_template)
                    if self._system_catalog.get_route_cost(route, ship_template)>100000.0:
                        #print("bad route? - {}".format(self._system_catalog.get_route_cost(route, ship_template)))
                        continue
                    
                    new_route.set_level(self._system_catalog.get_route_level(route))
                    new_route.set_full_route(route)

                    #self._trade_cat.register(system_key, other_key, new_route)
                    self._trade_cat.register(new_route)

                    modified_supply = market.get_modified_supply(good_name)
                    if modified_supply<1:
                        break
                    


        self.draw_routes()


    def draw_route_to(self, start:HexID, to:HexID):
        """
            This is exclusively used to draw routes a passenger would want to take 
        """
        self.clear_drawn_route()

        this_route = self._system_catalog.get_route_a_star(start, to)
        vertices = [hex_to_screen(hid) for hid in this_route]

        path = QtGui.QPainterPath()
        path.addPolygon(QtGui.QPolygonF(vertices))
        self._pen.setStyle(1)                
        self._pen.setWidth(5)
        self._pen.setColor(QtGui.QColor(150,150,255))
        self._brush.setStyle(0)
        self._alt_route_sid = self.addPath(path, self._pen, self._brush)
        self._alt_route_sid.setZValue(20)
        

    def clear_drawn_route(self):
        """
            clears the drawing of the route a passenger would like to take to get somewhere
        """
        if self._alt_route_sid is not None:
            self.removeItem(self._alt_route_sid)
            self._alt_route_sid= None


    def draw_routes(self):
        """
            draws all of the routes
        """
        print("drawing routes")
        for key in self._trade_cat:
            self.draw_route(key)

    def all_connections(self, start)->'list[HexID]':
        return self._trade_cat.all_connections(start)

    def draw_route(self, route_id, highlight=False):
        route = self._trade_cat.get(route_id)
        tpm =list(route.tons_per_month.keys())
        start = tpm[0]
        end = tpm[1]

        if start not in self._drawn_routes:
            self._drawn_routes[start]={}

        if end in self._drawn_routes[start]:
            if self._drawn_routes[start][end] is not None:
                self.removeItem(self._drawn_routes[start][end])
                self._drawn_routes[start][end] = None
        
    
        full_path = route.full_route
        
        shift = route.level-1
        shift = 1

        vertices = [hex_to_screen(hid) for hid in full_path]
        path = QtGui.QPainterPath()
        path.addPolygon(QtGui.QPolygonF(vertices))
        self._pen.setStyle(1 if route.level==1 else 3)                
        self._pen.setWidth(8 if highlight else 5)
        if highlight:
            self._pen.setColor(QtGui.QColor(255, 231, 71))
        else:
            if route.level==1:
                self._pen.setColor(QtGui.QColor(150,255,150))
            else:
                
                self._pen.setColor(QtGui.QColor(255,250-40*shift,250-40*shift))
            
        self._brush.setStyle(0)
        sid = self.addPath(path, self._pen, self._brush)
        sid.setZValue(3)
        self._drawn_routes[start][end]=sid

    def initialize_systems(self):
        sample = utils.perlin(150,octave=3)*0.6 + utils.perlin(150,octave=15)*0.40
        sample = sample*0.9+0.4
        extra_thresh = 0.9*np.max(sample)
        
        for i in range(30):
            for j in range(15):
                this_val = sample[i*5][j*5]
                shift = int(i/2)
                loc = HexID(i ,j-shift)
                if np.random.rand()<this_val:       
                    mod = 0 if this_val<extra_thresh else 2

                    new_system = generate_system(mod, loc)
                    #new_system.starport.link_shid(loc)
                    self._system_catalog.register(new_system, loc)

        
    def alt_initialize_regions(self):
        """
            My idea for this one is that each system will exact some 'influence' on all of the other systems. 
            Influence will be determined by the wealth of a system (and maybe presence of bases?), but then fall off with distance.
                --> influence will be wealth/5, falls off by 1 per hex, empty hexes count as two. 


            A system will be a vassal of another system if its influence on the other system is small compared to the influence of the other system on it. 
        """

        # threshold in 
        THRESH = 1

        # map of influence on [first] from [second]
        influence_map = {}

        for hID in self._systems.keys():
            influence_map[hID] = {}
            for other_hid in self._systems.keys():
                if other_hid==hID:
                    influence_map[hID][other_hid] = 0

                distance = hID - other_hid
                if distance>4:
                    influence_map[hID][other_hid] = 0
                    continue
                
                #print(cost)
                influence = self.get_system(other_hid).mainworld.wealth/5
                influence_map[hID][other_hid] = max([influence - 1.5*distance, 0])

        for hID in self._system_catalog.keys():
            world = self.get_system(hID).mainworld


            keys = list(influence_map[hID].keys()) 
            values = list(influence_map[hID].values())
            if max(values)==0:
                continue

            hid_max = keys[values.index(max(values))] # this is the world that has the most influence on hID 
            if hid_max==hID:
                continue
            liege = self.get_system(hid_max)
            world.set_liege(hid_max, liege)
            liege.add_vassal(hID, world)


        
        for system in self._systems.keys():
            center = hex_to_screen(system)
            this_hex = Hex(center)

            new = Region(this_hex, system)

            ultimate_liege = self.get_ultimate_liege(system)
            rid = self._regions.get_rid(ultimate_liege)

            if rid is not None:
                original = self._regions.get(rid)
                self._regions.update(original.merge(new), rid)
            else:
                self._regions.register(new)


        for rid in self._regions:
            self.draw_region(rid)



    def initialize_regions(self):
        by_title={
            Title.Emperor:[],
            Title.King:[],
            Title.Duke:[],
            Title.Count:[],
            Title.Lord:[]
        }

        
        all_wealths = [[key, self._trade_cat.wealth_flow(key)] for key in self._system_catalog]
        sorted(all_wealths, key=lambda x:x[1])
        all_wealths = all_wealths[::-1]

        # combine these 

        for key, wealth in all_wealths:
            world = self.get_system(key).mainworld
            world.set_wealth(wealth)
            world.update_category()
            world.set_title(wealth_tbl.access(wealth))
            #self._system_catalog.update(world, key)
            by_title[world.title].append(key)
        """
            For each title, we assign each lower ranking house to an upper one. There are chances for each level that a given house has no liege 

            So, each Duke is assigned to its nearest king
        """
        max_dist = 3
        ordered_labels= [Title.Lord, Title.Count, Title.Duke, Title.King, Title.Emperor]
        odds = [0.005, 0.04, 0.25, 0.40, 1.0]

        for i, title in enumerate(ordered_labels):
            #if title==Title.Emperor:
            #    continue
            for system_id in by_title[title]:
                roll = np.random.rand()
                if roll<odds[i]:
                    continue

                use = []
                all_lists = [by_title[ordered_labels[j]] for j in range(i+1, 5)]
                for entry in all_lists:
                    use+= entry
       
                if len(use)==0:
                    continue

                """if len(by_title[ordered_labels[i+1]])==0 and i<(len(ordered_labels))-2:
                    use = by_title[ordered_labels[i+2]]
                else:
                    use = by_title[ordered_labels[i+1]]
                if len(use)==0:
                    continue"""

                distances = [system_id-senior_id for senior_id in use]
                if min(distances)>max_dist:
                    continue
                senior_index = distances.index(min(distances))


                this_world = self.get_system(system_id).mainworld
                senior_world = self.get_system( use[senior_index]).mainworld

                this_world.set_liege(use[senior_index] , senior_world)
                senior_world.add_vassal(system_id, this_world)
        
        for i, title in enumerate(ordered_labels[::-1]):
            #if title==Title.Emperor:
            #    continue
            for system in by_title[title]:            
                center = hex_to_screen(system)
                this_hex = Hex(center)

                new = Region(this_hex, system)

                ultimate_liege = self.get_ultimate_liege(system)
                rid = self._regions.get_rid(ultimate_liege)

                if rid is not None:
                    original = self._regions.get(rid)
                    merged = original.merge(new)
                    self._regions.update(merged, rid)


                else:
                    self._regions.register(new)


        for rid in self._regions:
            self.draw_region(rid)

    def draw_all_hexes(self):
        for i in range(30):
            for j in range(15):
                shift = int(i/2)
                loc = HexID(i ,j-shift)
                if loc in self._system_catalog:
                    self.draw_system(loc)
                else:
                    self.draw_hex(loc)

    def get_ultimate_liege(self, hexID:HexID):
        world = self.get_system(hexID).mainworld
        liege = world.liege
        if liege is None:
            return hexID
        else:
            return self.get_ultimate_liege(liege)

    def mouseDoubleClickEvent(self, event:QGraphicsSceneMouseEvent)->None:
        loc =  screen_to_hex( event.scenePos() )
        if loc in self._system_catalog:
            self._parent_window.system_selected(self.get_system(loc), loc) 

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        loc =  screen_to_hex( event.scenePos() )

        if loc in self._system_catalog: 
            self._selected_hid = loc 
            self.draw_selection(loc)
            self._parent_window.planet_selected(self.get_system(loc), loc )
        else:
            self._selected_hid = None 
            self._parent_window.select_none()
            if self._selected_sid is not None:
                self.removeItem(self._selected_sid)
            self._selected_sid = None
    

    def get_system(self, hex_id:HexID)->System:
        return self._system_catalog.get(hex_id)
        
    def get_sub(self, shi: SubHID)->PointOfInterest:
        return self._system_catalog.get_sub(shi)

        
    def draw_hex(self, hex_id:HexID):
        return
        if hex_id in  self._drawn_systems:
            for entry in self._drawn_systems[hex_id]:
                self.removeItem(entry)

        center = hex_to_screen(hex_id)
        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor(150,150,150))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        sid = self.addPolygon(this_hex, self._pen, self._brush)
        sid.setZValue(0)
        self._drawn_systems[hex_id] = (sid,)

    def draw_region(self, rid:int, highlight=False):
        if rid in self._drawn_regions:
            for entry in self._drawn_regions[rid]:
                self.removeItem(entry)

        this_region = self._regions.get(rid)
        if this_region is None:
            if rid in self._drawn_regions:
                del self._drawn_regions[rid]
            return 
            
        self._pen.setStyle(0)
        #if highlight:
            #self._pen.setColor(QtGui.QColor(255, 20, 20))
        self._brush.setStyle(6 if highlight else 1)
        if highlight:
            self._brush.setColor(QtGui.QColor(255, 50, 50))
        else:
            self._brush.setColor(QtGui.QColor(this_region.fill))

        sid = self.addPolygon(this_region, self._pen, self._brush)
        self._drawn_regions[rid] = (sid, )

    def draw_ship(self, ship_id):
        this_ship = self.get_ship(ship_id)
        loc = this_ship.location
        
        self.draw_ships_hex(loc)

    def draw_ships_hex(self, loc):
        if loc is None:
            return
        if loc in self._ship_sids:
            self.removeItem(self._ship_sids[loc])
            del self._ship_sids[loc]

        all_ships = self._ship_catalog.get_at(loc)


        names = ["one", "two", "three", "four", "more"]
        index = len(all_ships)-1
        if index==-1:
            return 
        index = 4 if index>4 else index

        center = hex_to_screen(loc)
        sid = self.addPixmap(self.icon_map.access("{}_ship".format(names[index], 0.4*DRAWSIZE)))
        sid.setX(center.x()-DRAWSIZE*0.75)
        sid.setY(center.y()-DRAWSIZE*0.45)
        sid.setZValue(12)

        self._ship_sids[loc] = sid
            
        

    def draw_system(self, hex_id:HexID):
        if hex_id in  self._drawn_systems:
            for entry in self._drawn_systems[hex_id]:
                self.removeItem(entry)

        this_system = self.get_system(hex_id)
        this_world = this_system.mainworld
        this_starport = this_system.starport
        
        if this_world is None:
            del self._drawn_systems[hex_id]
            return

        if this_world._hydro>2:
            color = water_color
        else:
            color = no_water

        center = hex_to_screen(hex_id)
        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor(150,150,150))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        sid = self.addPolygon(this_hex, self._pen, self._brush)
        
        self._brush.setStyle(1)
        self._pen.setStyle(0)
        self._brush.setColor(QtGui.QColor(*color))

        all_sids = [sid,]

        if (this_world.liege is None):
            self.font.setBold(True)
            sid_5 = self.addPixmap(self.icon_map.access("crown", 0.4*DRAWSIZE))
            sid_5.setX(center.x()-0.22*DRAWSIZE)
            sid_5.setY(center.y()-0.55*DRAWSIZE)
            sid_5.setZValue(11)
            all_sids.append(sid_5)
        else:
            self.font.setBold(False)

        sid_4 = self.addText(this_world._name, self.font)
        sid_4.setX(center.x()-0.25*DRAWSIZE)
        sid_4.setY(center.y()-DRAWSIZE*0.75)
        sid_4.setZValue(10)
        all_sids.append(sid_4)
        

        sid_3 = self.addText(this_world.world_profile(hex_id) )# , location=QtCore.QPointF(center.x(), center.y()+DRAWSIZE*0.25))
        sid_3.setX(center.x()-0.5*DRAWSIZE)
        sid_3.setY(center.y()+DRAWSIZE*0.4)
        sid_3.setZValue(10)
        all_sids.append(sid_3)

        #sid_2 = self.addEllipse(center.x()-DRAWSIZE*0.25, center.y()-DRAWSIZE*0.25, DRAWSIZE*0.5, DRAWSIZE*0.5, self._pen, self._brush)

        sid_2 = self.addPixmap(self.pmap.access(this_world.get_image_name(), 0.8*DRAWSIZE))
        sid_2.setX(center.x()-DRAWSIZE*0.4)
        sid_2.setY(center.y()-DRAWSIZE*0.4)
        sid_2.setZValue(10) 
        all_sids.append(sid_2)

        if this_starport is not None:
            if Bases.Naval in this_starport.services or Bases.Scout in this_starport.services:
                sid_base = self.addPixmap(self.icon_map.access("anchor", 0.3*DRAWSIZE))
                sid_base.setX(center.x()-DRAWSIZE*0.75)
                sid_base.setY(center.y()-DRAWSIZE*0.15)
                sid_base.setZValue(12)
                all_sids.append(sid_base)
            if Bases.TAS in this_starport.services:
                sid_plus = self.addPixmap(self.icon_map.access("plus", 0.3*DRAWSIZE))
                sid_plus.setX(center.x()+DRAWSIZE*0.5)
                sid_plus.setY(center.y()-DRAWSIZE*0.15)
                sid_plus.setZValue(12)
                all_sids.append(sid_plus)
        
       
        self._drawn_systems[hex_id] = tuple(all_sids)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Called when a keyboard button is released
        """
        event.accept()
        if event.key() == QtCore.Qt.Key_Plus or event.key()==QtCore.Qt.Key_PageUp or event.key()==QtCore.Qt.Key_BracketRight:
            self.parent().scale( 1.05, 1.05 )

        if event.key() == QtCore.Qt.Key_Minus or event.key()==QtCore.Qt.Key_PageDown or event.key()==QtCore.Qt.Key_BracketLeft:
            self.parent().scale( 0.95, 0.95 )

