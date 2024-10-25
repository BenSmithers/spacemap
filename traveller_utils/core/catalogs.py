from traveller_utils.core import HexID, SubHID
from traveller_utils.places.world import World
from traveller_utils.places.system import System
from traveller_utils.ships import ShipSWN
from traveller_utils.ships.starport import StarPort

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
    def register(self, system: System, location: HexID):
        self._entries[location] = system
        
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
        result = []

        for i, hexid in hid_route:
            this_port = self.star_port(hexid)

            if i==0:
                pass 
        

    