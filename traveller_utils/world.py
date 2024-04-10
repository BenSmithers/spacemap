"""
Define the World class 
"""
from random import choice
import numpy as np
import os

from traveller_utils.tables import *
from traveller_utils.enums import WorldTag, WorldCategory, TradeGood, Contraband, Bases, Title, LandTitle
from traveller_utils.utils import roll, d100, roll1d
from traveller_utils.trade_goods import ALL_GOODS, TradeGoods
from traveller_utils.name_gen import create_name
from traveller_utils.person import Person
from traveller_utils.coordinates import HexID
from math import log10 

WorldTag._value2member_map_.keys()

star_hex = list(range(10))
star_hex+=[
    "A",
    "B",
    "C",
    "E",
    "F",
    "G",
    "H",
    "I"
]



star_hex = [str(entry) for entry in star_hex]

class Government:
    def __init__(self, dict_entry:dict, is_faction=False, score=0):
        self._gov_type = dict_entry["type"]
        self._desc = dict_entry["description"]
        self._what = choice(dict_entry["examples"])
        self._contraband = []
        for entry in dict_entry["contraband"]:
            for good in Contraband:
                if entry.lower() in good.name.lower():
                    self._contraband.append(good)
        self._raw_str = roll()
        self._strength = factions.access(self._raw_str if is_faction else 12)
        self._is_faction = is_faction
        self._score = score

        self.civil_war = False
        self._members = 0
    @property
    def score(self):
        return self._score
    
    @property
    def members(self):
        return self._members
    def set_members(self, many):
        self._members = many

    @property
    def gov_type(self):
        return self._gov_type
    @property
    def description(self):
        return self._desc
    @property
    def title(self):
        return self._what
    @property
    def contraband(self):
        return self._contraband
    
    @property
    def strength(self):
        return self._strength
    
    @property
    def raw_strength(self):
        return self._raw_str
    @property
    def is_faction(self):
        return self._is_faction
    
    @classmethod
    def unpack(cls, packed:dict):
        new = cls(packed, is_faction=packed["is_faction"], score=packed["score"])
        new._what= packed["examples"]
        new._strength = packed["strength"]
        new._members = packed["memb"]
        new.civil_war = packed["civil"]
        return new

    def pack(self)->dict:
        out = {
            "score":self._score,
            "memb":self._members,
            "type":self._gov_type,
            "description":self._desc,
            "examples":self._what,
            "contraband":[entry.name for entry in self._contraband],
            "strength":self._strength,
            "is_faction":self._is_faction,
            "civil":self.civil_war
        }
        return out

class World:
    def __init__(self, generate =True, modifier = 0):
        """
            Initialize a minimal world, generate full world if `generate`
        """
        self._name = ""
        self._fuel = False
        self._tags = []
        self._size= 0
        self._atmosphere= 0
        self._pressure = -1
        self._temperature=0
        self._trade_score = 0
        self._biosphere = 0
        self._population_raw=0
        self._population=0
        self._hydro=0
        self._tech_level=0
        self._government_raw=0
        self._government=Government(govs[0], False, self._government_raw)
        self._law_level=0
        self._factions=[]
        self._starport_raw=0
        self._liege = None
        self._liege_name = None
        self._vassals = []
        self._vassal_names = []
        self._services = []
        self._retailers = []
        self._has_gas_giant = False
        self._persistent_passengers={
            "high":[],
            "middle":[],
            "basic":[],
            "low":[],
        }
        self._generated = False
        self._passengers ={
            "high":[],
            "middle":[],
            "basic":[],
            "low":[], 
        }
        self._category =[WorldCategory.Common,]
        self._title = Title.Lord

        if generate:
            self.populate(modifier=modifier)

    @property
    def desireability(self):
        mod = 1

        if self._population_raw<=1:
            mod -= 4
        elif self._population_raw==6 or self._population_raw==7:
            mod += 1
        elif self._population_raw>8:
            mod += self._population_raw-8 + 3

        letter = self.starport_cat
        if letter=="A":
            mod +=2
        elif letter=="B":
            mod +=1
        elif letter=="E":
            mod -=1
        elif letter=="X":
            mod -=3
        if WorldCategory.red_zone in self._category:
            mod -=4
        if WorldCategory.amber_zone in self._category:
            mod -=1

        return mod

    @property
    def retailers(self):
        return self._retailers

    @property 
    def liege(self)->HexID:
        return self._liege
    @property
    def liege_world(self)->'World':
        return self._liege_name
    
    def set_liege(self, hid:HexID, which:'World'):
        self._liege = hid
        self._liege_name = which


    @property
    def wealth_str(self):
        pass
    
    @property
    def wealth(self):
        score = int(self.trade_score / 5)
        if self._population_raw>8:
            score+=3
        elif self._population_raw<3:
            score-=3
            
        if self._starport_raw>8:
            score+=3
        if self._starport_raw>10:
            score+=2

        if self._tech_level>10:
            score+=5
        if self._tech_level>14:
            score+=6

        if self._tech_level<4:
            score +=0
        if self._tech_level<8:
            score +=2

        if self._hydro > 4 and self._hydro<10:
            score += 2
        if self._atmosphere==6 or self._atmosphere==7:
            score += 2
        if "tainted" in self.atmosphere_str:
            score -=4
        
        if self._temperature>5 and self._temperature<10:
            score += 2
        if self._temperature<3 or self._temperature>12:
            score -=4 
        if self._tech_level>10:
            score +=2 
        if self._tech_level<9:
            score -=4

        score += len(self.services)

        return max([score, 0])
        

    @property 
    def trade_score(self):
        return self._trade_score
    def iterate_ts(self):
        self._trade_score = self._trade_score + 1
    def set_ts(self, value):
        self._trade_score = value

    @property
    def title(self):
        return self._title

    @property 
    def vassals(self)->'list[HexID]':
        return self._vassals
    @property
    def vassals_worlds(self)->'list[World]':
        return self._vassal_names
    
    def add_vassal(self, hid:HexID, which:'World'):
        self._vassals.append(hid)
        self._vassal_names.append(which)

    def fuel_present(self):
        """
            0 - none
            1 - gas giant
            2 - unrefined
            3 - refined
        """
        cat = self.starport_cat
        if cat=="A" or cat=="B":
            fuel = 3
        elif cat=="C" or cat=="D":
            fuel = 2
        elif self._has_gas_giant:
            fuel = 1
        elif cat=="E" or cat=="X":
            fuel = 0
        else:
            raise NotImplementedError("This should be un-reachable!")
        return fuel 


    def populate(self,name="",rng=None,
                atmosphere=-1, temperature=-1,biosphere=-1,
                population=-1, tech_level=-1,*world_tag,modifier=0, **kwargs) -> None:
        
        
        if not isinstance(world_tag,(list,tuple)):
            raise TypeError("World Tags should be type {}, not {}".format(list, type(world_tag)))

        if name=="":
            self._name=create_name("planet")
        else:
            self._name = name

        self._fuel=False
    
        if "seed" in kwargs.keys():
            np.random.seed(kwargs["seed"])

        self._tags = []

        for entry in world_tag:
            if isinstance(entry, str):
                parsed = WorldTag.__getitem__(entry)
            elif not isinstance(entry, WorldTag):
                raise TypeError("Cannot index with type {}, try an {}".format(type(entry, int)))
            else:
                parsed = entry
            self._tags.append(parsed)

        if len(world_tag)==0:
            self._tags=[ choice(list(WorldTag)) for i in range(2) ]
        
        self._size = roll(rng, mod=-2)

        self._atmosphere = roll(rng, -7+self._size) if atmosphere==-1 else atmosphere
        if self._atmosphere<0:
            self._atmosphere =0
        self._pressure = -1 

        atmo_t_mods=[
            0,0, -2,-2,-1,-1, 0,0,1,1,2,6,6,2,-1,2,2
        ]

        self._temperature = roll(rng, atmo_t_mods[self._atmosphere]) if temperature==-1 else temperature
        self._biosphere = roll(rng) if biosphere==-1 else biosphere
        self._population_raw = roll(rng, -2) if population==-1 else population
        self._population_raw += modifier    
        if self._size<2 or self._atmosphere==0:
            self._hydro = 0
        else:
            self._hydro = roll(rng) 
            if self._atmosphere < 2 or (self._atmosphere>9 and self._atmosphere < 13):
                self._hydro -= 4

            if self._temperature>=12:
                self._hydro -= 6
            elif self._temperature>=10:
                self._hydro -= 2

            self._hydro= min([10, max([self._hydro, 0])])

        if self._population_raw==0:
            self._population=0
            self._tech_level = 0
            self._government = Government(govs[0], False, 0)
            self._government_raw = 0
            self._law_level = 0
            self._factions = []

        else:
            self._population = int(round(np.random.rand(),4)*(10**self._population_raw))
            
            self._government_raw = roll(rng, -7+self._population_raw) + modifier
            if self._population_raw>3 and self._government_raw==0:
                self._government_raw = np.random.randint(1,3)
            self._government_raw = min([len(govs)-1, self._government_raw])
            self._government = Government(govs[self._government_raw], False, self._government_raw)
            self._law_level = roll(rng, -7+ self._government_raw)

            faction_mod = 0
            if self._government_raw==7:
                faction_mod = 1
            elif self._government_raw>=10:
                faction_mod = -1
            if self._government_raw<2:
                self._factions = []
            else:
                working_factions = []
                for i in range(np.random.randint(1,4)+faction_mod):
                    score = max([0, min([roll(rng, -7+self._population_raw), len(govs)-1])])
                    working_factions.append(Government(govs[score], True, score))

                total_weight = sum([entry.raw_strength for entry in working_factions]) + 12
                others = 0
                for fact in working_factions:

                    members = int((0.75 + 0.25*np.random.rand())*self._population*fact.raw_strength/total_weight)
                    fact.set_members(members)

                    if fact.raw_strength > 7 and abs(self._government.score - fact.score)>7 and fact.score>0:
                        fact.civil_war = True
                        self._government.civil_war = True
                        print("Civil war between a {} and a {}".format(
                            fact.gov_type,
                            self._government.gov_type
                        ))

                    if members>0:
                        others+=members
                        self._factions.append(fact)   
                self._government.set_members(self._population - others)

                

        star_mod = 0
        if self._population_raw>=8:
            star_mod = 1
        if self._population_raw>=10:
            star_mod=2
        if self._population_raw<=4:
            star_mod=-1
        if self._population_raw<=2:
            star_mod=-2


        self._starport_raw = roll(rng, star_mod) + modifier
        if self._starport_raw>= len(starports_str):
            self._starport_raw = len(starports_str)-1
        if self._population_raw==0:
            self._tech_level=0
        else:
            self._tech_level = np.random.randint(1,7)+ self._get_tl_mod()
            self._tech_level = min([15, self._tech_level])
        
        self._tech_level = self._tech_level if tech_level==-1 else tech_level
        
        self._category =[WorldCategory.Common,]

        self.update_category()

        self._has_gas_giant = roll() < 10

        naval_roll = roll()
        scout_roll = roll()
        research_roll = roll()
        tas_roll = roll()

        tas_lim = 14
        naval_lim = 14
        scout_lim = 14
        res_lim = 14
        if starports_str[self._starport_raw]=="A":
            tas_lim = 0
            naval_lim = 7
            scout_lim = 9
            res_lim = 7
        elif starports_str[self._starport_raw]=="B":
            tas_lim = 0
            naval_lim = 7
            scout_lim = 7
            res_lim = 9
        elif starports_str[self._starport_raw]=="C":
            tas_lim = 9
            scout_lim = 7
            res_lim = 9
        elif starports_str[self._starport_raw]=="D":
            scout_lim = 6

        if scout_roll>scout_lim:
            self._services.append(Bases.Scout)
        if naval_roll>naval_lim:
            self._services.append(Bases.Naval)
        if tas_roll>tas_lim:
            self._services.append(Bases.TAS)
        if research_roll>res_lim:
            self._services.append(Bases.Research)

    @property
    def services(self):
        return self._services

    def pack(self)->dict:
        liege_packed = "" if self._liege is None else self.liege.pack()
        packed = {
            "liege":liege_packed,
            "vassals":[ entry.pack() for entry in self._vassals ],
            "name":self._name,
            "title":self._title.value,
            "tags":[entry.name for entry in self._tags],
            "size":self._size,
            "atmo":self._atmosphere,
            "pressure":self._pressure,
            "temperature":self._temperature,
            "bio":self._biosphere,
            "raw_population":self._population_raw,
            "population":self._population,
            "hydro":self._hydro,
            "trade_score":self._trade_score,
            "tech":self._tech_level,
            "law":self._law_level,
            "government":self._government.pack(),
            "gov_raw":self._government_raw,
            "factions":[fact.pack() for fact in self._factions],
            "generated":self._generated,
            "gas_giant":self._has_gas_giant,
            "starport_raw":self._starport_raw,
            "services":[entry.name for entry in self._services],
            "persistent_pass":{
                key:[entry.pack() for entry in self._persistent_passengers[key]] for key in self._persistent_passengers.keys()
            },
            "passengers":{
                key:[entry.pack() for entry in self._passengers[key]] for key in self._passengers.keys()
            }
        }

        return packed
    
    @classmethod
    def unpack(cls, packed:dict):
        new = cls(
            generate=False
        )
        new._liege = None if packed["liege"]=="" else HexID.unpack(packed["liege"])
        new._vassals = [HexID.unpack(entry) for entry in packed["vassals"]]
        new._name=packed["name"]
        new._title=Title(packed["title"])
        new._tags=[WorldTag.__getitem__(entry) for entry in packed["tags"]]
        new._size=packed["size"]
        new._atmosphere=packed["atmo"]
        new._pressure=packed["pressure"]
        new._temperature=packed["temperature"]
        new._biosphere=packed["bio"]
        new._population_raw=packed["raw_population"]
        new._population=packed["population"]
        new._hydro=packed["hydro"]
        new._tech_level=packed["tech"]
        new._trade_score = packed["trade_score"] 
        new._law_level=packed["law"]
        new._has_gas_giant = packed["gas_giant"]
        new._government=Government.unpack(packed["government"])
        new._government_raw=packed["gov_raw"]
        new._generated=packed["generated"]
        new._services=[Bases.__getitem__(entry) for entry in packed["services"]]
        new._factions=[Government.unpack(entry) for entry in packed["factions"]]
        new._starport_raw=packed["starport_raw"]
        new._passengers={
            key:[Person.unpack(entry) for entry in packed["passengers"][key]] for key in packed["passengers"].keys()
        }
        new._persistent_passengers={
            key:[Person.unpack(entry) for entry in packed["persistent_pass"][key]] for key in packed["persistent_pass"].keys()
        }
        new.update_category()

        return new


    @property
    def generated(self):
        return self._generated
    def generate_passengers(self, steward_mod:int)->'dict[Person]':
        if self._generated:
            return self._passengers        

        for key in self._persistent_passengers:
            self._generated = True
            self._passengers[key] = []
            mod = 0
            mod += steward_mod
            if key=="high":
                mod -=4
            elif key=="low":
                mod +=1
            
            mod += self.desireability
            
            die_roll = roll(mod=mod)
            if die_roll<0:
                n_passengers = 0
            if die_roll>len(passenger_table)-1:
                n_passengers = sum(np.random.randint(1,7,10))
            else:
                n_passengers =  sum(np.random.randint(1,7,passenger_table[die_roll]))
            if len(self._persistent_passengers[key])>0:
                self._passengers[key] += self._persistent_passengers[key]
            self._passengers[key] += [Person.generate() for i in range(n_passengers - len(self._persistent_passengers[key]))]
        return self._passengers
    
    def world_profile(self, location):
        profile = str(location)+" "
        profile+=starports_str[self._starport_raw]
        profile+=star_hex[self._size]
        profile+=star_hex[self._atmosphere]
        profile+=star_hex[self._hydro]
        profile+=star_hex[self._population_raw]
        profile+=star_hex[self._government_raw]
        profile+=star_hex[min([self._law_level, len(star_hex)-1])]
        profile+=star_hex[self._tech_level]
        return profile


    def list_available_goods(self)->'set[TradeGoods]':
        """
        Returns a set of available goods. We use a set here so that each entry is unique
        """
        avail = []
        present_names = []

        for category in self._category:
            # take all the trade goods, and filter out only the ones that are available for this category 
            extra = list(filter(lambda entry: entry.is_available(category), list(ALL_GOODS.values())))

            for entry in extra:
                if entry.name not in present_names:
                    present_names.append(entry.name)
                    avail.append(entry)            
        

        return avail
    
    def sample_cargo(self, scale=6):
        """
            returns 1d<scale> units of cargo sampled from this world's parameters
        """
        available = self.list_available_goods()
        
        non_norm = [1./log10(self.get_purchase_price(entry)) for entry in available]
        total = sum(non_norm)
        weights = [entry/total for entry in non_norm]

        index = np.random.choice(range(len(weights)), p=weights)
        return available[index], scale*available[index].sample_amount()


    def get_purchase_price(self, entry:TradeGoods, modifier=0):
        """
            Returns the purchase price of the given trade good on this world 
            Returns -1 if the good is not available here 
        """

        return entry.sample_purchase_price(self.category, modifier)

        if any(entry.is_available(wc) for wc in self._category ):
            return entry.sample_purchase_price(self.category, modifier)
            #return min([entry.sample_purchase_price(wc, modifier) for wc in self.category])
        return -1 

    def get_sale_price(self, entry:TradeGoods, modifier=0):

        return entry.sample_sale_price(self._category, modifier) 

    def update_category(self):
        self._title = wealth_tbl.access(self.wealth)

        self._category = []
        if self._atmosphere==0 and self._size==0 and self._hydro==0:
            self._category.append(WorldCategory.Asteroid)

        if self._atmosphere>=4 and self._atmosphere<=9:
            if self._hydro>3 and self._hydro<9:
                if self._population_raw>4 and self._population_raw<8:
                    self._category.append(WorldCategory.Agricultural)
        
        if self._population_raw==0:
            self._category.append(WorldCategory.Barren)

        if self._hydro==2 and self._atmosphere>2:
            self._category.append(WorldCategory.Desert)
        
        if self._atmosphere>9 and self._hydro>0:
            self._category.append(WorldCategory.Fluid_Oceans)

        if self._atmosphere==5 or self._atmosphere==6 or self._atmosphere==8:
            if self._size>=6 and self._size<=8:
                    if self._hydro>4 and self._hydro<8:
                        self._category.append(WorldCategory.Garden)
        
        if self._population_raw>=9:
            self._category.append(WorldCategory.High_Pop)

        if self._tech_level>11:
            self._category.append(WorldCategory.High_Tech)

        if self._hydro>1 and self._atmosphere<2:
            self._category.append(WorldCategory.Ice_Capped)

        if self._population_raw>8:
            if self._atmosphere<3 or self._atmosphere==4 or self._atmosphere==7 or self._atmosphere==9:
                self._category.append(WorldCategory.Industrial)
        
        if self._population_raw<4:
            self._category.append(WorldCategory.Low_Pop)

        if self._tech_level<6:
            self._category.append(WorldCategory.Low_Tech)

        if self._population_raw>=6:
            if self._hydro<4:
                if self._atmosphere<4:
                    self._category.append(WorldCategory.Non_Agricultural)

            if self._government_raw>3 and self._government_raw<10:
                if self._atmosphere==6 or self._atmosphere==8:
                    if self._population_raw<9:
                        self._category.append(WorldCategory.Rich)
        else:
            self._category.append(WorldCategory.Non_Industrial)
        
        if self._hydro<4:
            if self._atmosphere<6 and self._atmosphere>1:
                self._category.append(WorldCategory.Poor)

        if self._hydro>9:
            self._category.append(WorldCategory.Water_World)
        
        if len(self._category)==0:
            self._category=[WorldCategory.Common]
    
    @property
    def gravity(self)->float:
        """
            Returns the approximate acceleration at the surface 
        """
        sizes = [
            0, 0.05,0.15,0.25,0.35,0.45,0.7,0.9,1.0,1.25,1.4
        ]
        assert len(sizes)==11
        
        return sizes[self._size]

    @property
    def pressure(self)->float:

        pressures = [
            0.00, 0.05, 
            0.1,0.3, 
            0.43, 0.65, 
            1.0, 1.0, 
            1.5, 2.5,
            -1, -1, 
            -1, 8.2, 
            0.3, -1
        ]
        self._pressure = pressures[self._atmosphere]

        if self._pressure==-1:
            self._pressure = np.random.rand()*2
            self._pressure = float(str(self._pressure)[:4])
        return self._pressure

    @property
    def category(self)->'list[WorldCategory]':
        return self._category

    @property 
    def atmosphere(self):
        return self._atmosphere

    @property
    def temperature(self):
        return self._temperature

    @property
    def biosphere(self):
        return self._biosphere
    
    @property
    def tech_level(self):
        return self._tech_level

    @property
    def tags(self):
        return self._tags
    
    @property
    def weapons_banned(self):
        if self._law_level>10:
            return law_levels[-1]
        else:
            return law_levels[self._law_level]
    def approach_check(self):
        die_roll = roll()
        if die_roll<self._law_level:
            return True
        else:
            return False

    @property
    def government(self):
        return self._government
    
    @property
    def factions(self):
        return self._factions

    @property
    def atmosphere_str(self)->str:
        what= "{} atmosphere.".format(atmo.access(self._atmosphere).lower())
        return  what[0].upper() + what[1:].lower()

    @property
    def hydro_str(self)->str:
        return "The planet " + hydro.access(self._hydro).lower()

    @property
    def temperature_str(self)->str:
        return "The planet is " + temp.access(self._temperature)
    
    @property
    def population_str(self)->str:
        return "It has a population of approximately {}".format(self._population)
    
    @property
    def tech_level_str(self)->str:
        return "{}".format(tl.access(self._tech_level))

    @property
    def biosphere_str(self)->str:
        return "The biosphere is " + bio.access(self._biosphere)

    @property
    def starport_cat(self):
        return starports_str[self._starport_raw]

    @property
    def starports_str(self)->str:
        return "{} - {}".format(starports_str[self._starport_raw], starports_quality[self._starport_raw])

    @property
    def name(self):
        return "The {} of {}".format(LandTitle(self._title.value).name, self._name)

    def description(self)->str:
        """
        Returns a string describing this world! 
        """
        x= ", ".join([self.atmosphere_str, self.temperature_str, self.population, self.tech_level_str, self.biosphere_str])+". \n\n"
        return x

    def _pretty_fmt(self, what):
        return what[0].upper() + what[1:].lower() + ". \n\n"

    def _make_nice(self, what:str):
        return what.replace("_", " ")

    def full_line(self)->str:
        output = "# The Planet {}\n\n".format(self.name)
        sentence = "\n    ".join(["Characteristics: ", self.atmosphere_str, self.temperature_str, self.population_str, self.tech_level_str, self.biosphere_str]) 
        sentence += "\n\n"
        output += sentence

        tags = "\n    ".join(["World Tags: "] + [tag.name for tag in self.tags]) 
        output += tags + "\n\n"

        cats = "\n    ".join(["World Categories: "] + [tag.name for tag in self.category]) 
        output += cats+ "\n\n"

        goods = "\n    ".join(["Available goods: "] + [self._make_nice(good.name) for good in self.list_available_goods()])
        goods += "\n\n"
        output+= goods

        return output
    
    def get_image_name(self)->str:
        if self._size<2 or self._atmosphere<2:
            return "RClassC" + str(choice(range(3)) +1)
        
        if self._temperature>12:
            return "RClassA1"
        elif self._temperature>11:
            return "RClassB1"
        elif self._temperature<3:
            return "RClassP"+str(choice([1,2]))
        
        
        if self._hydro<2:
            return "RClassH1"
        elif self._hydro<3:
            return "RClassH3"
        elif self._hydro<4:
            return "RClassH2"
        elif self._hydro<9:
            if self._temperature<5:
                return "RClassL"+str(choice([1,2]))
            return "RClassM"+str(choice(range(5))+1)
        else:
            return "RClassO" + str(choice([1,2]))


    def _get_tl_mod(self):
        mod = 0
        if self._starport_raw<3:
            mod-=4
        elif self._starport_raw==10:
            mod+=6
        elif  self._starport_raw==11:
            mod+=4
        elif self._starport_raw==12:
            mod+=2

        if self._size==0 or self._size==1:
            mod+=2
        elif self._size>1 and self._size<5:
            mod+=1

        if self._atmosphere <4 or self._atmosphere>9:
            mod+=1 
        
        if self._hydro==0:
            mod+=1
        elif self._hydro==9:
            mod+=1
        elif self._hydro==10:
            mod+=2

        if self._population_raw>0 and self._population_raw<6:
            mod +=1
        elif self._population_raw==8:
            mod +=1
        elif self._population==9:
            mod+=2
        elif self._population_raw==10:
            mod += 4

        if self._government_raw==0:
            mod +=1
        elif self._government_raw==5:
            mod +=1
        elif self._government_raw==7:
            mod +=2 
        elif self._government_raw==13 or self._government_raw==14:
            mod -=2

        return mod
        

    def notes(self):
        serv = ""

        if self.starport_cat=="A":
            fuel = "Refined"
            berth_scale = 1000
            fuel_cost = "at Cr500 per ton."
            facility = "Fully functioning capital-class shipyard. \n Repair"
        elif self.starport_cat=="B":
            fuel = "Refined"
            berth_scale = 500
            fuel_cost = "at Cr500 per ton."
            facility = "Shipyard capable of building all craft up to 5,000 tons. \n Repair"
        elif self.starport_cat=="C":
            fuel = "Unrefined"
            fuel_cost = "at Cr100 per ton."
            berth_scale = 100
            facility = "Shipyard capable of building all craft below 100 tons. \n Repair"
        elif self.starport_cat=="D":
            fuel = "Unrefined"
            berth_scale = 10
            fuel_cost = "at Cr100 per ton."
            facility = "Limited Repair. Can only fix hull damage."
        else:
            fuel = "No"
            berth_scale = 0
            facility = "No repair facilities."
            fuel_cost=0

        serv += "{} fuel available {}\n".format(fuel, fuel_cost)
        serv+=facility+"\n"
        serv+="Berthing costs Cr{}.".format(roll1d()*berth_scale)
        serv+="\n\n"
        if Bases.Naval in self.services:
            serv+="Has naval base. Ex-Naval Travellers may meet Contacts or Allies here, and mercenary Travellers can try to pick up work. "
            serv+="Naval bases also have an advanced hospital, though it is normally available only to naval personnel. "
            serv+="Travellers may also be able to purchase navy-surplus weapons here.\n\n"
        if Bases.Scout in self.services:
            serv+="The scout base here offers refined fuel and supplies to scout ships (including retired scout ships obtained by retired scouts). "
            serv+="They are also an excellent place to pickup rumors and news. "
            serv+="\n\n"
        if Bases.TAS in self.services:
            serv+="Has a Traveller's Aid Society Hostel, where Travellers with TAS memberships and their guests can stay. "
            serv+="In the Third Imperium TAS Hostels offer medical facilities for members, as well as supplies and luxuries notnormally available on most worlds. TAS Hostels are a good source of rumors and passengers. "
            serv+="\n\n"
        if Bases.Research in self.services:
            serv+="A Research base is here. It might be a weapons testing facility, or a solar observatory, or part of a secret Imperial project. "
            serv+="A research base may have Contacts or Allies of Travellers who followed a Scholar career. "
            serv+="Such bases may have advanced medical facilities. "
            serv+="\n\n"

        serv+="Wealth Score: {}\n".format(self.wealth)
        serv+="Trade Score: {}\n".format(self._trade_score)
            
        return serv