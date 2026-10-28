"""
Manage the random number generator to ensure consistent results when seeded in the same way. 
"""

import numpy as np 

class RNG:
    """
    This is a little bit of a wrapper around the regular numpy random number generator. 
    This is kind of used to give an equivalent interface as used in the regular `random` library
    """
    def __init__(self, seed=None):
        self._generator = np.random.default_rng(seed)


    def set_seed(self, seed):
        self._generator = np.random.default_rng(seed)

    def choice(self, list, weights=None):
        if weights is None:
            return self._generator.choice(list)
        else:
            assert len(weights)==len(list), "Illegal weights list"
            weights = weights/np.sum(weights)
            index=np.digitize(self.rand(), np.cumsum(weights))-1
            return list[index]

        
    def randint(self, low, high, number=1):
        if number==1:
            return self._generator.integers(low, high)
        else:
            return self._generator.integers(low, high, number)
    def rand(self):
        return self._generator.random()
    def randn(self, mean, dev):
        return self._generator.normal()*dev + mean
    def roll1d(self, mod=0):
        return self.randint(1,7)+mod
    def roll(self, mod=0):
        return self.randint(1,7, 2).sum() +mod 
    def d100(self):
        return self.randint(1,101)
    def shuffle(self, x):
        return self._generator.shuffle(x)

random = RNG()
