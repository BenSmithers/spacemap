from traveller_utils.name_gen import create_name
from traveller_utils.places.world import World
from traveller_utils.places.poi import PointOfInterest, GasGiant
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
    
    def append(self, obj:PointOfInterest, of_note=SystemNote.Nothing):
        if isinstance(obj, GasGiant):
            self._gas_giants = True 
            self._fuel = True

        index= 0
        location = SubHID(self._system_location.xid, self._system_location.yid, index, 0)
        while location in self._regions:
            index +=1  
            location = SubHID(self._system_location.xid, self._system_location.yid, index, 0)
        self._regions[location] = obj

        if of_note.value==SystemNote.MainWorld.value:
            self._mainworld = location
        elif of_note.value==SystemNote.MainPort.value:
            self._starport = location 

        return location

    def insert(self, location:SubHID, obj,of_note=SystemNote.Nothing):
        assert location.downsize()==self._system_location
        
        if location in self._regions:
            # take whatever is already there and push it into the next region (recursively) 
            old_entry = self._regions[location]
            self._regions[location] = obj 
            new_location = SubHID(location.xid, location.yid, location.region +1, location.point)
            
            if self._starport==location:
                call_with = SystemNote.MainPort
            elif self._mainworld==location:
                call_with = SystemNote.MainWorld
            else:
                call_with = SystemNote.Nothing
            self.insert(new_location, old_entry, call_with)
        else:
            self._regions[location] = obj

        if of_note.value==SystemNote.MainWorld.value:
            self._mainworld = location
        elif of_note.value==SystemNote.MainPort.value:
            self._starport = location 

def generate_system(modifier, location:HexID):
    
    name = create_name("planet")

    # create main world
    new_system = System(location, name)


    new_world = World(True, modifier)
    world_loc = new_system.append(new_world, SystemNote.MainWorld)

    starport_loc = SubHID(world_loc.xid, world_loc.yid, world_loc.region, 1)
    

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


    tas = False
    if scout_roll>scout_lim:
        services.append(Bases.Scout)
    if naval_roll>naval_lim:
        services.append(Bases.Naval)
    if tas_roll>tas_lim:
        services.append(Bases.TAS)
        tas = True 
    if research_roll>res_lim:
        services.append(Bases.Research)

    if not no_starport:
        starport = StarPort(starport_class, tas)
        for entry in services:
            starport.add_service(entry)

        new_system.insert(starport_loc, starport, SystemNote.MainPort)

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