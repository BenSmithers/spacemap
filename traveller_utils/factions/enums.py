from enum import Enum

class AssetTheme(Enum):
    cunning = 1
    force = 2
    wealth = 4

class FactionTag(Enum):
    Colonists = 1 
    DeepRooted = 2 
    EugenicsCult = 3
    ExchangeConsulate = 4
    Fanatical = 5 
    Imperialists = 6
    Machiavellian = 7
    MercenaryGroup = 8
    PerimeterAgency = 9
    Pirates = 10
    PlanetaryGov = 11
    Plutocratic=12

def asset_appeal_modifier(theme:AssetTheme, tag:FactionTag):
    if theme.value == AssetTheme.cunning.value:
        modifiers = [
            1.0, 
            1.2, 
            0.8,
            1.5,
            0.8, 
            0.8,
            1.5,
            0.5,
            1.5, 
            0.5, 
            1.0,
            1.2
        ]
        assert len(modifiers)==12
        return modifiers[tag.value-1]
    elif theme.value == AssetTheme.force.value:
        modifiers = [
            1.0,
            0.8,
            1.5,
            0.5,
            1.5,
            1.5,
            0.5,
            1.2,
            0.8,
            1.5,
            0.5,
            0.5
        ] 
        assert len(modifiers)==12
        return modifiers[tag.value-1]
    else:
        modifiers = [
            0.8,
            1.5,
            0.5,
            1.5,
            0.8,
            1.2,
            1.5,
            1.0,
            1.2,
            0.8,
            1.2,
            1.5
        ] 
        assert len(modifiers)==12
        return modifiers[tag.value-1]
    
class AssetType(Enum):
    SpecialForces=1
    MilitaryUnit=2
    Facility=4
    Starship=8
    Special=16
    LogisticsFacility=32
    Tactic=64 
    Stealth=128
    
