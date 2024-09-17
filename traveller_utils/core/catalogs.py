from traveller_utils.core import HexID, SubHID
from traveller_utils.places.world import World
from traveller_utils.ships import ShipSWN

class Catalog:
    token_type = int
    def __init__(self, draw_function:function):
        self._ships = {}
        self._ship_locations = {} #ship_id -> SubHID
        self._ships_at = {} # SubHID -> list[ship_ids]
        self._ships_at_hid = {} # HexID -> list[ship_ids]

        self._function = draw_function

    def update(self, token, id):
        """
            Updates the object with the id 'id' 
        """
        self._ships[id] = token 

        # now we need to re-draw thing, whereever it is 
        location = self.get_loc(id)
        if location is not None:
            self.draw(location)
        

    def register(self, ship:token_type, location:SubHID):
        ship_id = 0
        while ship_id in self._ships:
            ship_id+=1
        self._ships[ship_id] = ship 

        self.move(ship_id, location)

        return ship_id

    def delete(self, id):
        location = self.get_loc(id)
        
        self.get_at(location).remove(id)
        if id in self._ships:
            del self._ships[id]
        
        self.draw(location)

            

    def draw(self, location:SubHID):
        return self._function(location)


    def get_loc(self, shipID)->SubHID:
        if shipID in self._ship_locations:
            return self._ship_locations[shipID]
         
    def get(self, shipID)->token_type:
        if shipID in self._ships:
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

class ShipCatalog(Catalog):
    def register(self, ship: ShipSWN, location: SubHID):
        return super().register(ship, location)
    def get(self, shipID) -> ShipSWN:
        return super().get(shipID)
    def get_at(self, hid: HexID) -> 'list[ShipSWN]':
        return super().get_at(hid)


class SystemCatalog(Catalog):
    def has_fuel(self, hID:HexID):
        pass 
    def main_world(self, hID:HexID)->World:
        pass 
    def star_port(self, hID:HexID)->ShipSWN:
        pass