from traveller_utils.person import Person
from traveller_utils.trade_goods import TradeGoods

class Retailer:
    """
        A person who sells things. 
    """
    def __init__(self):
        self._person = Person.generate() 

    def clear(self):
        pass

    def add_sale(self):
        pass