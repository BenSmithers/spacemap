from traveller_utils.person import Person
from traveller_utils.trade_goods import TradeGoods, ALL_GOODS

from traveller_utils.places.world import World

from random import choice
from random import randint
from traveller_utils.core.utils import roll1d

prefixes = [
    "Dr ",
    "Professor ",
    "The Esteemed ",
]
suffixes = [
    " Industries",
    " Incorporated",
    " Limited",
    " Unlimited",
]

class Retailer:
    """
        A person who sells things. 
    """
    def __init__(self):
        self._person = Person.generate() 

        self._name = self._person.name
        if randint(1,4)==1:
            self._name = self._name.split(" ")[-1]
            self._name += " & " + Person.generate().name.split(" ")[-1]

        if randint(1,4)==1:
            self._name = choice(prefixes) + self._name
        if randint(1,4) ==1:
            self._name = self._name + choice(suffixes)

        self._purchase_prices = {}
        self._sale_prices = {}

        self._generated = False

    @property
    def generated(self):
        return self._generated
    @property
    def purchase_prices(self):
        return self._purchase_prices
    @property
    def sale_prices(self):
        return self._sale_prices

    def pack(self)->dict:
        return {
            "generated":self._generated,
            "person":self._person.pack(),
            "name":self._name,
            "purchase":{good.name:self._purchase_prices[good] for good in self._purchase_prices.keys()},
            "sale":{good.name:self._sale_prices[good] for good in self._sale_prices.keys()},
        }
    @classmethod
    def unpack(cls, packed:dict):
        
        newp = Retailer()
        newp._person = Person.unpack(packed["person"])
        newp._name = packed["name"]
        if "generated" in packed:
            newp._generated = packed["generated"]

        return newp

    @property
    def person(self)->Person:
        return self._person
    

    @property
    def name(self):
        return self._name
    

    def clear(self):
        self._generated = False
        self._purchase_prices = {}
        self._sale_prices = {}

    def regenerate(self, home:World, modifier=0):
        """
            Regenerate sale/purchase prices using the `home` as the base to determine prices and availability 
            
        """
        self.clear()
        self._generated = True
        all_goods = home.list_available_goods()

        scaling=  4**(home.title.value -2)


        for good in all_goods:
            number = int(good.sample_amount()*scaling)
            if number<1:
                continue
            self._sale_prices[good] = {
                "amount":number,
                "price":home.get_purchase_price(good, modifier)
            }

        # choose 1d6 more randomly 
        quant = roll1d()
        for i in range(quant):
            good = ALL_GOODS[choice(list(ALL_GOODS.keys()))]
            number = int(good.sample_amount()*scaling)
            if number<1:
                continue
            if good not in self._sale_prices:
                self._sale_prices[good] = {
                    "amount":number,
                    "price":home.get_purchase_price(good, modifier)
                }
            else:
                self._sale_prices[good]["amount"] += number


        for good in ALL_GOODS.keys():
            good = ALL_GOODS[good]
            self._purchase_prices[good]={
                "price":home.get_sale_price(good, modifier)
            }

            if good in self._sale_prices and (self._purchase_prices[good]["price"]>self._sale_prices[good]["price"]):
                self._purchase_prices[good]["price"] = self._sale_prices[good]["price"]*0.6
                