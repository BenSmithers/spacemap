from traveller_utils.person import Person
from traveller_utils.trade_goods import TradeGoods, ALL_GOODS

from traveller_utils.world import World

from random import choice
from random import randint
from traveller_utils.utils import roll1d

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

    @property
    def purchase_prices(self):
        return self._purchase_prices
    @property
    def sale_prices(self):
        return self._sale_prices

    def pack(self)->dict:
        return {
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

    @property
    def person(self)->Person:
        return self._person
    

    @property
    def name(self):
        return self._name
    

    def _clear(self):
        self._purchase_prices = {}
        self._sale_prices = {}

    def regenerate(self, home:World, modifier=0):
        """
            Regenerate sale/purchase prices using the `home` as the base to determine prices and availability 
            
        """
        self._clear()
        all_goods = home.list_available_goods()

        for good in all_goods:
            number = good.sample_amount()
            self._sale_prices[good] = {
                "amount":number,
                "price":home.get_purchase_price(good, modifier)
            }

        # choose 1d6 more randomly 
        quant = roll1d()
        for i in range(quant):
            good = ALL_GOODS[choice(list(ALL_GOODS.keys()))]
            number = good.sample_amount()
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
                