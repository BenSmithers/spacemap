import os 
import json

import random
import numpy as np

from traveller_utils.trade_goods import TradeGoods
from traveller_utils.core.coordinates import HexID, SubHID
from traveller_utils.enums import Skill, Attribute, WorldCategory, Profession, HairColor, HairLength, HairStyle, EyeColor, Gender
from traveller_utils.clock import Time

names_fn = os.path.join(os.path.dirname(__file__), "..","resources", "names.json")
_obj = open(names_fn,'rt')
name_data = json.load(_obj)
_obj.close()

names_fn = os.path.join(os.path.dirname(__file__),"..", "resources", "npc_data.json")
_obj = open(names_fn,'rt')
data = json.load(_obj)
_obj.close()
related_skills = {
        Profession.Administrator.name:[
            Skill.Administer.name,
            Skill.Connect.name,
            Skill.Lead.name,
            Skill.Notice.name,
            Skill.Talk.name,  ],
        Profession.Athlete.name:[
            Skill.Exert.name,
            Skill.Punch.name,
            Skill.Shoot.name,
            Skill.Sneak.name,
            Skill.Notice.name ],
        Profession.Doctor.name:[
            Skill.Heal.name,
            Skill.Know.name,
            Skill.Notice.name,
            Skill.Stab.name,
            Skill.Work.name],
        Profession.Scout.name:[
            Skill.Sneak.name,
            Skill.Exert.name,
            Skill.Notice.name,
            Skill.Shoot.name,
            Skill.Survive.name ],
        Profession.Soldier.name:[
            Skill.Shoot.name,
            Skill.Exert.name,
            Skill.Punch.name,
            Skill.Stab.name,
            Skill.Stab.name ],
        Profession.Pilot.name:[
            Skill.Pilot.name,
            Skill.Connect.name,
            Skill.Lead.name,
            Skill.Notice.name,
            Skill.Trade.name ],
        Profession.Mechanic.name:[
            Skill.Fix.name,
            Skill.Notice.name,
            Skill.Punch.name,
            Skill.Work.name,
            Skill.Connect.name ],
        Profession.Scientist.name:[
            Skill.Know.name,
            Skill.Notice.name,
            Skill.Program.name,
            Skill.Work.name,
            Skill.Fix.name],
        Profession.Technician.name:[
            Skill.Program.name,
            Skill.Fix.name,
            Skill.Know.name,
            Skill.Notice.name,
            Skill.Work.name ], 
        Profession.Merchant.name:[
            Skill.Trade.name,
            Skill.Connect.name,
            Skill.Lead.name,
            Skill.Talk.name,
            Skill.Work.name ],
        Profession.Diplomat.name:[
            Skill.Talk.name,
            Skill.Administer.name,
            Skill.Connect.name,
            Skill.Lead.name,
            Skill.Notice.name],
        Profession.Entertainer.name:[
            Skill.Perform.name,
            Skill.Lead.name,
            Skill.Talk.name,
            Skill.Notice.name,
            Skill.Connect.name ]

}
def get_skills(prof:Profession, grade=0):
    """
        Get +2+grade in Primary 
        
        Get +1 in 5 related skills

        For each grade above 0, 
            get another +1 in another two related skills  

        Get another +1 in three+grade random skills

    """
    skill_dict = {attr.name:-1 for attr in Skill}
    these_skills = related_skills[prof.name]

    skill_dict[these_skills[0]] = 2 + grade

    for sk in these_skills[1:]:
        skill_dict[sk] =1

    
    for extra in range(grade):
        choices = [sk for sk in these_skills if skill_dict[sk]<2+grade]
        if len(choices)>0:
            pick = random.choice(choices)
            skill_dict[pick] +=1

    for _ in range(3+grade):
        choices = [sk.name for sk in Skill if skill_dict[sk.name]<2+grade]
        if len(choices)>0:
            pick = random.choice(choices)
            skill_dict[pick] +=1

    return skill_dict


def get_keys():
    return name_data.keys()


def get_name(key, gender:str):
    if key=="Combined":
        fn_key = random.choice(list(name_data.keys()))
        ln_key = random.choice(list(name_data.keys()))
        if gender=="Non_Binary":
            fn = random.choice( name_data[fn_key]["male"] + name_data[fn_key]["female"] )  
        else:
            fn = random.choice( name_data[fn_key][gender.lower()] )  

        ln = random.choice( name_data[ln_key]["surnames"] )
        return fn + " " + ln
    elif key == "Random":
        usekey = random.choice(list(name_data.keys()))
    else:
        usekey = key

    
    if gender=="Non_Binary":
        fn = random.choice( name_data[usekey]["male"] + name_data[usekey]["female"] )  
    else:
        fn = random.choice( name_data[usekey][gender.lower()] )
    ln = random.choice( name_data[usekey]["surnames"] )

    return fn + " " +ln

class Person:
    def __init__(self):
        self._name = ""

        self._birthday = Time()
        self._gender = 0 # 0-male, 1-female, 2-nb
        self._hair_color = HairColor.Brown
        self._eye_color = EyeColor.Brown
        self._hair_length = HairLength.Bald
        self._hair_style = HairStyle.Straight


        self._wants = []

        self._destination = None
        self._persistent = False

        self._image_name = ""

        self._skills = {
            attr.name:-1 for attr in Skill
        }
        self._attrs = {
            attr.name:0 for attr in Attribute
        }

        self._profression = Profession.Administrator

    def pack(self):
        """ Convert to dictionary for saving """
        data = {
            "name":self._name,
            "birthday":self._birthday.pack(),
            "gender":self._gender.name,
            "hair_color":self._hair_color.name,
            "eye_color":self._eye_color.name,
            "hair_length":self._hair_length.name,
            "hair_style":self._hair_style.name,
            "wants":[wg.name for wg in self._wants], 
            "destination":self._destination.pack() if self._destination is not None else None,
            "persistent":self._persistent,
            "image_name":self._image_name,
            "skills":self._skills,
            "attrs":self._attrs,
            "profession":self._profression.name
        }
        return data
    @classmethod
    def unpack(cls, data):
        """ Create from saved dictionary """
        newp = cls()
        newp._name = data["name"]
        newp._birthday = Time.unpack(data["birthday"])
        newp._gender = Gender[data["gender"]]
        newp._hair_color = HairColor[data["hair_color"]]
        newp._eye_color = EyeColor[data["eye_color"]]       
        newp._hair_length = HairLength[data["hair_length"]]
        newp._hair_style = HairStyle[data["hair_style"]]
        newp._wants = [TradeGoods[wg] for wg in data["wants"]]
        newp._destination = SubHID.unpack(data["destination"]) if data["destination"] is not None else None
        newp._persistent = data["persistent"]
        newp._image_name = data["image_name"]
        newp._skills = data["skills"]
        newp._attrs = data["attrs"]
        newp._profression = Profession[data["profession"]]
        return newp

    @property
    def name(self):
        return self._name
    
    @property
    def pronouns(self):
        if self._gender==0:
            return "he/him",
        elif self._gender==1:
            return "she/her"
        else:
            return "they/them"

    @property
    def profession(self):
        return self._profression
    

    @property
    def birthday(self):
        return self._birthday
    

    def age(self, today:Time):
        print("today is {}; birthday is {}".format(type(today), type(self._birthday)))
        tdiff = today - self._birthday
        return tdiff.year
    @property
    def attributes(self):
        return self._attrs
    @property
    def skills(self):
        return self._skills
    @property
    def hair_color(self):
        return self._hair_color
    @property
    def hair_style(self):
        return self._hair_style
    @property
    def eye_color(self):
        return self._eye_color
    @property
    def hair_length(self):
        return self._hair_length

    @property
    def destination(self)->SubHID:
        return self._destination
    def set_destination(self, dest:SubHID):
        self._destination = dest


    @property
    def persistent(self):
        return self._persistent

    def make_persistent(self):
        self._persistent = True

    @property
    def wants(self)->'list[TradeGoods]':
        return self._wants
    def add_want(self, want:TradeGoods):
        self._wants.append(want)
    def clear_wants(self):
        self._wants = []

    @property
    def image_name(self):
        return self._image_name

    @classmethod
    def generate(cls, key="Random", today=Time(year=2500), grade=0, profession:Profession=Profession.Not_Specified,*worldcategories:WorldCategory):
        newp = cls()

        """
        Wants should depend on things not available on home world world categories
        """

        if profession.name == Profession.Not_Specified.name:
            profession = random.choice( list(Profession)[1:] )

        newp._profression = profession
        newp._skills = get_skills(profession, grade)

        gender_roll = random.randint(1, 100)
        if gender_roll<=48:
            newp._gender = Gender.Male
        elif gender_roll<=96:
            newp._gender = Gender.Female
        else:
            newp._gender = Gender.Non_Binary
        newp._name = get_name(key, newp._gender.name)

        for attr in newp._attrs.keys():
            newp._attrs[attr] = np.floor((np.random.randint(1,7, 3).sum()-10)/2)


        # they should be between 20 and 120 years old
        newp._birthday = today - Time(minute=np.random.randint(20*365*24*60,120*365*24*60))
        
        
       
        if newp._gender.name == "Male":
            newp._image_name = "Male_{:02d}".format(np.random.randint(1,19))
        else:
            newp._image_name = "Female_{:02d}".format(np.random.randint(1,13))

        return newp
