from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QMainWindow
from traveller_utils.actions import ActionManager

from traveller_utils.enums import Title, LandTitle
from traveller_utils.coordinates import HexID, DRAWSIZE, screen_to_hex, hex_to_screen
from traveller_utils.core import Hex, Region
from traveller_utils.world import World
from traveller_utils import utils

import numpy as np
import os 
import json

water_color = (92, 157, 214)
no_water = (38, 38, 38)

WORLD_PATH = os.path.join(os.path.dirname(__file__), "..","galaxy.json")


class Clicker(QGraphicsScene,ActionManager):
    def __init__(self, parent, parent_window:QMainWindow):
        QGraphicsScene.__init__(self, parent)
        ActionManager.__init__(self)

        
        self._parent_window = parent_window
        #self.parent().scale( 0.8, 0.8 )

        self.pmap = utils.IconLib(os.path.join(os.path.dirname(__file__), "..","images","planets"))

        self._systems = {}
        self._drawn_systems = {}

        self._regions = {}
        self._drawn_regions = {}

        self._pen = QtGui.QPen() # STROKE EFFECTS
        self._pen.setColor(QtGui.QColor(240,240,240))
        self._pen.setStyle(Qt.PenStyle.SolidLine )
        self._pen.setWidth(5)
        self._brush = QtGui.QBrush() 
        self._brush.setStyle(0)

        self._selected_sid = None

        if os.path.exists(WORLD_PATH):
            _obj = open(WORLD_PATH, 'rt')
            data = json.load(_obj)
            _obj.close()
            self.unpack(data)
        else:
            self.initialize()

        self.update()

        

    def closeEvent(self, event):
        packed= self.pack()
        _obj = open(WORLD_PATH, 'wt')
        json.dump(packed, _obj, indent=4)
        _obj.close()

    @property
    def systems(self):
        return self._systems

    def pack(self)->dict:
        return {
            "systems":{key.pack():self.systems[key].pack() for key in self.systems.keys()},
            "regions":{rkey.pack():self._regions[rkey].pack() for rkey in self._regions.keys()}
        }
    
    def unpack(self, packed:dict):
        for i in range(25):
            for j in range(20):
                shift = int(i/2)
                loc = HexID(i ,j-shift)
                if loc.pack() in packed["systems"]:
                    self._systems[loc] = World.unpack(packed["systems"][loc.pack()])
                    self.draw_system(loc)
                else:
                    self.draw_hex(loc)
        for key in packed["regions"]:
            id_unpacked = HexID.unpack(key)
            self._regions[id_unpacked] = Region.unpack(packed["regions"][key])
            self.draw_region(id_unpacked)
            
        for key in self._systems.keys():
            world = self.get_system(key)
            world.set_liege(key, self.get_system(world.liege))

    def draw_selection(self, hex_id):
        if self._selected_sid is not None:
            self.removeItem(self._selected_sid)


        center = hex_to_screen(hex_id)
        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor(118, 216, 219))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        self._selected_sid = self.addPolygon(this_hex, self._pen, self._brush)
        self._selected_sid.setZValue(100)

    def initialize(self):
        sample = utils.perlin(150)*0.9 + 0.5
        by_title={
            Title.Emperor:[],
            Title.King:[],
            Title.Duke:[],
            Title.Count:[],
            Title.Lord:[],
            
        }

        for i in range(25):
            for j in range(20):
                this_val = sample[i*5][j*5]
                shift = int(i/2)
                loc = HexID(i ,j-shift)
                if np.random.rand()>this_val:
                    self.draw_hex(loc)
                else:
                    
                    self._systems[loc] = World()
                    by_title[self._systems[loc].title].append(loc)
                    self.draw_system(loc)
        
        """
            For each title, we assign each lower ranking house to an upper one. There are chances for each level that a given house has no liege 

            So, each Duke is assigned to its nearest king
        """
        max_dist = 2
        ordered_labels= [Title.Lord, Title.Count, Title.Duke, Title.King, Title.Emperor]
        odds = [0.01, 0.08, 0.25, 0.40]

        for i, title in enumerate(ordered_labels):
            if title==Title.Emperor:
                continue
            for system_id in by_title[title]:
                roll = np.random.rand()
                if roll<odds[i]:
                    continue

                use = []
                all_lists = [by_title[ordered_labels[j]] for j in range(i+1, 4)]
                for entry in all_lists:
                    use+= entry
       
                if len(use)==0:
                    continue

                """if len(by_title[ordered_labels[i+1]])==0 and i<(len(ordered_labels))-2:
                    use = by_title[ordered_labels[i+2]]
                else:
                    use = by_title[ordered_labels[i+1]]
                if len(use)==0:
                    continue"""

                distances = [system_id-senior_id for senior_id in use]
                if min(distances)>max_dist:
                    continue
                senior_index = distances.index(min(distances))


                this_world = self.get_system(system_id)
                senior_world = self.get_system( use[senior_index])

                this_world.set_liege(use[senior_index] , senior_world)
                senior_world.add_vassal(system_id, this_world)
        
        for system in self._systems.keys():
            

            center = hex_to_screen(system)
            this_hex = Hex(center)

            new = Region(this_hex, system)

            ultimate_liege = self.get_ultimate_liege(system)

            if ultimate_liege in self._regions:
                original = self._regions[ultimate_liege]
                self._regions[ultimate_liege] = original.merge(new)
            else:
                self._regions[ultimate_liege] = new

        for rid in self._regions.keys():
            self.draw_region(rid)

    def get_ultimate_liege(self, hexID:HexID):
        world = self.get_system(hexID)
        liege = world.liege
        if liege is None:
            return hexID
        else:
            return self.get_ultimate_liege(liege)


    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        loc =  screen_to_hex( event.scenePos() )

        if loc in self._systems: 
            self.draw_selection(loc)
            self._parent_window.planet_selected(self._systems[loc], loc )
        else:
            self._parent_window.select_none()
            if self._selected_sid is not None:
                self.removeItem(self._selected_sid)
            self._selected_sid = None
    

    def get_system(self, hex_id:HexID)->World:
        if hex_id in self._systems:
            return self._systems[hex_id]
        else:
            return None
        
    def get_region(self, hex_id:HexID)->Region:
        if hex_id in self._regions:
            return self._regions[hex_id]
        else:
            return None
        
    def draw_hex(self, hex_id:HexID):
        if hex_id in  self._drawn_systems:
            for entry in self._drawn_systems[hex_id]:
                self.removeItem(entry)

        center = hex_to_screen(hex_id)
        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor(150,150,150))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        sid = self.addPolygon(this_hex, self._pen, self._brush)
        sid.setZValue(0)
        self._drawn_systems[hex_id] = (sid,)

    def draw_region(self, origin:HexID):
        if origin in self._drawn_regions:
            for entry in self._drawn_regions[origin]:
                self.removeItem(entry)

        this_region = self.get_region(origin)
        if this_region is None:
            del self._drawn_regions[origin]
            return 
            
        self._pen.setStyle(0)
        self._brush.setStyle(1)
        self._brush.setColor(QtGui.QColor(this_region.fill))

        sid = self.addPolygon(this_region, self._pen, self._brush)
        self._drawn_regions[origin] = (sid, )

    def draw_system(self, hex_id:HexID):
        if hex_id in  self._drawn_systems:
            for entry in self._drawn_systems[hex_id]:
                self.removeItem(entry)

        this_world = self.get_system(hex_id)
        if this_world is None:
            del self._drawn_systems[hex_id]
            return

        if this_world._hydro>2:
            color = water_color
        else:
            color = no_water

        center = hex_to_screen(hex_id)
        this_hex = Hex(center)
        self._pen.setColor(QtGui.QColor(150,150,150))
        self._pen.setStyle(1)
        self._brush.setStyle(0)
        sid = self.addPolygon(this_hex, self._pen, self._brush)
        
        self._brush.setStyle(1)
        self._pen.setStyle(0)
        self._brush.setColor(QtGui.QColor(*color))

        sid_4 = self.addText(this_world._name)
        sid_4.setX(center.x()-0.25*DRAWSIZE)
        sid_4.setY(center.y()-DRAWSIZE*0.75)
        sid_4.setZValue(10)

        sid_3 = self.addText(this_world.world_profile(hex_id) )# , location=QtCore.QPointF(center.x(), center.y()+DRAWSIZE*0.25))
        sid_3.setX(center.x()-0.5*DRAWSIZE)
        sid_3.setY(center.y()+DRAWSIZE*0.4)
        sid_3.setZValue(10)

        #sid_2 = self.addEllipse(center.x()-DRAWSIZE*0.25, center.y()-DRAWSIZE*0.25, DRAWSIZE*0.5, DRAWSIZE*0.5, self._pen, self._brush)

        sid_2 = self.addPixmap(self.pmap.access(this_world.get_image_name(), 0.8*DRAWSIZE))
        sid_2.setX(center.x()-DRAWSIZE*0.4)
        sid_2.setY(center.y()-DRAWSIZE*0.4)
        sid_2.setZValue(10) 

        self._drawn_systems[hex_id] = (sid, sid_2, sid_3, sid_4)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Called when a keyboard button is released
        """
        event.accept()
        if event.key() == QtCore.Qt.Key_Plus or event.key()==QtCore.Qt.Key_PageUp or event.key()==QtCore.Qt.Key_BracketRight:
            self.parent().scale( 1.05, 1.05 )

        if event.key() == QtCore.Qt.Key_Minus or event.key()==QtCore.Qt.Key_PageDown or event.key()==QtCore.Qt.Key_BracketLeft:
            self.parent().scale( 0.95, 0.95 )