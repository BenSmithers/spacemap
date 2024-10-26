from traveller_utils.name_gen import create_name
from traveller_utils.places.world import World
from traveller_utils.places.poi import PointOfInterest, GasGiant, InterRegion, InFlight
from traveller_utils.core.utils import roll 
from traveller_utils.tables import starports_str
from traveller_utils.ships import StarPort
from traveller_utils.enums import Bases, SystemNote
from traveller_utils.core.coordinates import SubHID, HexID

class System:
    def __init__(self, hID:HexID, name:str):
        self._regions = {}
        
        self._system_location = hID
        self._name = name
        self._starport =None 
        self._mainworld = None

        self._fuel = False 
        self._gas_giants = False 
        self._location_inter = SubHID(hID.xid, hID.yid,0,0)
        self._regions[self._location_inter] = InFlight()

    @property
    def inflight(self):
        return self._location_inter

    def get(self, subh:SubHID):
        if subh in self._regions:
            return self._regions[subh]

    @property
    def fuel(self):
        return self._fuel

    @property
    def starport(self)->StarPort:
        if self._starport is not  None:
            return self._regions[self._starport]
    @property
    def mainworld(self)->World:
        return self._regions[self._mainworld]
    
    def get_notable(self, of_note:SystemNote):
        if of_note.value == SystemNote.MainPort.value:
            return  self._starport
        elif of_note.value == SystemNote.MainWorld.value:
            return self._mainworld
        else:
            return 
    
    def append(self, obj:PointOfInterest, of_note=SystemNote.Nothing):
        """
            Append a new region 
        """
        if isinstance(obj, GasGiant):
            self._gas_giants = True 
            self._fuel = True

        index= 1
        interloc = SubHID(self._system_location.xid, self._system_location.yid, index, 0)
        location = SubHID(self._system_location.xid, self._system_location.yid, index, 1)
        while interloc in self._regions:
            index +=1  
            interloc = SubHID(self._system_location.xid, self._system_location.yid, index, 0)
            location = SubHID(self._system_location.xid, self._system_location.yid, index, 1)
        self._regions[interloc] = InterRegion()
        self._regions[location] = obj

        if of_note.value==SystemNote.MainWorld.value:
            self._mainworld = location
        elif of_note.value==SystemNote.MainPort.value:
            self._starport = location 

        return location

    def insert(self, region_number, obj, of_note=SystemNote.Nothing):
        """
            Insert an object into a region
        """
        test = SubHID(self._system_location.xid, self._system_location.yid, region_number, 0)
        if test not in self._regions:
            self._regions[test] = InterRegion()
            location = SubHID(self._system_location.xid, self._system_location.yid, region_number, 1)
        else: 
            index = 1 
            location = SubHID(self._system_location.xid, self._system_location.yid, region_number, index)
            while location in self._regions:
                index+=1 
                location = SubHID(self._system_location.xid, self._system_location.yid, region_number, index)
        
        self._regions[location] = obj 
        
        if of_note.value==SystemNote.MainWorld.value:
            self._mainworld = location
        elif of_note.value==SystemNote.MainPort.value:
            self._starport = location 
        return location

def generate_system(modifier, location:HexID)->System:
    
    name = create_name("planet")

    # create main world
    new_system = System(location, name)

    new_world = World(True, modifier)
    world_loc = new_system.append(new_world, SystemNote.MainWorld)
    
    # generate services 

    # build spaceport 
    star_mod = 0 
    if new_world._population_raw>=8:
        star_mod = 1
    if new_world._population_raw>=10:
        star_mod=2
    if new_world._population_raw<=4:
        star_mod=-1
    if new_world._population_raw<=2:
        star_mod=-2
    starport_roll = roll(mod=star_mod) + modifier
    if starport_roll>= len(starports_str):
        starport_roll = len(starports_str)-1

    services = []

    naval_roll = roll()
    scout_roll = roll()
    research_roll = roll()
    tas_roll = roll()

    tas_lim = 14
    naval_lim = 14
    scout_lim = 14
    res_lim = 14
    no_starport = False 
    starport_class = starports_str[starport_roll]
    if starport_class=="A":
        tas_lim = 0
        naval_lim = 7
        scout_lim = 9
        res_lim = 7
    elif starport_class=="B":
        tas_lim = 0
        naval_lim = 7
        scout_lim = 7
        res_lim = 9
    elif starport_class=="C":
        tas_lim = 9
        scout_lim = 7
        res_lim = 9
    elif starport_class=="D":
        scout_lim = 6
    else:
        tas_lim = 1000
        scout_lim = 1000
        res_lim = 1000
        naval_lim = 1000
        no_starport = True 


    if scout_roll>scout_lim:
        services.append(Bases.Scout)
    if naval_roll>naval_lim:
        services.append(Bases.Naval)
    if tas_roll>tas_lim:
        services.append(Bases.TAS)
    if research_roll>res_lim:
        services.append(Bases.Research)

    if not no_starport:
        starport = StarPort(starport_class, new_world)
        for entry in services:
            starport.add_service(entry)
        
        starport_loc = new_system.insert(world_loc.region, starport, SystemNote.MainPort)
        starport.link_shid(starport_loc)
    # generate other worlds 

    # generate gas giant or two 
    has_gas_giant = roll() < 10
    if has_gas_giant:
        n_giants = int(roll()/2)
    else:
        n_giants = 0

    for i in range(n_giants):
        new_gas = GasGiant()
        new_system.append(new_gas)
    


    return new_system