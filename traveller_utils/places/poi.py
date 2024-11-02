from random import randint

def get_origin():
    value = randint(1,8)
    if value ==1:
        return "Recent colony from the primary world."
    elif value==2:
        return "Refuge for exiles from primary."
    elif value==3:
        return "Founded ages ago by a different group"
    elif value==4:
        return "Founded long before the primary world"
    elif value==5:
        return "Lost ancient colony of hte primary"
    elif value==6:
        return "Colony recently torn free of the primary"
    elif value==7:
        return "Long-standing cooperative colony world"
    elif value==8:
        return "Recent interstellar colony from elsewhere"
    else:
        raise Exception()
    
def make_point_of_interest():

    points = ["Deep-space station", "Asteroid based", "Remote moon base", "Ancient orbital ruin",
                "surface mine", 
                "Research base", "Asteroid belt", "Gas giant mine", "Refueling station"]

    occupiers = [
            ["Dangerously odd transhumans", "Freeze-dried ancient corpses", "Scretive military observers", "Eccentric oligarch and minions", "Deranged but brilliant scientist"],
            ["Zealous religions sectarians", "Failed rebels from another world", "Wage-slave corporate miners", "Independent asteroid prospectors", "Pirates masquerading as otherwise"],
            ["Unlucky corporate researchers", "Reclusive hermit genius", "Remnants of a failed colony", "Military listening post", "Lonely overseers and robot miners"],
            ["Robots of dubious sentience","Trigger-happy scavengers", "Government researchers","Military quarantine enforcers","Heirs of the original alien builders"],
            ["Experiments that have gotten loose","Scientists from a major local corp", "Black-ops governmental researchers","Secret employees of a foreign power","Aliens studying the human locals"],
            ["Grizzled belter mine laborers", "Ancient automated guardian drones","Survivors of destroyed asteroid base","Pirates hiding out among the rocks","Lonely military patrol base staff"],
            ["Miserable gas-miner slaves or serfs","Strange robots and their overseers","Scientists studying the alien life", "Scrappers in the ruined old mine", "Impoverished separatist group"],
            ["Half-crazed hermit caretaker","Sordid purveyors of decadent fun","Extortionate corporate minions","Religious missionaries to travelers","brainless autmoated vendors"]
        ]

    situation=[
            ["Sysdtems breaking down", "Foreign sabotage attempt", "black market for the elite","vault for dangerous pretech", "suply base for pirates"],
            ["Life support is threatened","base needs a new asteroid","Dug out something nasty","Fighting another asteroid","hit a priceless vein of ore"],
            ["something dark has awoken", "criminals trying to take over","moon plague breaking out","desperate for vital supplies","rich but badly-protected"],
            ["Trying to stop it awakening","Meddling with strange tech","Impending tech calamity","a terrible secret is unearthed","fighting outside interlopers"],
            ["Perilous research underway","hideoussly immoral research","held hostage by outsiders","scientist monsters run amok", "selling black-market tech"],
            ["ruptured rock released a peril", "foreign spy ships hide there", "Gold rush for new minerals", "Ancient ruins dot the rocks", "War between rival rocks"],
            ["Things are emerging below", "They need vital supplies", "The workers are in revolt", "Pirates secretly fuel there", "Alien remnants were found"],
            ["A ship is in severe distress", "Pirates have taken over", "has corrupt customs agents", "foreign saboteurs are active", "deep-space alien signal"]
        ]


    first = randint(0,7)
    second = randint(0,4)
    third = randint(0,4)

    return points[first], occupiers[first][second].lower(), situation[first][third].lower()

class PointOfInterest:
    def __init__(self, **kwargs):
        self._scoopable = False


class Situation(PointOfInterest):
    def __init__(self, **kwargs):
        self._classification = ""
        self._occupiers = ""
        self._situation = "" 
    @classmethod
    def generate(cls):
        new = cls()
        new._classification, new._occupiers, new._situation = make_point_of_interest()
        return new

class InterRegion(PointOfInterest):
    pass 
class InFlight(PointOfInterest):
    pass
class SystemEdge(PointOfInterest):
    pass

class GasGiant(Situation):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self._scoopable = True

    @classmethod
    def generate(cls):
        gassy = super().generate()
        gassy._classification = "Gas giant"
        gassy._scoopable = True 
        return gassy