from traveller_utils.factions.moves import AttackAction
from traveller_utils.factions.base_classes import Roll
from traveller_utils.factions.base_classes import Asset
from traveller_utils.factions.enums import AssetTheme, AssetType

class Smugglers(Asset):
    max_hp = 4
    cost = 2
    tl = 4 
    type = AssetType.Starship
    theme = AssetTheme.cunning
    defense_theme = AssetTheme.wealth

    def __init__(self):
        Asset.__init__(self)
        
        self._hp = 4

        self._location = None
        self._hasattack = True
        self._damage = Roll("1d4")

class Informers(Asset):
    max_hp=3
    cost=2
    tl=4
    type=AssetType.SpecialForces
    defense_theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._damage = Roll("0d4")
        self._special = True
        self._hasattack = True 

class FalseFront(Asset):
    max_hp=2
    cost=1
    tl=0
    type=AssetType.LogisticsFacility
    def __init__(self):
        super().__init__()
        self._damage = Roll("0d4")

class Lobbyists(Asset):
    max_hp=4
    cost=4
    tl=0
    rank=2
    type=AssetType.SpecialForces
    def __init__(self):
        super().__init__()
        self._damage = Roll("0d4")
        self._special = True
        self._hasattack = True


class Saboteurs(Asset):
    max_hp =6
    cost=5
    tol=0
    type=AssetType.SpecialForces
    theme = AssetTheme.cunning
    defense_theme=AssetTheme.cunning
    rank=2
    def __init__(self):
        super().__init__()
        self._special = True 
        self._damage = Roll("2d4")
        self._hasattack = True
class Blackmail(Asset):
    hp=4
    rank =2
    tl=0 
    cost=4
    theme=AssetTheme.cunning
    type=AssetType.Tactic
    defense_theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._damage = Roll("1d4+1")
        self._hasattack = True
class Seductress(Asset):
    rank=2
    hp=4
    cost=4
    tl=4
    type=AssetType.SpecialForces
    theme=AssetTheme.cunning
    defense_theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._special = True 
        self._hasattack = True

# special -stealth 
class Cyberninjas(Asset):
    rank=3
    hp=4
    cost=6
    tl=4
    type=AssetType.SpecialForces
    theme=AssetTheme.cunning
    defense_theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._damage = Roll("2d6")
        self._hasattack = True
class Covert_Shipping(Asset):
    rank=3
    hp=4
    cost=8
    tl=4
    type=AssetType.LogisticsFacility
    theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()

class Party_Machine(Asset):
    rank=4
    hp=10
    cost=8
    tl=0
    type=AssetType.LogisticsFacility
    defense_theme =AssetTheme.cunning

    theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._damage = Roll("2d6")
        self._hasattack = True
class Vanguard_Cadres(Asset):
    rank=4
    hp=12
    cost=8
    tl=3
    theme=AssetTheme.cunning
    defense_theme =AssetTheme.cunning
    type=AssetType.MilitaryUnit
    def __init__(self):
        super().__init__()
        self._damage = Roll("1e6")
        self._hasattack = True
class Tripwire_Cells(Asset):
    rank=4
    hp=8
    cost=12
    cl=4
    theme=AssetTheme.cunning
    type=AssetType.SpecialForces
    def __init__(self):
        super().__init__()
class Seditionists(Asset):
    rank=4
    hp=8
    cost=12
    tl=0
    theme=AssetTheme.cunning
    type=AssetType.SpecialForces
    def __init__(self):
        super().__init__()

class Organization_Moles(Asset):
    rank=5
    hp=8
    cost=10
    tl=0
    theme=AssetTheme.cunning
    defense_theme =AssetTheme.cunning
    type=AssetType.Tactic
    def __init__(self):
        super().__init__()
        self._damage = Roll("2d6")
        self._hasattack = True
class Cracked_Comms(Asset):
    rank=5
    hp=6
    cost=12
    tl=0
    theme=AssetTheme.cunning
    type=AssetType.Tactic
    def __init__(self):
        super().__init__()
class Boltholes(Asset):
    rank=5
    hp=6
    cost=12
    tl=4
    theme=AssetTheme.cunning
    type=AssetType.LogisticsFacility
    def __init__(self):
        super().__init__()

class Transport_Lockdown(Asset):
    rank=6
    hp=10
    cost=20
    tl=4
    theme=AssetTheme.cunning
    defense_theme =AssetTheme.cunning
    type=AssetType.Tactic
    def __init__(self):
        super().__init__()
        self._special = True 
        self._hasattack = True
class Covert_Transit_Net(Asset):
    rank=6
    hp=15
    cost=18
    tl=4
    theme=AssetTheme.cunning
    type=AssetType.LogisticsFacility
    def __init__(self):
        super().__init__()
class Demagogue(Asset):
    rank=6
    hp=10
    cost=20
    tl=0
    theme=AssetTheme.cunning
    defense_theme =AssetTheme.cunning
    type=AssetType.SpecialForces
    def __init__(self):
        super().__init__()
        self._damage = Roll("2d8")
        self._hasattack = True

class Popular_Movement(Asset):
    rank=7
    hp=16
    cost=25
    tl=4
    theme=AssetTheme.cunning
    type=AssetType.Tactic
    defense_theme =AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._damage = Roll("2d6")
        self._hasattack = True
class Book_of_Secrets(Asset):
    rank=7
    hp=10
    cost=20
    tl=4
    theme=AssetTheme.cunning
    type=AssetType.Tactic
    def __init__(self):
        super().__init__()
class Treachery(Asset):
    rank=7
    hp=5
    cost=10
    tl=0
    theme=AssetTheme.cunning
    type=AssetType.Tactic
    defense_theme =AssetTheme.cunning
    def __init__(self):
        super().__init__()
        self._special = True 
        self._hasattack = True

class Panopticon_Matric(Asset):
    rank=8
    hp=20
    cost=30
    tl=5
    type=AssetType.LogisticsFacility
    theme=AssetTheme.cunning
    def __init__(self):
        super().__init__()