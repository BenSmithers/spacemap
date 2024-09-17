from traveller_utils.ships import ShipSWN
from traveller_utils.enums import ShipCategory

class Fleet:
    def __init__(self, fleet_template:'dict[str]', category:ShipCategory):
        self._category = category
        self._ships = {}

        self._template = {}
        for key in fleet_template.keys():
            if key in self._template:
                self._template[key] += fleet_template[key]
            else:
                self._template[key] = fleet_template[key]

        self._members = {}

    @property
    def category(self):
        return self._category

    def add_ship(self, _ship):
        if isinstance(_ship, str):
            ship = ShipSWN.load_from_template(_ship)
        elif isinstance(_ship, ShipSWN):
            ship = _ship
        else:
            raise TypeError()

        name = ship.template
        if name in self._members:
            self._members[name].append(ship)
        else:
            self._members[name] = [ship, ]
        
        if self._template[name] < len(self._members[name]):
            self._template[name] = len(self._members[name])

    @property
    def ships(self):
        return self._ships