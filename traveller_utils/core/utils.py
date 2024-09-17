"""
Define some utilities used by the generators

 - perlin noise generator
"""
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor
from PyQt5 import QtGui


from math import exp, sqrt
import numpy as np
import numpy.random as rnd

from glob import glob
import os

from scipy.interpolate import interp2d
from traveller_utils.core.coordinates import DRAWSIZE

 
def all_subclasses(cls, get_names = False):
    """
        Returns either a list of the names of all subclasses of `cls`, or a list of the classes themselves
    """
    if get_names:
        return list(set(cls.__name__ for cls in cls.__subclasses__()).union(
            [s.__name__ for c in cls.__subclasses__() for s in all_subclasses(c)]))
    else:
        return list(set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in all_subclasses(c)]))

def number_add_comma(number):
    number = str(int(number))[::-1]

    str_thing = ""
    for i, val in enumerate(number):
        
        if i%3==0 and i!=0:
            if i!=len(number):
                str_thing+=","
        str_thing+=val
    return str_thing[::-1]



class IconLib:
    """
        A library for pre-loading all the icons we'll be using. This is used by the clicker tool for drawing the entities 

        Modules can provide a folder of icons which can overwrite (and add to) the default set of icons
    """
    def __init__(self, folder = "", ext="png"):
        self._pictures = glob(os.path.join(folder,"*."+ext))
        self._module_folder = ""
        
        self.reload()

    def set_module(self, module_folder):
        if not os.path.exists(module_folder):
            raise IOError("Module folder does not exist: {}".format(module_folder))
        self._module_folder = module_folder
        self.reload()

    def reload(self):
        self._pixmaps = {}        
        for each in self._pictures:
            name = os.path.split(each)[1].split(".")[0]

            self._pixmaps[name] = QtGui.QPixmap(each)

        if self._module_folder!="":
            module_overwrite = glob(os.path.join(self._module_folder, "*"))
            for each in module_overwrite:
                name = os.path.split(each)[1].split(".")[0]
                print("added {}".format(name))
                self._pixmaps[name] = QtGui.QPixmap(each)

    def all_names(self):
        return list(self._pixmaps.keys())

    def __iter__(self):
        return self._pixmaps.__iter__()

    def access(self, name:str, width=-1)->QtGui.QPixmap:
        if name not in self._pixmaps:
            raise ValueError("Requested {} pixmap, don't see it! Have {}".format(name, self._pixmaps.keys()))

        if width==-1:
            return self._pixmaps[name].scaledToWidth(DRAWSIZE)
        else:
            return self._pixmaps[name].scaledToWidth(int(width))

def roll1d(rng=None, mod=0):
    if rng is None:
        return np.random.randint(1,7) + mod
    else:
        return rng.randint(1,7) + mod 

def roll( mod=0):
    return np.random.randint(1,7)+np.random.randint(1,7)+mod



def d100(rng=None):
    if rng is None:
        return np.random.randint(1,101)
    else:
        return rng.randint(1,101)

class Table:
    """
    This class is used for the rollable tables where we have something like 
        2d6     Type
         2      One
         3      another
        4-7     a third

    and if we give it, say, 5, we want "a third"

    So here, you make the Table, and enter in values (one at a time) for each entry in the table. Then it can be accessed 
    """
    def __init__(self):
        self._mins = []
        self._entry = []


    def add_entry(self, min:int, entry:str):
        self._mins.append(int(min))
        self._entry.append(entry)
    def access(self, value:int)->str:
        if value>max(self._mins):
            return self._entry[-1]
        elif value<min(self._mins):
            return self._entry[0]
        else:
            what = get_loc(value, self._mins)[0]
            return self._entry[what]

def get_loc(x:float, domain:list,closest=False):
    """
    Returns the indices of the entries in domain that border 'x' 
    Raises exception if x is outside the range of domain 
    Assumes 'domain' is sorted!! And this _only_ works if the domain is length 2 or above 
    This is made for finding bin numbers on a list of bin edges 
    """

    if len(domain)<=1:
        raise ValueError("get_loc function only works on domains of length>1. This is length {}".format(len(domain)))

    if x>domain[-1]:
        return [len(domain)-1, len(domain)]
    elif x<domain[0]:
        return [0,1]

    # I think this is a binary search
    min_abs = 0
    max_abs = len(domain)-1

    lower_bin = int(abs(max_abs-min_abs)/2)
    upper_bin = lower_bin+1

    while not (domain[lower_bin]<=x and domain[upper_bin]>=x):
        if abs(max_abs-min_abs)<=1:
            print("{} in {}".format(x, domain))
            raise Exception("Uh Oh")

        if x<domain[lower_bin]:
            max_abs = lower_bin
        if x>domain[upper_bin]:
            min_abs = upper_bin

        # now choose a new middle point for the upper and lower things
        lower_bin = min_abs + int(abs(max_abs-min_abs)/2)
        upper_bin = lower_bin + 1
    
    assert(x>=domain[lower_bin] and x<=domain[upper_bin])
    if closest:
        return( lower_bin if abs(domain[lower_bin]-x)<abs(domain[upper_bin]-x) else upper_bin )
    else:
        return(lower_bin, upper_bin)

def bilinear_interp(p0, p1, p2, q11, q12, q21, q22):
    """
    Performs a bilinear interpolation on a 2D surface
    Four values are provided (the qs) relating to the values at the vertices of a square in the (x,y) domain
        p0  - point at which we want a value (len-2 tuple)
        p1  - coordinates bottom-left corner (1,1) of the square in the (x,y) domain (len-2 tuple)
        p2  - upper-right corner (2,2) of the square in the (X,y) domain (len-2 tuple)
        qs  - values at the vertices of the square (See diagram), any value supporting +/-/*
                    right now: floats, ints, np.ndarrays 
        (1,2)----(2,2)
          |        |
          |        |
        (1,1)----(2,1)
    """

    
    # check this out for the math
    # https://en.wikipedia.org/wiki/Bilinear_interpolation

    x0 = p0[0]
    x1 = p1[0]
    x2 = p2[0]
    y0 = p0[1]
    y1 = p1[1]
    y2 = p2[1]

    if not (x0>=x1 and x0<=x2):
        raise ValueError("You're doing it wrong. x0 should be between {} and {}, got {}".format(x1,x2,x0))
    if not (y0>=y1 and y0<=y2):
        raise ValueError("You're doing it wrong. y0 should be between {} and {}, got {}".format(y1,y2,y0))

    # this is some matrix multiplication. See the above link for details
    # it's not magic, it's math. Mathemagic 
    mat_mult_1 = [q11*(y2-y0) + q12*(y0-y1) , q21*(y2-y0) + q22*(y0-y1)]
    mat_mult_final = (x2-x0)*mat_mult_1[0] + (x0-x1)*mat_mult_1[1]

    return( mat_mult_final/((x2-x1)*(y2-y1)) )

def perlin(granularity,octave=5)->np.ndarray:
    """
    returns a mesh of perlin noise given a seed and granularity 
    
    returns numpy array with values ranging between -0.5 and 0.5
    """

    lin = np.linspace(0,octave,200,endpoint=False)
    x,y = np.meshgrid(lin, lin)

    # permutation table
    p = np.arange(256,dtype=int)
    np.random.shuffle(p)
    p = np.stack([p,p]).flatten()
    # coordinates of the top-left
    xi = x.astype(int)
    yi = y.astype(int)
    # internal coordinates
    xf = x - xi
    yf = y - yi
    # _fade factors
    u = _fade(xf)
    v = _fade(yf)
    # noise components
    n00 = _gradient(p[p[xi]+yi],xf,yf)
    n01 = _gradient(p[p[xi]+yi+1],xf,yf-1)
    n11 = _gradient(p[p[xi+1]+yi+1],xf-1,yf-1)
    n10 = _gradient(p[p[xi+1]+yi],xf-1,yf)
    # combine noises
    x1 = _lerp(n00,n10,u)
    x2 = _lerp(n01,n11,u) # FIX1: I was using n10 instead of n01

    values = np.zeros(shape=(granularity, granularity))
    xs = np.array(range(200))*granularity/200
    evals = interp2d(xs,xs,_lerp(x1,x2,v))
    values = evals(range(granularity),range(granularity))

    return values # FIX2: I also had to reverse x1 and x2 here

def _lerp(a,b,x):
    "linear interpolation"
    return a + x * (b-a)

def _fade(t):
    "6t^5 - 15t^4 + 10t^3"
    return 6 * t**5 - 15 * t**4 + 10 * t**3

def _gradient(h,x,y):
    "grad converts h to the right _gradient vector and return the dot product with (x,y)"
    vectors = np.array([[0,1],[0,-1],[1,0],[-1,0]])
    g = vectors[h%4]
    return g[:,:,0] * x + g[:,:,1] * y

def gauss(mean, dev):
    return (rnd.randn()*dev + mean)

def point_is_in(point:QPointF, dimensions):
    """
    Returns whether or not a Point is within the bounds of a map of given dimensions.

    @param Point    - a Point object
    @param dimensions - list-like 
    """

    return( point.x() < dimensions[0] and point.x() > 0 and point.y() < dimensions[1] and point.y()>0)



def angle_difference( theta_1, theta_2 ):
    """
    Returns the absolute difference between two angles

    @param theta_1 - first angle [degrees]
    @param theta_2 - second angle [degrees]
    """
    if not isinstance( theta_1, float):
        raise TypeError("theta_1 not {}, it's {}".format(float, type(theta_1)))
    if not isinstance( theta_2, float):
        raise TypeError("theta_2 not {}, it's {}".format(float, type(theta_2)))

    if not (theta_1 >= 0 and theta_1<=360):
        raise Exception("bad angle {}".format(theta_1))
    if not (theta_2 >= 0 and theta_2<=360):
        raise Exception("bad angle {}".format(theta_2))
    
    return(min([(360.) - abs(theta_1-theta_2), abs(theta_1-theta_2)]) )

def get_distribution( direction, variance=20. ):
    """
    Creates a normalized, discrete, gaussian distribution centered at a given angle and with a given variance. Distribution applies to the six angles correlated with the directions to a Hexes' neighbors' centers. 

    @param direction - mean of distribution
    @param variance -  variance of distribution
    """
    normalization = 0
#    variance = 20.
    angles = [150., 90., 30., 330., 270., 210.]

    # We do this to calculate the overall normalization
    for angle in angles:
        normalization += exp( -1.*(angle_difference(angle, direction)**2)/(2*variance**2))

    # Then prepare a function returning normalized probabilities 
    def distribution(angle): 
        return( (1./normalization)*exp(-1*(angle_difference(angle, direction)**2)/(2*variance**2)))

    return( distribution )