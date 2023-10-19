from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QColor
from math import sqrt,sin,cos
from PyQt5.QtWidgets import QGraphicsItem

from traveller_utils.coordinates import HexID, hex_to_screen, DRAWSIZE

import numpy as np
from numpy.random import randint

RTHREE = sqrt(3)

class Hex(QPolygonF):
    def __init__(self, center:QPointF):
        """
        Construct like a polygon, must pass a list of QPointF objects 
        """
        points = [
            QPointF(center.x()+DRAWSIZE, center.y()),
            QPointF(center.x()+DRAWSIZE*0.5, center.y()+DRAWSIZE*0.5*RTHREE),
            QPointF(center.x()-DRAWSIZE*0.5, center.y()+DRAWSIZE*0.5*RTHREE),
            QPointF(center.x()-DRAWSIZE, center.y()),
            QPointF(center.x()-DRAWSIZE*0.5, center.y()-DRAWSIZE*0.5*RTHREE),
            QPointF(center.x()+DRAWSIZE*0.5, center.y()-DRAWSIZE*0.5*RTHREE)
        ]
        super().__init__(points)

        # store relevant hex parameters. These will be set by the brushes, adjusters, generators, etc. 
        # used to store any special parameters 
        self._params = {}
        self._fill = QColor(255,255,255)
        self.x = center.x()
        self.y = center.y()
        self.genkey = '0000'
        self.geography = ""
        self.is_land = False
        self.wind = np.zeros(2)

    @property 
    def center(self):
        return QPointF(self.x, self.y)

    @property
    def params(self):
        return self._params
    @property
    def fill(self)->QColor:
        return self._fill

    def set_fill(self, fill:QColor):
        self._fill = fill
    def set_params(self, params:dict):
        self._params = params
    def set_param(self, param:str, value:float):
        self._params[param] = value
    
    def get_cost(self, other:'Hex', ignore_water=False):
        """
        Gets the cost of movement between two hexes. Used for routing
        """
        # xor operator
        # both should be land OR both should be water
        if (self.is_land ^ other.is_land) and not ignore_water:
            water_scale = 5.
        else:
            water_scale = 1.


        # prefer flat ground!
        lateral_dist=(self.center - other.center)
        lateral_dist = lateral_dist.x()*lateral_dist.x() + lateral_dist.y()*lateral_dist.y()

        mtn_scale =1.0
        if other.geography=="peak" or other.geography=="ridge":
            mtn_scale=100.0
        elif other.geography=="mountain":
            mtn_scale=50.0
        

        alt_dif = abs(10*(other.params["altitude_base"] - self.params["altitude_base"])) 
        if (not self.is_land) or (not other.is_land):
            alt_dif = 0.0

        return(mtn_scale*water_scale*(0.1*lateral_dist + DRAWSIZE*RTHREE*alt_dif))

    def get_heuristic(self, other:'Hex'):
        """
        Estimates the total cost of going from this hex to the other one
        """
        lateral_dist = (self.center - other.center)
        lateral_dist= lateral_dist.x()*lateral_dist.x() + lateral_dist.y()*lateral_dist.y()
        alt_dif = abs(2*(other.params["altitude_base"] - self.params["altitude_base"]))
        return(0.1*lateral_dist + DRAWSIZE*RTHREE*alt_dif)

    def pack(self)->dict:
        """
        Takes the hex object and save the essentials such that this can be reconstructed later. 
        """
        vals = {
            "red":self.fill.red(),
            "green":self.fill.green(),
            "blue":self.fill.blue(),
            "params":self.params,
            "x":self.x,
            "Y":self.y,
            "geo":self.geography,
            "wind":list(self.wind)
        }
        return vals
    @classmethod
    def unpack(cls, obj:dict)->'Hex':
        """
        Alternate of `pack` function. 
        """
        new_hx = Hex(QPointF(obj["x"], obj["Y"]))
        new_hx._fill = QColor(obj["red"], obj["green"], obj["blue"])
        new_hx._params = obj["params"]
        new_hx.geography=obj["geo"]
        new_hx.wind = np.array(obj["wind"])
        return new_hx



class Region(QPolygonF):
    """
    Regions are just two polygons, merged together
    """
    def __init__(self, origin:QPolygonF, *hexIDs:HexID):
        super().__init__(origin)
        self._name = "New Region"
        self._hexIDs = list(hexIDs)
        self._fill = QColor(randint(1,255),randint(1,255),randint(1,255),100)

    def average_location(self):
        mean_x = 0.0
        mean_y = 0.0
        n = len(self._hexIDs)
        for hid in self.hexIDs:
            pt = hex_to_screen(hid)
            mean_x += pt.x()/n
            mean_y += pt.y()/n
        return QPointF(mean_x, mean_y)

    @property
    def hexIDs(self)->list:
        return self._hexIDs
    @property
    def name(self)->str:
        return self._name
    @property
    def fill(self)->QColor:
        return self._fill

    def pack(self)->dict:
        """
            Converts the Region into a dictionary that can later be unpacked with the 'unpack' function 
        """
        hids = {
            "xids":[hid.xid for hid in self._hexIDs],
            "yids":[hid.yid for hid in self._hexIDs]
        }
        points = []
        for pt in range(len(self)):
            points.append([ self[pt].x(), self[pt].y()])
        return {
            "vertices":points,
            "hIDs":hids,
            "name":self._name,
            "red":self.fill.red(),
            "green":self.fill.green(),
            "blue":self.fill.blue()
        }
    @classmethod
    def unpack(cls, packed:dict)->'Region':
        verts = [QPointF(item[0], item[1]) for item in packed["vertices"]]
        hIDs = [HexID(packed["hIDs"]["xids"][i], packed["hIDs"]["yids"][i]) for i in range(len(packed["hIDs"]["yids"]))]
        new_reg = cls(QPolygonF(verts), *hIDs)
        new_reg._name = packed["name"]
        new_reg._fill=QColor(packed["red"], packed["green"], packed["blue"], 100)
        return new_reg

    def set_name(self, name:str):
        self._name = name
    def set_fill(self,fill:QColor):
        self._fill = fill

    def merge(self, other:'Region')->'Region':
        """
        Combines the regions together, returns Region
        """
        combined = self.united(other)
        new = Region(combined, *self._hexIDs)
        new._hexIDs += other.hexIDs
        new._name = self._name
        new._fill = self._fill
        return new

    def subtract(self, other:'Region')->'Region':
        combined = self.subtracted(other)
        new = Region(combined,*self._hexIDs)
        #new._hexIDs += other.hexIDs
        for id in other.hexIDs:
            if id in self._hexIDs:
                new._hexIDs.remove(id)

        new._name = self._name
        new._fill = self._fill
        return new
