from traveller_utils.ships import ShipSWN
from traveller_utils.ships.ship_items import sample_ships
from traveller_utils.core.utils import roll 
from traveller_utils.places.world import World


class StarPort(ShipSWN):
    def __init__(self, starport_class, linked_world:World):
        station_template = "station{}Class".format(starport_class.upper())
        template_dict=sample_ships[station_template]
        self._load_template(template_dict)   

        self._linked_world = linked_world
