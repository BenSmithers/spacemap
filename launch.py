
import typing
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QGraphicsScene
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore

from qtdesigner.main_window import Ui_MainWindow as main_gui

from traveller_utils.world import World, Government
from traveller_utils.person import Person
from traveller_utils.click_interface import Clicker
from traveller_utils.coordinates import HexID
from traveller_utils import utils 

from qtdesigner.passengers import Ui_Form as passenger_widget_gui
from qtdesigner.trade_goods import Ui_Form as trade_goods_widget_gui
from qtdesigner.planet_page import Ui_Form as planet_widget_gui
from qtdesigner.person import Ui_Form as passenger_desc_dialog_gui
from qtdesigner.government import Ui_Form as gov_widget_gui

import os 
import sys

class PassengerDialog(QDialog):
    def __init__(self, parent):
        super(PassengerDialog, self).__init__(parent)
        self.ui = passenger_desc_dialog_gui()
        self.ui.setupUi(self)

    def update_gui(self, passy:Person, pixmap):
        self.setWindowTitle(passy.name)
        self.ui.label_2.setPixmap(pixmap)
        self.ui.name_lbl.setText("{}".format(passy.name)) #, passy.pronouns))
        self.ui.app_desc.setText(passy.appearance)
        self.ui.quirks_desc.setText(passy.quirks)
        self.ui.Needs_desc.setText(passy.motivations)
        self.ui.wants_desc.setText(passy.wants)
        self.ui.probs_desc.setText(passy.problems)



class PassengerItem(QtGui.QStandardItem):
    """
    These are the items added to the great big list of spells. 

    Each carries an attribute ("this_path"), that specifies which json file correlates with this entry
    """

    def __init__(self, value, passenger):
        super(PassengerItem,self).__init__(value)
        self._this_path = passenger

    @property
    def passenger(self):
        return(self._this_path)
    
class GovWidget(QtWidgets.QWidget):
    def __init__(self, parent: QWidget):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui=gov_widget_gui()
        self.ui.setupUi(self) 

    def configure(self,gov:Government):
        add = " Faction" if gov.is_faction else ""
        self.ui.name_lbl.setText(gov.gov_type+add)
        self.ui.desc_desc.setText(gov.description)
        self.ui.contraband_desc.setText(", ".join([str(entry.name) for entry in gov.contraband]))
        self.ui.title_desc.setText(gov.title)
        if gov.is_faction:
            self.ui.strength_desc.setText(str(gov._strength))
        else:
            self.ui.strength_desc.setText("The Government")

class PassWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui=passenger_widget_gui()
        self.ui.setupUi(self)

        self.pass_list_entry = QtGui.QStandardItemModel()
        self.ui.tableView.setModel(self.pass_list_entry)
        self.ui.tableView.clicked[QtCore.QModelIndex].connect(self.pass_click)

        self.ui.berth_combo.currentIndexChanged.connect(self.log_passengers)
        self.ui.comboBox.currentIndexChanged.connect(self.log_passengers)

        self._cache_world = None

        self.people_pixes = utils.IconLib(os.path.join(os.path.dirname(__file__),"images","chars"))

    def pass_click(self, index):
        passenger_item = self.pass_list_entry.itemFromIndex(index)
        passenger = passenger_item.passenger

        pixname = passenger.image_name
        pix = self.people_pixes.access(pixname, 100)

        dialog = PassengerDialog(self)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.update_gui(passenger, pix)
        dialog.exec_()

    def log_passengers(self, world:World):
        if type(world)==int:
            all_passengers = self._cache_world.generate_passengers(0)
        else:
            self._cache_world = world
            all_passengers = world.generate_passengers(0)

        self.pass_list_entry.clear()
        for berth_key in all_passengers.keys():
            for passenger in all_passengers[berth_key]:
                if self.ui.berth_combo.currentText()!="Any":
                    if self.ui.berth_combo.currentText().lower() != berth_key.lower():
                        continue

                entry = [PassengerItem(berth_key, passenger), PassengerItem(passenger.name, passenger)]
                self.pass_list_entry.appendRow(entry)
        


class TradeWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui=trade_goods_widget_gui()
        self.ui.setupUi(self)
        
        self.ui.generate_retailer_button.clicked.connect(self.generate_retailer)

    def update_ui(self, world:World):
        return 

    def generate_retailer(self):
        new_person = Person.generate()


                
class PlanetWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui=planet_widget_gui()
        self.ui.setupUi(self)

    def update_ui(self, world:World, loc:HexID):
        self.ui.size_desc.setText("{} g at surface".format(world.gravity))
        self.ui.pressure_desc.setText("{} atmospheres".format(world.pressure))
        self.ui.atmo_desc.setText(world.atmosphere_str)
        self.ui.hydro_desc.setText(world.hydro_str)
        self.ui.tmp_desc.setText(world.temperature_str)
        self.ui.starport_desc.setText(world.starports_str)
        self.ui.code_lbl.setText(world.name)
        self.ui.code_lbl_2.setText(world.world_profile(loc))
        self.ui.pop_desc.setText(utils.number_add_comma(world._population))
        self.ui.tech_desc.setText(world.tech_level_str)
        self.ui.services_desc.setText(", ".join([entry.name for entry in world.services]))
        self.ui.trade_code_desc.setText(", ".join([entry.name for entry in world.category]).replace("_"," "))

    def clear_ui(self):
        self.ui.size_desc.setText("")
        self.ui.pressure_desc.setText("")
        self.ui.atmo_desc.setText("")
        self.ui.hydro_desc.setText("")
        self.ui.tmp_desc.setText("")
        self.ui.starport_desc.setText("")
        self.ui.code_lbl.setText("")
        self.ui.code_lbl_2.setText("")
        self.ui.pop_desc.setText("")
        self.ui.services_desc.setText("")
        self.ui.tech_desc.setText("")
        self.ui.trade_code_desc.setText("")

class main_window(QMainWindow):
    def __init__(self,parent=None):
        QWidget.__init__(self, parent)

        self.ui = main_gui()
        self.ui.setupUi(self)
        self._pass_widget =PassWidget(self)
        self._trade_widget = TradeWidget(self)
        self._planet_widget = PlanetWidget(self)
        self.ui.tabWidget.addTab(self._planet_widget, "Planet")
        self.ui.tabWidget.addTab(self._pass_widget, "Passengers")
        self.ui.tabWidget.addTab(self._trade_widget, "Trade")

        self.scene = Clicker( self.ui.map_view, self )
        # Allow the graphics view to follow the mouse when it isn't being clicked, and associate the clicker control with the ui 
        self.ui.map_view.setScene( self.scene )
        self.ui.map_view.setMouseTracking(True)


        self.govs = []

    def closeEvent(self, event):
        self.scene.closeEvent(event)

        
    def planet_selected(self, world:World, loc:HexID):
        self._planet_widget.update_ui(world, loc)
        self._pass_widget.log_passengers(world)

        while len(self.govs)>0:
            first = self.govs.pop()
            self._planet_widget.ui.formLayout_2.removeWidget(first)

        self.govs.append(GovWidget(self._planet_widget.ui.overview_page))
        self.govs[0].configure(world.government)

        for fact in world.factions:
            new = GovWidget(self._planet_widget.ui.overview_page)
            new.configure(fact)
            self.govs.append(new)

        for i, entry in enumerate(self.govs):
            self._planet_widget.ui.formLayout_2.setWidget(
                i+10, QtWidgets.QFormLayout.SpanningRole, entry
            )
        


        

    def select_none(self):
        self._planet_widget.clear_ui()
        while len(self.govs)>0:
            first = self.govs.pop()
            self._planet_widget.ui.formLayout_2.removeWidget(first)



app = QApplication(sys.argv)
app_instance = main_window()

if __name__=="__main__":
    # make sure the base saves folder exists 
    app_instance.show()
    sys.exit(app.exec_())


