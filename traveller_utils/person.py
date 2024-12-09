import os 
import json

import random
import numpy as np

from traveller_utils.trade_goods import TradeGoods
from traveller_utils.core.coordinates import HexID
from traveller_utils.enums import Skill, Attribute, WorldCategory

names_fn = os.path.join(os.path.dirname(__file__), "..","resources", "names.json")
_obj = open(names_fn,'rt')
name_data = json.load(_obj)
_obj.close()

names_fn = os.path.join(os.path.dirname(__file__),"..", "resources", "npc_data.json")
_obj = open(names_fn,'rt')
data = json.load(_obj)
_obj.close()

def get_keys():
    return name_data.keys()


def get_name(key, gender=False):
    if key=="Combined":
        fn_key = random.choice(list(name_data.keys()))
        ln_key = random.choice(list(name_data.keys()))

        fn = random.choice( name_data[fn_key][gender] )
        ln = random.choice( name_data[ln_key]["surnames"] )
        return fn + " " + ln
    elif key == "Random":
        usekey = random.choice(list(name_data.keys()))
    else:
        usekey = key

    fn = random.choice( name_data[usekey][gender] )
    ln = random.choice( name_data[usekey]["surnames"] )

    return fn + " " +ln

class Person:
    def __init__(self):
        self._name = ""
        self._sex = ""
        self._appearance = ""
        self._description = ""
        self._quirks = ""
        self._problems = ""
        self._motivations = ""
        self._pronouns = ""

        self._wants = ""

        self._destination = None
        self._persistent = False

        self._image_name = ""

        self._skills = {
            attr.name:-1 for attr in Skill
        }
        self._attrs = {
            attr.name:0 for attr in Attribute
        }

    @property
    def destination(self):
        return self._destination
    def set_destination(self, dest):
        self._destination = dest

    @classmethod
    def unpack(cls, packed:dict):
        new = cls()
        new._name = packed["name"]
        new._sex = packed["sex"]
        new._appearance = packed["appear"]
        new._description = packed["description"]
        new._quirks = packed["quirks"]
        new._problems = packed["problems"]
        new._motivations = packed["motivations"]
        new._pronouns = packed["pronoun"]
        new._wants = packed["wants"]
        new._persistent = packed["persistent"]
        new._image_name = packed["image"]
        new._destination = HexID.unpack(packed["dest"]) if packed["dest"]!="" else None
        return new
    
    def pack(self)->dict:
        packed ={
            "name":self._name,
            "sex":self._sex,
            "appear":self._appearance,
            "description":self._description,
            "quirks":self._quirks,
            "problems":self._problems,
            "motivations":self._motivations,
            "pronoun":self._pronouns,
            "wants":self._wants,
            "persistent":self._persistent,
            "image":self._image_name,
            "dest":self._destination.pack() if self._destination is not None else ""
        }
        return packed

    @property
    def persistent(self):
        return self._persistent

    def make_persistent(self):
        self._persistent = True

    @property
    def wants(self)->'list[TradeGoods]':
        return self._wants

    @property
    def pronouns(self):
        return self._pronouns
    @property
    def name(self):
        return self._name
    @property
    def appearance(self):
        return self._appearance.replace("\n","")
    @property
    def description(self):
        return self._description.replace("\n","")
    @property
    def quirks(self):
        return self._quirks.replace("\n","")
    @property
    def problems(self):
        return self._problems.replace("\n","")
    @property
    def motivations(self):
        return self._motivations.replace("\n","")
    @property
    def image_name(self):
        return self._image_name

    @classmethod
    def generate(cls, key="Random", *worldcat):
        newp = cls()
        newp._sex =  "male" if random.randint(0,1) else "female"

        pronoun = "he" if newp._sex=="male" else "she"
        slash = "his" if newp._sex=="male" else "her"
        newp._pronouns = "{}/{}".format(pronoun,slash)
        formatted_pn = pronoun[0].upper() + pronoun[1:]

        newp._name = get_name(key, newp._sex)
        short_name = newp._name.split(" ")[0]
        newp._appearance=newp._name + " is {} and {}. ".format(random.choice(data["heights"]).lower(), random.choice(data["ages"]).lower())

        bald = False
        if "old" in newp._appearance.lower() or "middle" in newp._appearance.lower():
            if newp._sex=="male":
                if random.randint(1,3)==1:
                    bald = True
            else:
                if random.randint(1,20)==1:
                    bald = True
        if bald:
            hair = "{} is bald. ".format(short_name)
        else:
            hair = "{} has {} {} hair. ".format(
                short_name,
                random.choice(data["hair"]),
                random.choice(data["hair_color"])
            )

        newp._appearance = newp._appearance + hair
            
        desc = formatted_pn + " was formally a {}.\n\n".format(random.choice(data["role"]).lower())
        desc += formatted_pn + " is {} and known for {} {}.\n\n".format(
            random.choice(data["background"]).lower(),
            slash, 
            random.choice(data["traits"]).lower()
        )

        newp._description = desc
        newp._quirks= pronoun[0].upper() + pronoun[1:] + " {}. \n\n".format(random.choice(data["quirks"]).lower())
        newp._problems = pronoun[0].upper() + pronoun[1:].lower() + " has " + random.choice(data["problems"]).lower()
        newp._motivations =  pronoun[0].upper() + pronoun[1:] + " {}. \n\n".format(random.choice(data["motivations"]).lower())
        newp._wants =  formatted_pn + " wants {}.\n\n".format(random.choice(data["desires"]).lower())

        if newp._sex == "male":
            newp._image_name = "Male_{:02d}".format(np.random.randint(1,19))
        else:
            newp._image_name = "Female_{:02d}".format(np.random.randint(1,13))

        return newp
