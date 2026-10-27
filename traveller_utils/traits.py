from traveller_utils.enums import Skill, Attribute, Profession
import random
import numpy as np

related_attributes={
    Profession.Administrator.name:[
        Attribute.Social.name, 
        Attribute.Education.name
    ],
    Profession.Athlete.name:[
        Attribute.Strength.name,
        Attribute.Endurance.name
    ],
    Profession.Doctor.name:[
        Attribute.Intelligence.name,
        Attribute.Education.name
    ],
    Profession.Scout.name:[
        Attribute.Dexterity.name,
        Attribute.Endurance.name
    ],
    Profession.Soldier.name:[
        Attribute.Endurance.name,
        Attribute.Dexterity.name
    ],
    Profession.Pilot.name:[
        Attribute.Dexterity.name,
        Attribute.Education.name
    ],
    Profession.Mechanic.name:[
        Attribute.Intelligence.name,
        Attribute.Dexterity.name
    ],
    Profession.Scientist.name:[
        Attribute.Intelligence.name,
        Attribute.Education.name
    ],
    Profession.Technician.name:[
        Attribute.Intelligence.name,
        Attribute.Education.name
    ],
    Profession.Merchant.name:[
        Attribute.Social.name,
        Attribute.Intelligence.name
    ],
    Profession.Diplomat.name:[
        Attribute.Social.name,
        Attribute.Education.name
    ],
    Profession.Entertainer.name:[
        Attribute.Social.name,
        Attribute.Dexterity.name
    ]
}
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

attribute_map={
    Skill.Administer.name : Attribute.Social.name,
    Skill.Connect.name : Attribute.Social.name,
    Skill.Exert.name : Attribute.Strength.name,
    Skill.Fix.name : Attribute.Intelligence.name,
    Skill.Heal.name : Attribute.Intelligence.name,
    Skill.Know.name : Attribute.Intelligence.name,
    Skill.Lead.name : Attribute.Social.name,
    Skill.Notice.name : Attribute.Intelligence.name,
    Skill.Perform.name : Attribute.Social.name,
    Skill.Pilot.name : Attribute.Dexterity.name,
    Skill.Program.name : Attribute.Intelligence.name,
    Skill.Punch.name : Attribute.Strength.name,
    Skill.Shoot.name : Attribute.Dexterity.name,
    Skill.Sneak.name : Attribute.Dexterity.name,
    Skill.Stab.name : Attribute.Strength.name,
    Skill.Survive.name : Attribute.Endurance.name,
    Skill.Talk.name : Attribute.Social.name,
    Skill.Trade.name : Attribute.Intelligence.name,
    Skill.Work.name : Attribute.Education.name,
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

def get_attributes(prof:Profession):
    """
        1. Roll attributes and sort them largest to smallest
        2. Get relevant attributes (if any)
        3. Assign highest rolled attributes to the relevant ones
        4. assign the rest in whatever order 
    """
    res = list(sorted([np.floor((np.random.randint(1,7, 3).sum()-10)/2) for attr in Attribute]))
    these_attrs = related_attributes[prof.name]

    attr_dict = {}

    for attr in these_attrs:
        score = res.pop()
        attr_dict[attr] = score 

    for attr in Attribute:
        if attr.name in attr_dict:
            continue
        else:
            score= res.pop()
            attr_dict[attr.name] = score 
    return attr_dict
    

