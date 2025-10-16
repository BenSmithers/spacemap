from traveller_utils.enums import WorldCategory, TradeGood, get_entry_by_name
import json, os
import numpy as np



# total supply mod scales base price like so when purchasing
purchase_scale = [ 
    300, 200, 175, 150,
    135, 125, 120, 115, 110,
    105, 100, 95, 90, 85, 80,
    75, 70, 65, 55, 50, 40, 25
]

for i in range(len(purchase_scale)):
    purchase_scale[i] = purchase_scale[i]/100.

# total demand mod effects sale price like so
sale_scale = [25,] + [45 + i*5 for i in range(16)]
sale_scale += [135,150,175,200,300,400]


for i in range(len(sale_scale)):
    sale_scale[i] = sale_scale[i]/100.

_data = open(os.path.join(os.path.dirname(__file__),"..","resources","swon_trade_good_data.json"), 'rt')
tg_data = json.load(_data)
_data.close()

supply_file = open(os.path.join(os.path.dirname(__file__),"..","resources","tg_data.json"), 'rt')
supply_data = json.load(supply_file)
supply_file.close()

class Cargo:
    def __init__(self, **cargodict):
        self._cargo = cargodict


    def validate(self, cargodict):
        pass


class TradeGoods:
    def __init__(
        self,
        name:str,
        json_entry:dict
    ):
        self.name = name
        self._demand_flexibility = float(json_entry["flex"])
        self._price = float(json_entry["price"])
        self._amount_string = json_entry["tons"]
        self._common = False
        self._availble = []
        split= self._amount_string.split("*")

        self._split0 = int(split[0])
        self._split1 = int(split[1].split("d")[0])

        if len(json_entry["available"])==1:
            if json_entry["available"][0] == "all":
                self._common = True

        self._availble = []
        for entry in supply_data["supply"].keys():
            if supply_data["supply"][entry][name]>0:
                self._availble.append( get_entry_by_name(entry, WorldCategory))
        #self._availble= [ get_entry_by_name(entry, WorldCategory) for entry in json_entry["available"] ]        

        self._demand_mod = { 
            get_entry_by_name(entry, WorldCategory): supply_data["demand"][entry][name]  for entry in supply_data["demand"].keys()
        }

        self._supply_mod = { 
            get_entry_by_name(entry, WorldCategory): supply_data["supply"][entry][name]  for entry in supply_data["supply"].keys()
        }



    @property
    def base_price(self):
        return self._price
    @property
    def supply_mod(self):
        return self._supply_mod
    @property
    def demand_mod(self):
        return self._demand_mod
    @property 
    def available(self):
        return self._availble

    @property
    def demand_flexibility(self):
        """
            A metric for flexible demand is 
             <1 inflexible (like, food)
             >1 flexible (luxury goods)
        """
        return self._demand_flexibility


    def __hash__(self) -> int:
        return self.name.__hash__()

    def extract_base_tonnage(self): 
        return self._split0*self._split1*3.5

    def sample_amount(self):
        die_roll = np.random.randint(1,7,self._split1)
        return self._split0*np.sum(die_roll)

    def is_available(self, wc:WorldCategory)->bool:
        """
        Returns whether or not this Trade Good is usually available on a planet of a given World Category 
        """
        if self._common:
            return self._common
        else:
            return wc in self._availble

    def get_mod(self, wc_list:'list[WorldCategory]')->int:
        """
        The bigger the number, the more supply there is relative to the demand 
        """
        demand = 0
        supply = 0
        for wc in wc_list:
            if wc in self._demand_mod:
                demand += self._demand_mod[wc]


            if wc in self._supply_mod:
                supply += self._supply_mod[wc]

        return supply - demand

    def sample_purchase_price(self, wc_list:'list[WorldCategory]', broker=0)->float:
        """
            Returns the expected price to purchase this good on a planet 

            Uses the "supply" and purchase
        """
        base = np.sum(np.random.randint(1,7,3)) + self.get_mod(wc_list) +broker
        if base < 0:
            scale = 4.0
        elif base < 21:
            scale = purchase_scale[int(base)]
        else:
            scale = 0.25
        return self._price*scale


    def sample_sale_price(self, wc_list:'list[WorldCategory]', broker=0)->float:
        """
            Returns the expected amount to get by selling this good on a given planet 

            Uses the "demand" and sale
        """

        base = np.sum(np.random.randint(1,7,3)) - self.get_mod(wc_list) +broker

        if base < 0:
            scale = 0.25
        elif base < 21:
            scale = sale_scale[int(base)]
        else:
            scale = 4.00
        
        return self._price*scale




# map a tradegood enum entry to a constructed TradeGoods object
ALL_GOODS = {}
for entry in tg_data:
    new_good = TradeGoods(entry, tg_data[entry])
    ALL_GOODS[new_good.name] = new_good

def get_good(good_name)->TradeGoods:
    return ALL_GOODS[good_name]

