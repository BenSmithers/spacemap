import json
import os

from traveller_utils.core.utils import Table
from traveller_utils.enums import Title

fares={
    "high":[8500,12000,20000,41000,45000,470000],
    "middle":[6200,9000,15000,31000,34000,350000],
    "basic":[2200,2900,4400,8600,9400,93000],
    "low":[700,1300,2200,4300,13000,96000],
    "freight":[1000,1600,3000,7000,7700,86000]
}

atmospheres=[
    "No",
    "Trace",
    "Very Thin, Tainted",
    "Very Thin",
    "Thin, Tainted",
    "Thin",
    "Standard",
    "Standard",
    "Dense",
    "Dense, Tainted",
    "Exotic",
    "Corrosive",
    "Insidious",
    "Very Dense",
    "Low",
    "Unusual"
]

hydrographics = [
    "is nothing but sand",
    "is a dry World",
    "has a few small seas",
    "has small seas and oceans",
    "is a wet world",
    "has large Oceans",
    "has several Large Oceans",
    "is an Earth-like world",
    "is a water-world",
    "has only a few small islands and archipelagos",
    "is almost entirely covered in water"
]

law_levels=[
    "no restrictions",
    "poison gas, explosives, undetectable weapons, WMDs",
    "portable energy and laser weapons",
    "military weapons",
    "light assault weapons and submachine guns",
    "personal concealable weapons",
    "all firearms except shotguns and stunners; carrying weapons discouraged",
    "shotguns",
    "all bladed weapons, stunners",
    "all weapons",
    "all weapons",
    "all weapons",
    "all weapons",
]

passenger_table = [
    0,1,1,2,2,2,3,3,3,3,4,4,4,5,5,6,7,8,9,10
]
assert len(passenger_table)==20

starports_str= [
    "X","X","X",
    "E","E",
    "D","D",
    "C","C",
    "B","B",
    "A"
]

starports_quality = [
    "No Starport","No Starport","No Starport",
    "Frontier", "Frontier",
    "Poor","Poor",
    "Routine", "Routine",
    "Good", "Good",
    "Excellent",
]

_fname = os.path.join(os.path.dirname(__file__),"..","resources","swon_data.json")
_obj = open(_fname, 'r')
_data = json.load(_obj)
_obj.close()


_fname = os.path.join(os.path.dirname(__file__),"..","resources","governments.json")
_obj = open(_fname, 'r')
govs = json.load(_obj)
_obj.close()

govs= govs["all"]

tech_levels=[
    "(primitive) stone age primitives",
    "(primitive) bronze or Iron Age",
    "(primitive) renaissance-era technology",
    "(primitive) primitive firearms, inklings of science and industry",
    "(industrial) industrial, plastics, radio, airplanes",
    "(industrial) widespread electricity, automobiles and telephones",
    "(industrial) early fission and rocketry. Start of the space age",
    "(pre-stellar) satellites, common computers, reliably reaching orbit",
    "(pre-stellar) possible to reach other worlds, permanent spacehabitats, fusion viable",
    "(pre-stellar) gravity manipulation, possible jump drive technology",
    "(early-stellar) common jump drives, common orbital infrastructure, intersetellar trade",
    "(early-stellar) True AI possible, grav-supported super structures, jump 2",
    "(stellar) weather control, terraforming, plasma weapons, jump 3",
    "(stellar) battle dress, convenient cloning, underwater space ships, jump 4",
    "(stellar) fusion weapons, flying cities, jump 5",
    "(high stellar) vast improvement to human life, black globe generators, jump 6",
    "(high stellar) vast improvement to human life, black globe generators, jump 6",
    "(high stellar) vast improvement to human life, black globe generators, jump 6"
]


atmo = Table()
for i in range(len(atmospheres)):
    atmo.add_entry(i, atmospheres[i])

hydro = Table()
for i in range(len(hydrographics)):
    hydro.add_entry(i, hydrographics[i])

temp = Table()
for key in _data["temperature"]:
    temp.add_entry(_data["temperature"][key]["min"], "{}".format( _data["temperature"][key]["text"]))


factions = Table()
for key in _data["factions"]:
    factions.add_entry(_data["factions"][key]["min"], "{}".format( _data["factions"][key]["text"]))


bio = Table()
for key in _data["biosphere"]:
    bio.add_entry(_data["biosphere"][key]["min"], "{} - {}".format(key, _data["biosphere"][key]["text"]))

tl = Table()
for ik, key in enumerate(tech_levels):
    tl.add_entry(ik-0.5, "TL{} - {}".format(ik, key))


wealth_tbl = Table()
wealth_tbl.add_entry(-5, Title.Lord)
wealth_tbl.add_entry(5, Title.Count)
wealth_tbl.add_entry(10, Title.Duke)
wealth_tbl.add_entry(15, Title.King)
wealth_tbl.add_entry(20, Title.Emperor)