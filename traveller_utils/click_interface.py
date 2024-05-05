from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QMainWindow
from traveller_utils.actions import ActionManager, unpack_event, MonthlyEvent

from traveller_utils.enums import Title, Bases, WorldCategory
from traveller_utils.clock import minutes_in_day
from traveller_utils.coordinates import HexID, DRAWSIZE, screen_to_hex, hex_to_screen
from traveller_utils.ship import Ship, AIShip, AIShipMoveEvent
from traveller_utils.core import Hex, Region, Route
from traveller_utils.world import World
from traveller_utils import utils
from collections import deque
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


        self._systems = {}
        self._drawn_systems = {}

        self._regions = {}
        self._drawn_regions = {}

        self._routes = {}
        self._drawn_routes = {}

        # shipid->Ship
        self._ships = {} 
        #hexid->list[shipids]
        self._ship_locations={} 
        # -> hexID -> sid
        self._ship_sids = {} 

        self._cummulative_wealths = []

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

        if os.path.exists(WORLD_PATH):
            _obj = open(WORLD_PATH, 'rt')
            data = json.load(_obj)
            _obj.close()
            self.unpack(data)
        else:
            self.initialize_systems()
            self.initialize_routes()
            self.initialize_regions()
            n_ships = 60

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
        for hid in self._systems:
            world = self.get_system(hid)
            ts = world.wealth
            all_ts.append(ts)

        if False:
            import matplotlib.pyplot as plt 
            plt.hist(all_ts, bins=np.arange(0, 20,1))
            plt.xlabel("Wealth Score")
            plt.ylabel("Count")
            plt.show()


    def update_prices(self):
        for hid in self._systems:
            world = self.get_system(hid)
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
        if ship_id in self._ships:
            return self._ships[ship_id]
    def get_ships_at(self,hid:HexID)->'list[int]':
        if hid in self._ship_locations:
            return self._ship_locations[hid]
        else:
            return []
    
    def register_ship(self, ship:Ship, location:HexID):
        """
            finds the next available ship ID, registers the ship in the catalogs 
        """
        ship.set_location(location)

        ship_id = 0
        while ship_id in self._ships:
            ship_id+=1
        self._ships[ship_id] = ship
        if location not in self._ship_locations:
            self._ship_locations[location] = []
        self._ship_locations[location].append(ship_id)
        
        self.draw_ship(ship_id)
        return ship_id
        
    def delete_ship(self, ship_id):
        """
            deletes the entry in _ship_locations first
            then deletes it from the ship list
            then calls the draw function to remove the drawing on the screen
        """
        loc = self.get_ship(ship_id)
        if loc is not None:
            loc = loc.location
        self.get_ships_at(loc).remove(ship_id)

        if ship_id in self._ships:
            del self._ships[ship_id]
        self.draw_ships_hex(loc)


    def move_ship(self, ship_id, dest:HexID):
        """
            Updates maps regarding where a Ship is, plays an animation as it moves the icon
        """
        
        ship = self.get_ship(ship_id)
        old_loc = ship.location

        if ship_id in self._ship_locations[old_loc]:        
            self._ship_locations[old_loc].remove(ship_id)

        ship.set_location(dest)

        if dest not in self._ship_locations:
            self._ship_locations[dest] = []
        self._ship_locations[dest].append(ship_id)

        

        """     This wasn't working, I gave up on it... 
        sid = self._ship_sids[old_loc]
        start = sid.pos()
        end = hex_to_screen(dest)
        animation = QtCore.QPropertyAnimation(self._parent_window)
        animation.setTargetObject(sid)
        animation.setPropertyName(b"pos")
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setDuration(500) # ms 
        animation.start()
        """

        self.draw_ships_hex(old_loc)
        self.draw_ships_hex(dest)
        


    def closeEvent(self, event):
        packed= self.pack()
        _obj = open(WORLD_PATH, 'wt')
        json.dump(packed, _obj, indent=4)
        _obj.close()

    @property
    def systems(self):
        return self._systems

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
            
        for key in self._systems.keys():
            world = self.get_system(key)
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
            self._ships[ship_id] = AIShip.unpack(packed["ships"][_ship_id])
            loc = self._ships[ship_id].location
            if loc not in self._ship_locations:
                self._ship_locations[loc] = []
            self._ship_locations[loc].append(ship_id)
            self.draw_ship(ship_id)

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

    def _route_present(self, start:HexID, end:HexID):
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
        world = self.get_system(hexID)
        skip = world.generated

        all_passengers = world.generate_passengers(mod)
        if skip:
            return all_passengers

        n_gen = 0
        for berth_key in all_passengers.keys():
            n_gen+= len(all_passengers[berth_key])
        destinations = self.choose_dest(hexID, n_gen)

        item = 0
        for berth_key in all_passengers.keys():
            for passenger in all_passengers[berth_key]:
                passenger.set_destination(destinations[item])
                #passenger.set_destination(self.get_system(destinations[item]))
                item += 1

        return all_passengers

    def choose_dest(self, source:HexID, samples=1)->HexID:
        """
        Uses desireability of worlds around a given HexID to sample `samples` destinations 
        Punishes distant destinations
        """

        max_dist = 6
        all_possible = source.in_range(6)
        all_possible = list(filter(lambda x:x in self._systems, all_possible))
        all_possible = list(filter(lambda entry:entry!=source, all_possible))

        distance_weight = np.array([(source - entry)**2 for entry in all_possible])
        desireability = np.array([self.get_system(hid).desireability for hid in all_possible])
        desireability += min(desireability)

        total_weights = desireability.astype(float)**2 / distance_weight
 
        total_weights+=np.min(total_weights)
        total_weights /= np.sum(total_weights)

        dests = [np.random.choice(all_possible,size=1, p = total_weights)[0] for i in range(samples)]

        return dests
    

    def update_world(self, other:World, hid:HexID)->None:
        """
            Swaps out the world at hid with the world provided. We then redraw the world, 
            and clear out the cummulative wealths list so that it's regenerated later
        """
        self._cummulative_wealths = []
        self._systems[hid] = other
        self.draw_hex(hid)

    def _sample_from_wealth(self)->HexID:
        """
            samples a HexIDs based on system wealth

            We first get all of the worlds' wealths, and save the cummulative sum. The sum of all wealths is used for sampling
        """

        # get all of the wealths and accumulate them. Only do this if it hasn't been done already
        all_keys = list(self.systems.keys())
        if len(self._cummulative_wealths)==0:
            self._cummulative_wealths = [self.get_system(key).wealth for key in all_keys]
            self._cummulative_wealths = np.cumsum(self._cummulative_wealths).tolist()
        

        sampled = np.random.rand()*self._cummulative_wealths[-1]
        index = utils.get_loc(sampled, self._cummulative_wealths)[0]
        return all_keys[index]
                
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
            next_step = this_ship.step()
            self.move_ship(ship_id, next_step)    
            if this_ship.is_done(): # no more steps after this 
                self.delete_ship(ship_id)    
                self._initialize_ship()    
                return 1 
            else:
                return 0
            
    def _initialize_ship(self, start_hex=None):
        """
            samples a ship's origin from the wealth distribution of worlds in the sector
            Chooses a route for the ship to follow: if this is an endpoint for a route, use one of the routes
            otherwise sample the endpoint from the same wealth distribution 

            Then make a ship and queue its travel
        """
        if start_hex is None:
            loc = self._sample_from_wealth()
        else:
            assert isinstance(start_hex, HexID), "Received non-HexID start hex: {}".format(type(start_hex))
            loc = start_hex

        if loc in self._routes:
            key_choice = choice(list( self._routes[loc] ))
            route = self._routes[loc][key_choice].route # route object to list! 
        else:
            other = self._sample_from_wealth()
            route = self.get_route_a_star(loc, other)

        new_ship = AIShip.generate(route)
        if "freighter" in new_ship.description.lower():
            scale = 4
            samples = 1
            if "medium" in new_ship.description:
                scale = 6
                samples = 2
            elif "large" in new_ship.description:
                scale = 12
                samples = 3 
            for i in range(samples):
                cargo, quantity = self.get_system(loc).sample_cargo(scale)
                new_ship.add_cargo(cargo, quantity)
            

        sid = self.register_ship(new_ship, loc)
        move = AIShipMoveEvent(
            recurring = Time(minute=int(minutes_in_day/new_ship.rate)),
            n_events = len(route),
            ship_id=sid
        )
        next_time = self.clock.time +  Time(minute=int(60*np.random.randint(-100,120) +minutes_in_day/new_ship.rate))
        self.add_event(move, next_time)


    def initialize_routes(self):
        """
            Use the SwoN rules to create hyperlane trade routes between systems
        """
        for system_key in self.systems.keys():
            this_world = self.get_system(system_key)

            if WorldCategory.Industrial in this_world.category or WorldCategory.High_Tech in this_world.category:
                check = [
                    WorldCategory.Asteroid,
                    WorldCategory.Desert,
                    WorldCategory.Ice_Capped,
                    WorldCategory.Non_Industrial
                ]
            elif WorldCategory.High_Pop in this_world.category or WorldCategory.Rich in this_world.category:
                check = [
                    WorldCategory.Agricultural,
                    WorldCategory.Garden, 
                    WorldCategory.Water_World
                ]
            else:
                continue

            
            in_range = system_key.in_range(4, False)
            in_range = list(filter(lambda x:x in self._systems, in_range))
            for other_key in in_range:
                other_world = self.get_system(other_key)
                if any([entry in other_world.category for entry in check]):
                    # draw route! 
                    if  not self._route_present(system_key, other_key):
                        route_raw = self.get_route_a_star(system_key, other_key)
                        level = self.get_route_level(route_raw)
                        route = Route(route_raw, level)
                        if len(route)>6:
                            continue
                        if route.level<=2:
                            self.add_route(system_key, other_key, route)

        self.draw_routes()

    def add_route(self, start:HexID, end:HexID, route:Route):
        """
            Internally reggister the route from the given start and end hexid

            note: the start and end aren't needed, right? 
        """

        if self._route_present(start, end):
            return
        else:
            if start not in self._routes:
                self._routes[start] = {}
            if end not in self._routes:
                self._routes[end] = {}
            
            # we do this so that it's symmetric
            self._routes[start][end] = route
            self._routes[end][start] = route
            for i, hid in enumerate(route):
                world = self.get_system(hid)
                if i==0 or i==(len(route)-1):
                    amt = 2
                else:
                    amt = 0.5
                if world is not None:
                    #world.iterate_ts()
                    world.set_ts(world.trade_score + amt)
                    self._systems[hid] = world

    def draw_route_to(self, start:HexID, to:HexID):
        """
            This is exclusively used to draw routes a passenger would want to take 
        """
        self.clear_drawn_route()

        this_route = self.get_route_a_star(start, to)
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
        for route in self._routes.keys():
            for destination in self._routes[route].keys():
                self.draw_route(route, destination)

    def all_connections(self, start)->'list[HexID]':
        if start in self._routes:
            return list(self._routes[start].keys())
        else:
            return []

    def draw_route(self, start, end, highlight=False):
        if start not in self._drawn_routes:
            self._drawn_routes[start]={}

        if end in self._drawn_routes[start]:
            if self._drawn_routes[start][end] is not None:
                self.removeItem(self._drawn_routes[start][end])
                self._drawn_routes[start][end] = None
        
        if start not in self._routes:
            return
        if end not in self._routes[start]:
            return

        full_path = self._routes[start][end]
        
        shift = full_path.level-1

        vertices = [hex_to_screen(hid) for hid in full_path]
        path = QtGui.QPainterPath()
        path.addPolygon(QtGui.QPolygonF(vertices))
        self._pen.setStyle(1 if full_path.level==1 else 3)                
        self._pen.setWidth(8 if highlight else 5)
        if highlight:
            self._pen.setColor(QtGui.QColor(255, 231, 71))
        else:
            if full_path.level==1:
                self._pen.setColor(QtGui.QColor(150,255,150))
            else:
                
                self._pen.setColor(QtGui.QColor(255,250-40*shift,250-40*shift))
            
        self._brush.setStyle(0)
        sid = self.addPath(path, self._pen, self._brush)
        sid.setZValue(2)
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

                    self._systems[loc] = World(modifier = mod)
        
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
                
                #cost = self.get_route_cost(self.get_route_a_star(hID, other_hid))
                #print(cost)
                influence = self.get_system(other_hid).wealth/5
                influence_map[hID][other_hid] = max([influence - 1.5*distance, 0])

        for hID in self._systems.keys():
            world = self.get_system(hID)


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

            if ultimate_liege in self._regions:
                original = self._regions[ultimate_liege]
                self._regions[ultimate_liege] = original.merge(new)
            else:
                self._regions[ultimate_liege] = new


        for rid in self._regions.keys():
            self.draw_region(rid)



    def initialize_regions(self):
        by_title={
            Title.Emperor:[],
            Title.King:[],
            Title.Duke:[],
            Title.Count:[],
            Title.Lord:[]
        }
        for key in self._systems:
            world = self.get_system(key)
            world.update_category()
            by_title[world.title].append(key)
        """
            For each title, we assign each lower ranking house to an upper one. There are chances for each level that a given house has no liege 

            So, each Duke is assigned to its nearest king
        """
        max_dist = 3
        ordered_labels= [Title.Lord, Title.Count, Title.Duke, Title.King, Title.Emperor]
        odds = [0.01, 0.08, 0.25, 0.40, 1.0]

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


                this_world = self.get_system(system_id)
                senior_world = self.get_system( use[senior_index])

                this_world.set_liege(use[senior_index] , senior_world)
                senior_world.add_vassal(system_id, this_world)
        
        for system in self._systems.keys():
            

            center = hex_to_screen(system)
            this_hex = Hex(center)

            new = Region(this_hex, system)

            ultimate_liege = self.get_ultimate_liege(system)

            if ultimate_liege in self._regions:
                original = self._regions[ultimate_liege]
                self._regions[ultimate_liege] = original.merge(new)
            else:
                self._regions[ultimate_liege] = new


        for rid in self._regions.keys():
            self.draw_region(rid)

    def draw_all_hexes(self):
        for i in range(30):
            for j in range(15):
                shift = int(i/2)
                loc = HexID(i ,j-shift)
                if loc in self._systems:
                    self.draw_system(loc)
                else:
                    self.draw_hex(loc)

    def get_ultimate_liege(self, hexID:HexID):
        world = self.get_system(hexID)
        liege = world.liege
        if liege is None:
            return hexID
        else:
            return self.get_ultimate_liege(liege)


    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        loc =  screen_to_hex( event.scenePos() )

        if loc in self._systems: 
            self._selected_hid = loc 
            self.draw_selection(loc)
            self._parent_window.planet_selected(self._systems[loc], loc )
        else:
            self._selected_hid = None 
            self._parent_window.select_none()
            if self._selected_sid is not None:
                self.removeItem(self._selected_sid)
            self._selected_sid = None
    

    def get_system(self, hex_id:HexID)->World:
        if hex_id in self._systems:
            return self._systems[hex_id]
        else:
            return None
        
    def get_region(self, hex_id:HexID)->Region:
        if hex_id in self._regions:
            return self._regions[hex_id]
        else:
            return None
        
    def draw_hex(self, hex_id:HexID):
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

    def draw_region(self, origin:HexID):
        if origin in self._drawn_regions:
            for entry in self._drawn_regions[origin]:
                self.removeItem(entry)

        this_region = self.get_region(origin)
        if this_region is None:
            del self._drawn_regions[origin]
            return 
            
        self._pen.setStyle(0)
        self._brush.setStyle(1)
        self._brush.setColor(QtGui.QColor(this_region.fill))

        sid = self.addPolygon(this_region, self._pen, self._brush)
        self._drawn_regions[origin] = (sid, )

    def draw_ship(self, ship_id):
        this_ship = self.get_ship(ship_id)
        loc = this_ship.location
        
        self.draw_ships_hex(loc)

    def draw_ships_hex(self, loc):
        if loc in self._ship_sids:
            self.removeItem(self._ship_sids[loc])
            del self._ship_sids[loc]

        all_ships = self.get_ships_at(loc)

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

        this_world = self.get_system(hex_id)
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

        if Bases.Naval in this_world.services or Bases.Scout in this_world.services:
            sid_base = self.addPixmap(self.icon_map.access("anchor", 0.3*DRAWSIZE))
            sid_base.setX(center.x()-DRAWSIZE*0.75)
            sid_base.setY(center.y()-DRAWSIZE*0.15)
            sid_base.setZValue(12)
            all_sids.append(sid_base)
        if Bases.TAS in this_world.services:
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

            if hexID not in self._systems:
                without = True
            else:
                if self.get_system(hexID).starport_cat=="X" or self.get_system(hexID).starport_cat=="E":
                    without = True

            if current > max_without:
                max_without = current

            if not without:
                current = 0 # reset it ! 
        
        # check one last time in case we got to the destination on the last step and still have no fuel (shouldn't happen, but w/e)
        if current > max_without:
            max_without = current
        
        return max_without


    def _get_heuristic(self, start:HexID, end:HexID)->float:
        val =  abs(end - start)
        return val
    
    def _get_cost_between(self, start_id:HexID, end_id:HexID):
        # only called on neighboring hexes 
        cost = abs(end_id - start_id)

        # if that one is unknown, it has no starport. Avoid! 
        if end_id not in self._systems:
            cost*= 7 # no starport
            if start_id not in self._systems:
                cost*=7 # penalize double-nothings a lot 
        else:
            # avoid ones with no starport
            fuel = self.get_system(end_id).fuel_present()

            if fuel==0:
                cost *= 4 # no fuel
                
                if start_id in self._systems:
                    if self.get_system(start_id).fuel_present()==0:
                        cost *= 7
                else:
                    cost *= 7

            # and also penalize ones with bad fuel 
            elif fuel<3:
                cost *= 1.2
        return cost
    
    def get_route_cost(self, hexIDs:'list[HexID]'):
        cost = 0
        for i in range(len(hexIDs)-1):
            cost += self._get_cost_between(hexIDs[i], hexIDs[i+1])
        return cost
    
    def get_route_a_star(self, start_id:HexID, end_id:HexID)->'list[HexID]':
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

            for next_step in from_hid.neighbors:
                # true cost to here plus the cost to the neighbor 
                next_step_cost = min_cost_to_hex[from_hid] + self._get_cost_between(from_hid, next_step)

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