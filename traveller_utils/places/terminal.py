from traveller_utils.places.world import World 
from traveller_utils.person import Person
from traveller_utils.core.utils import roll
from traveller_utils.tables import passenger_table
from traveller_utils.trade_goods import ALL_GOODS, TradeGoods

from math import log10
import numpy as np 

class Terminal:
    """
        A terminal is a place where you can find passengers and trade goods.
    """
    def __init__(self, linked_world:World):
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

        self._linked_world = linked_world
        self._retailers = []
    @property
    def generated(self):
        return self._generated
    def degenerate_passengers(self):
        self._generated = False

        for key in self._passengers.keys():
            for person in self._passengers[key]:
                assert isinstance(person, Person)

                if person.persistent:
                    self._persistent_passengers[key].append(person)
                    
        
        self._passengers ={
                    "high":[],
                    "middle":[],
                    "basic":[],
                    "low":[], 
                }

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
            
            mod += self._linked_world.desireability
            
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
        

    def list_available_goods(self)->'set[TradeGoods]':
        """
        Returns a set of available goods. We use a set here so that each entry is unique
        """
        avail = []
        present_names = []

        for category in self._linked_world.category:
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

        return entry.sample_purchase_price(self._linked_world.category, modifier)

        if any(entry.is_available(wc) for wc in self._category ):
            return entry.sample_purchase_price(self.category, modifier)
            #return min([entry.sample_purchase_price(wc, modifier) for wc in self.category])
        return -1 

    def get_sale_price(self, entry:TradeGoods, modifier=0):

        return entry.sample_sale_price(self._linked_world.category, modifier) 