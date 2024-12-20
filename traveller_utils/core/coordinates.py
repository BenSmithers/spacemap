from PyQt5.QtCore import QPointF
import numpy as np
from math import sqrt

RTHREE = sqrt(3)
DRAWSIZE = 100
    
class HexID:
    """
        MultiHex2 uses a cubic coordinate system for the hexes. 
    """
    def __init__(self, xid:int, yid:int):
        """
        In cubic coordinates, the sum of all indices is zero. So we only need two IDs to get the third
        """
        self._xid = xid
        self._yid = yid
        self._zid = 0 - xid - yid

    def pack(self):
        return "{}.{}".format(self.xid, self.yid)
    @classmethod
    def unpack(cls, packed):
        return cls(int(packed.split(".")[0]),int( packed.split(".")[1]))

    @property
    def xid(self)->int:
        return self._xid
    @property
    def yid(self)->int:
        return self._yid
    @property
    def zid(self)->int:
        return self._zid
    def __hash__(self):
        return hash(str(self))
    def __str__(self) -> str:
        return "{}-{}".format(self._xid, self._yid)
    def __eq__(self, other):
        if other.__class__!=HexID:
            return False
        else:
            return (self.xid == other.xid) and (self.yid==other.yid)
    def __add__(self, other:'HexID'):
        return HexID(self.xid + other.xid, self.yid + other.yid)
    
    @property
    def neighbors(self):
        nb = [
            HexID(self.xid+1,self.yid), HexID(self.xid+1, self.yid-1), HexID(self.xid, self.yid+1),
            HexID(self.xid-1, self.yid),HexID(self.xid-1, self.yid+1), HexID(self.xid, self.yid-1)
        ]
        return nb

    def in_range(self, dist:int, include_self=True):
        """
            returns all hexIDs in a given range
        """
        results = []
        for i in range(-dist, dist+1):
            for j in range(max(-dist, -i-dist), min(dist, -i+dist)+1):
                if i==0 and j==0 and (not include_self):
                    continue
                results.append(self + HexID(i,j))
        return results
    def __repr__(self) -> str:
        return "{}_{}_{}".format(self._xid, self._yid, self._zid)

        # -30 degrees, increment by 60 with each
    
    def __sub__(self, other:'HexID')->int:
        """
            returns the distance between this and another HexID
        """
        inter_id = HexID(self.xid - other.xid, self.yid - other.yid)

        return int((abs(inter_id.xid) + abs(inter_id.yid) + abs(inter_id.zid))/2)

        # -30 degrees, increment by 60 with each
    def distance(self, other):
        return self - other 


class SubHID(HexID):
    def __init__(self, xid: int, yid: int, region:int, point:int):
        super().__init__(xid, yid)
        self._region = region
        self._point = point 

    def distance(self, other:'SubHID'):
        base = HexID.distance(self, other)*6 

        # not in the same system 
        if base>=0:
            return base + 1
        else: # same system, different regions 
            if other.region!=self.region:
                return 0.5 
            else:
                # same system, same region
                return 0.25 

    @property
    def region(self):
        return self._region 
    @property 
    def point(self):
        return self._point
    
    def downsize(self):
        return HexID(self.xid, self.yid)

    def __hash__(self):
        return hash(str(self))
    def __str__(self) -> str:
        return "{}-{}-{}-{}".format(self._xid, self._yid, self._region, self._point)

class NonPhysical(SubHID):
    def __init__(self):
        super().__init__(np.nan, np.nan, np.nan, np.nan)
    def __str__(self) -> str:
        return "NonPhys_Coord"
    def __eq__(self, other):
        return False
    def __hash__(self):
        return hash("SPAAAAAAACE")


# magic numbers for unit conversion
M = (3.0 / 2.0, 0.0, RTHREE/2.0, RTHREE, # F0-F3
               2.0 / 3.0, 0.0, -1.0 / 3.0, RTHREE / 3.0) #b0-b3

def screen_to_hex(point:QPointF)->HexID:
    """
        Returns the HexID for the hex containing the spot under the cursor in pixel-space 
    """
    fq = (M[4]*point.x())/DRAWSIZE
    fr = (M[6]*point.x() + M[7]*point.y())/DRAWSIZE

    q = round(fq)
    r = round(fr)
    s = -q-r

    q_diff = abs(q-fq)
    r_diff = abs(r-fr)
    s_diff = abs(s+fq+fr)
    if q_diff > r_diff and q_diff > s_diff:
        q = -r-s
    elif r_diff > s_diff:
        r = -q-s
    else:
        pass
    return HexID(q, r)

def hex_to_screen(id:HexID)->QPointF:
    """
        Returns the pixel location of the center of the given HexID 
    """
    x_loc = DRAWSIZE*(M[0]*id.xid)
    y_loc = DRAWSIZE*(M[2]*id.xid + M[3]*id.yid)
    return QPointF(x_loc, y_loc)
