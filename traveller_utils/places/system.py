from traveller_utils.name_gen import create_name
from traveller_utils.places.world import World
from traveller_utils.core.utils import roll 
from traveller_utils.tables import starports_str
from traveller_utils.ships import StarPort
from traveller_utils.enums import Bases


def generate_system(modifier):
    
    name = create_name("planet")

    # create main world

    new_world = World(True, modifier)

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


    starport = StarPort(starport_class, tas)


    # generate other worlds 

    # generate gas giant or two 
    has_gas_giant = roll() < 10
    if has_gas_giant:
        n_giants = int(roll()/2)
    else:
        n_giants = 0

    

    
    
    return []