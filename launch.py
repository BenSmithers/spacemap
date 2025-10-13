#!/opt/homebrew/bin/python3.12
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog
from PyQt5 import QtGui
from PyQt5 import QtWidgets, QtGui, QtCore

from qtdesigner.main_window import Ui_MainWindow as main_gui

from traveller_utils.places.system import System, InterRegion
from traveller_utils.click_interface import Clicker
from traveller_utils.core.coordinates import HexID, DRAWSIZE
from traveller_utils.clock import MultiHexCalendar, Time, Clock
from traveller_utils.tables import *

from random import randint

from widgets import PassWidget, TradeWidget, PlanetWidget, NotesTab, ManyShipDialog, GovWidget, SystemDialog

import os 
import sys

# self.parent.scene.get_system(hid)
class main_window(QMainWindow):
    def __init__(self,parent=None):
        QWidget.__init__(self, parent)

        self.ui = main_gui()
        self.ui.setupUi(self)
        self._pass_widget =PassWidget(self)
        self._trade_widget = TradeWidget(self)
        self._planet_widget = PlanetWidget(self)
        self._notes_widget = NotesTab(self)
        now = Time(30, 12, randint(0,20), randint(0,11), randint(0,300)+3000)
        self._ship_widget = ManyShipDialog(self)
        self._calendar_widget = MultiHexCalendar(self, now)

        self.ui.tabWidget.addTab(self._planet_widget, "Planet")
        self.ui.tabWidget.addTab(self._calendar_widget, "Calendar")
        self.ui.tabWidget.addTab(self._pass_widget, "Passengers")
        self.ui.tabWidget.addTab(self._trade_widget, "Trade")
        self.ui.tabWidget.addTab(self._notes_widget, "Notes")
        self.ui.tabWidget.addTab(self._ship_widget, "Ships")

        #self.ui.verticalLayout.insertWidget(0, self._calendar_widget)

        self.scene = Clicker( self.ui.map_view, self, Clock(now))
        # Allow the graphics view to follow the mouse when it isn't being clicked, and associate the clicker control with the ui 
        self.ui.map_view.setScene( self.scene )
        self.ui.map_view.setMouseTracking(True)



        self.export_image()

        self.govs = []
        self._previous = None
        self._previous_reg = None

    def closeEvent(self, event):
        self.scene.closeEvent(event)

    def system_selected(self, system:System, loc:HexID):
        dialog = SystemDialog(self)
        dialog.configure(system)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        dialog.exec_()

        
    def planet_selected(self, system:System, loc:HexID):
        self._ship_widget.clear()
        while len(self.govs)>0:
            first = self.govs.pop()
            first.deleteLater()
            self._planet_widget.ui.formLayout_2.removeWidget(first)
        
        self._planet_widget.update_ui(system, loc)
        self._trade_widget.update_ui(system.starport)

        #self._pass_widget.log_passengers(loc)
        #self._notes_widget.set_text(world.notes())

        ship_cat = self.scene.ships
        these_ships = ship_cat.get_at(loc)
        for this_shipid in these_ships:
            this_ship = ship_cat.get(this_shipid)
            sub_loc = ship_cat.get_loc(this_shipid)

            sub_location = self.scene.get_sub(sub_loc)
                        
            if isinstance(sub_loc, InterRegion):
                parent = sub_location.parent
                     
                location = "In flight over {}".format(parent.name)
            else:
                location = "At {}".format(sub_location.name)
            self._ship_widget.add_ship(this_ship, location)
        self._ship_widget.update_gui()


        if False:
            
            these_ships = [self.scene.get_ship(sid) for sid in self.scene.get_ships_at(loc)]
            for ship in these_ships:
                world_routes_filter = list(filter(lambda entry:entry is not None, [self.scene.get_system(hid) for hid in ship.route]))
                route_names = [entry.name for entry in world_routes_filter]
                
                self._ship_widget.add_ship(ship, route_names)
            self._ship_widget.update_gui()

        self.govs.append(GovWidget(self._planet_widget.ui.overview_page))
        self.govs[0].configure(system.mainworld.government)

        for fact in system.mainworld.factions:
            new = GovWidget(self._planet_widget.ui.overview_page)
            new.configure(fact)
            self.govs.append(new)

        for i, entry in enumerate(self.govs):
            self._planet_widget.ui.formLayout_2.setWidget(
                i+13, QtWidgets.QFormLayout.SpanningRole, entry
            )
        
        
        if self._previous_reg is not None:
            self._previous_reg = self.scene.draw_region(self._previous_reg, False)
        if system.mainworld is not None:
            if system.mainworld.liege is None:
                self._previous_reg=self.scene.regions.get_rid(loc)
                self.scene.draw_region(self._previous_reg, True)
            else:
                self._previous_reg=None
        else:
            self._previous_reg

        if self._previous is not None:
            prev_con = self.scene.all_connections(self._previous)
            for rid in prev_con:
                self.scene.draw_route(rid, False)
        
        
        new_con = self.scene.all_connections(loc)
        if new_con is not None:
            self._previous = loc
            for rid in new_con:
                self.scene.draw_route(rid, True)
        else:
            self._previous = None


    def select_none(self):
        if self._previous is not None:
            prev_con = self.scene.all_connections(self._previous)
            for con in prev_con:
                self.scene.draw_route(con, False)
        if self._previous_reg is not None:
            self.scene.draw_region(self._previous_reg, False)

        self._previous_reg = None
        self._previous = None

        self._planet_widget.clear_ui()
        self._pass_widget.clear_pass()
        self._trade_widget.clear()
        self._notes_widget.clear()
        self._ship_widget.clear()
        self.scene.clear_drawn_route()

        while len(self.govs)>0:
            first = self.govs.pop()
            first.deleteLater()
            self._planet_widget.ui.formLayout_2.removeWidget(first)

    def export_image(self):
        size   = QtCore.QSize(DRAWSIZE*45    ,DRAWSIZE*27)
        image  = QtGui.QImage(size,QtGui.QImage.Format_ARGB32_Premultiplied)
        painter= QtGui.QPainter(image)
        self.scene.render(painter)
        painter.end()
        image.save(os.path.join(os.path.dirname(__file__),"galaxy.png"))


app = QApplication(sys.argv)
app_instance = main_window()

if __name__=="__main__":
    # make sure the base saves folder exists 
    app_instance.show()
    sys.exit(app.exec_())


