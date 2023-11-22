#!/usr/bin/python3.8
import typing
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QGraphicsScene
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore

from qtdesigner.main_window import Ui_MainWindow as main_gui

from traveller_utils.world import World, Government
from traveller_utils.person import Person
from traveller_utils.retailer import Retailer
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
    
class SellerItem(QtGui.QStandardItem):
    def __init__(self, item:str, price:float, qty):
        if qty=="":
            combined = "{} : ${:.2f} per unit".format(item, price)
        else:
            combined = "{} : ${:.2f} per unit | {} units".format(item, price, qty)
        super(SellerItem, self).__init__(combined)
        self._item = item
        self._price = price
        self._qty = qty

    
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

    def clear_pass(self):
        self.pass_list_entry.clear()

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
        self.seller_list_entry = QtGui.QStandardItemModel()
        self.buyer_table_entry = QtGui.QStandardItemModel()
        self.ui.trade_good_table.setModel(self.seller_list_entry)
        self.ui.trade_good_table.clicked[QtCore.QModelIndex].connect(self.trade_good_clicked)

        self.ui.buyer_table.setModel(self.buyer_table_entry)
        self.ui.buyer_table.clicked[QtCore.QModelIndex].connect(self.buyer_clicked)
        self.ui.retailer_combo.currentIndexChanged.connect(self.retail_combo_updated)
        self.ui.type_combo.currentIndexChanged.connect(self.retail_combo_updated)

        self._world= None


    def clear(self):
        self._world = None
        self.seller_list_entry.clear()
        self.buyer_table_entry.clear()
        self.ui.retailer_combo.clear()

    def update_ui(self, world:World):        
        self._world = world
        if world is not None:
            all_retails = world.retailers

        self.seller_list_entry.clear()
        self.buyer_table_entry.clear()
        self.ui.retailer_combo.clear()

        mod = 0
        if world.starport_cat=="A":
            mod = -6
        elif world.starport_cat=="B":
            mod = -4
        elif world.starport_cat=="C":
            mod = -2
        elif world.starport_cat=="E":
            mod +=4

        add_string = "Finding a Retailer: CR {}+, 1D days (hours online)\n".format(8+mod)
        add_string += "+1 per attempt each month "
        self.ui.difficulty_lbl.setText(add_string)

        if len(all_retails)==0:
            return
        for retailer in world.retailers:
            self.ui.retailer_combo.addItem(retailer.name)

        #chosen_retailer = all_retails[self.ui.retailer_combo.currentIndex()]

        self.retail_combo_updated()

    def retail_combo_updated(self):
        index = self.ui.retailer_combo.currentIndex()
        self.seller_list_entry.clear()
        self.buyer_table_entry.clear()

        if self._world is None:
            return

        if len(self._world.retailers)==0:
            return

        this_retail = self._world.retailers[index]
        for entry in this_retail.sale_prices.keys():
            if self.ui.type_combo.currentText()!="Any":
                if self.ui.type_combo.currentText()=="Uncommon":
                    if ("advanced" in entry.name.lower() or "Common" in entry.name or "illegal" in entry.name.lower()):
                        continue
                elif self.ui.type_combo.currentText() not in entry.name:
                    continue
            new_item = SellerItem(entry.name, this_retail.sale_prices[entry]["price"],this_retail.sale_prices[entry]["amount"] )
            self.seller_list_entry.appendRow(new_item)

        for entry in this_retail.purchase_prices.keys():
            if self.ui.type_combo.currentText()!="Any":
                if self.ui.type_combo.currentText()=="Uncommon":
                    if ("advanced" in entry.name.lower() or "Common" in entry.name or "illegal" in entry.name.lower()):
                        continue
                elif self.ui.type_combo.currentText() not in entry.name:
                    continue
            new_item = SellerItem(entry.name, this_retail.purchase_prices[entry]["price"], "")
            self.buyer_table_entry.appendRow(new_item)
        

    def generate_retailer(self):
        if self._world is None:
            raise ValueError("This should be unreachable")

        print("generating retailer")

        new_retailer = Retailer()
        self._world._retailers.append(new_retailer)
        new_retailer.regenerate(self._world, self.ui.skill_spin.value())

        self.update_ui(self._world)

    def trade_good_clicked(self, what):
        item = self.seller_list_entry.itemFromIndex(what)

    def buyer_clicked(self, what):
        item = self.buyer_table_entry.itemFromIndex(what)


                
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

        if world.liege_world is not None:
            self.ui.liege_desc.setText(world.liege_world.name)
        else:
            self.ui.liege_desc.setText("")

        self.ui.vassal_desc.setWordWrap(True)
        if len(world.vassals_worlds)!=0:
            text= ", ".join([entry.name for entry in world.vassals_worlds])

            self.ui.vassal_desc.setText(text)
        else:
            self.ui.vassal_desc.setText("")

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
        self.ui.liege_desc.setText("")
        self.ui.vassal_desc.setText("")

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
        while len(self.govs)>0:
            first = self.govs.pop()
            first.deleteLater()
            self._planet_widget.ui.formLayout_2.removeWidget(first)
        
        self._planet_widget.update_ui(world, loc)
        self._trade_widget.update_ui(world)
        self._pass_widget.log_passengers(world)


        self.govs.append(GovWidget(self._planet_widget.ui.overview_page))
        self.govs[0].configure(world.government)

        for fact in world.factions:
            new = GovWidget(self._planet_widget.ui.overview_page)
            new.configure(fact)
            self.govs.append(new)

        for i, entry in enumerate(self.govs):
            self._planet_widget.ui.formLayout_2.setWidget(
                i+12, QtWidgets.QFormLayout.SpanningRole, entry
            )

    def select_none(self):
        self._planet_widget.clear_ui()
        self._pass_widget.clear_pass()
        self._trade_widget.clear()

        while len(self.govs)>0:
            first = self.govs.pop()
            first.deleteLater()
            self._planet_widget.ui.formLayout_2.removeWidget(first)



app = QApplication(sys.argv)
app_instance = main_window()

if __name__=="__main__":
    # make sure the base saves folder exists 
    app_instance.show()
    sys.exit(app.exec_())


