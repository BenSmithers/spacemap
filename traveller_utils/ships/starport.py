from traveller_utils.ships import ShipSWN
from traveller_utils.ships.ship_items import sample_ships
from traveller_utils.name_gen import sample_adjective, sample_noun
from traveller_utils.core.utils import roll 
from traveller_utils.places.world import World

from traveller_utils.places.terminal import Terminal
from traveller_utils.places.market import Market

class StarPort(ShipSWN, Market):
    def __init__(self, starport_class, linked_world:World):
        
        station_template = "station{}Class".format(starport_class.upper())
        template_dict=sample_ships[station_template]
        ShipSWN.__init__(self, template_dict["shipHullType"])
        self._load_template(template_dict)   

        self._linked_world = linked_world

        Terminal.__init__(self, linked_world)
        Market.__init__(self, linked_world)

        self._services = []

        self._category = starport_class.upper()

        linked_world.name
        self._name = linked_world.name + "'s" + " {} Starbase".format(sample_adjective())
    @property
    def category(self):
        return self._category

    def add_service(self, what):
        self._services.append(what)

    @property
    def services(self):
        return self._services