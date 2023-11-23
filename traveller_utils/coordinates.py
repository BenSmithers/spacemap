from PyQt5.QtCore import QPointF
from math import sqrt

RTHREE = sqrt(3)
DRAWSIZE = 100

class Primitive:
    """
    Will implement simple versions of the raw classes for saving them efficiently 
    """
    def __init__(self)->None:
        raise NotImplementedError("Use derived class")

    def construct(self):
        raise NotImplementedError("Use derived method")
    
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
        return hash((self._xid, self._yid))
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

    def in_range(self, dist:int):
        results = []
        for i in range(-dist, dist+1):
            for j in range(max(-dist, -i-dist), min(dist, -i+dist)+1):
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


M = (3.0 / 2.0, 0.0, RTHREE/2.0, RTHREE, # F0-F3
               2.0 / 3.0, 0.0, -1.0 / 3.0, RTHREE / 3.0) #b0-b3

def screen_to_hex(point:QPointF)->HexID:
    """
        Returns the HexID for the spot under the cursor in pixel-space 
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
        Returns the pixel location of the center of the gien HexID 
    """
    x_loc = DRAWSIZE*(M[0]*id.xid)
    y_loc = DRAWSIZE*(M[2]*id.xid + M[3]*id.yid)
    return QPointF(x_loc, y_loc)
