#!/opt/homebrew/bin/python3.12
import typing
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore

from qtdesigner.main_window import Ui_MainWindow as main_gui

from traveller_utils.world import World, Government, star_hex
from traveller_utils.person import Person
from traveller_utils.retailer import Retailer
from traveller_utils.click_interface import Clicker
from traveller_utils.coordinates import HexID, DRAWSIZE
from traveller_utils import utils 
from traveller_utils.tables import fares
from traveller_utils.clock import MultiHexCalendar, Time, Clock

from qtdesigner.passengers import Ui_Form as passenger_widget_gui
from qtdesigner.trade_goods import Ui_Form as trade_goods_widget_gui
from qtdesigner.planet_page import Ui_Form as planet_widget_gui
from qtdesigner.person import Ui_Form as passenger_desc_dialog_gui
from qtdesigner.government import Ui_Form as gov_widget_gui
from qtdesigner.notes_ui import Ui_Form as notes_widget
from qtdesigner.editor_window import Ui_Form as editor_window

from traveller_utils.tables import *

from random import randint

import os 
import sys


class EditorDialog(QDialog):
    def __init__(self, parent):
        super(EditorDialog, self).__init__(parent)
        self.ui = editor_window()
        self.ui.setupUi(self)
        self._configuring = None

        self.ui.atmo_desc.valueChanged.connect(self.update_descriptions)
        self.ui.size_spin.valueChanged.connect(self.update_descriptions)
        self.ui.starport_combo.currentIndexChanged.connect(self.update_descriptions)
        self.ui.temp_spin.valueChanged.connect(self.update_descriptions)
        self.ui.hydro_spin.valueChanged.connect(self.update_descriptions)
        self.ui.pop_spin.valueChanged.connect(self.update_descriptions)
        self.ui.tl_spin.valueChanged.connect(self.update_descriptions)
        self.ui.tl_spin.setMaximum(len(star_hex)-1)

        self.ui.buttonBox.accepted.connect(self.set_world_to_ui)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Discard).clicked.connect(self.exit)

    def exit(self):
        self.close()

    def set_ui_to_world(self, world:World):
        """
            prepares the internal UI to that of the world it is passed
        """
        self._configuring = world
        self.ui.atmo_desc.setValue(world._atmosphere)
        self.ui.size_spin.setValue(world._size)
        #self.ui.pressure_spin.setValue(world._pressure)
        values = ["A","B","C","D","E","X"]
        self.ui.starport_combo.setCurrentIndex(values.index(world.starport_cat))
        self.ui.temp_spin.setValue(world._temperature)
        self.ui.hydro_spin.setValue(world._hydro)
        self.ui.pop_spin.setValue(world._population_raw)
        self.ui.tl_spin.setValue(world._tech_level)

        self.ui.pop_spin.setMaximum(12)
        self.ui.label_15.setText(world.world_profile(""))
        self.ui.lineEdit.setText(world.name)
        
        self.update_descriptions()

    def update_descriptions(self):
        
        what= "{} atmosphere.".format(atmo.access(self.ui.atmo_desc.value()))
        self.ui.atmo_spin.setText(what)

        trim = list(sorted((set(starports_quality))))[::-1]
        star_index = self.ui.starport_combo.currentIndex()
        self.ui.starport_desc.setText(trim[star_index])

        what = "The planet is " + temp.access(self.ui.temp_spin.value())
        self.ui.temp_desc.setText(what)
        
        what = "The planet " + hydro.access(self.ui.hydro_spin.value()).lower()
        self.ui.hydro_desc.setText(what)

        pop = int((10**self.ui.pop_spin.value()))
        what = "It has a population of approximately {}".format(utils.number_add_comma(pop))
        self.ui.pop_desc.setText(what)

        self.ui.tl_desc.setWordWrap(True)
        self.ui.tl_desc.setText("{}".format(tl.access(self.ui.tl_spin.value())))

        profile= ""
        profile+=starports_str[star_index]
        profile+=star_hex[self.ui.size_spin.value()]
        profile+=star_hex[self.ui.atmo_desc.value()]
        profile+=star_hex[self.ui.hydro_spin.value()]
        profile+=star_hex[self.ui.pop_spin.value()]
        profile+="#"
        profile+="#" #star_hex[min([self._law_level, len(star_hex)-1])]
        profile+=star_hex[self.ui.tl_spin.value()]


        #self.ui.trade_code_desc.setText(". ".join([str(entry) for entry in world.category]))

        self.ui.label_15.setText(profile)

    def set_world_to_ui(self)->World:
        print("Accept!")
        return self._configuring

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

    def __init__(self, passenger:Person, berth, world_name, fare):
        combined = "{} - {} - {} for ${} FC".format(berth, passenger.name, world_name, fare)
        super(PassengerItem,self).__init__(combined)
        self._this_path = passenger
        self._berth = berth
        self._dest = world_name

    @property
    def passenger(self):
        return(self._this_path)
    
    def destination(self):
        return self._this_path.destination
    
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

class NotesTab(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = notes_widget()
        self.ui.setupUi(self)

    def set_text(self, text):
        self.ui.textBrowser.setPlainText(text)
    def clear(self):
        self.ui.textBrowser.setPlainText("")

class PassWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.ui=passenger_widget_gui()
        self.ui.setupUi(self)

        self.pass_list_entry = QtGui.QStandardItemModel()
        self.ui.tableView.setModel(self.pass_list_entry)
        self.ui.tableView.clicked[QtCore.QModelIndex].connect(self.pass_click)

        self._pass_selected = ""

        self.ui.berth_combo.currentIndexChanged.connect(self.log_passengers)
        self.ui.comboBox.currentIndexChanged.connect(self.log_passengers)

        self._cache_pass = None
        self._hid = None


        self.people_pixes = utils.IconLib(os.path.join(os.path.dirname(__file__),"images","chars"))

    def pass_click(self, index):
        
        passenger_item = self.pass_list_entry.itemFromIndex(index)
        passenger = passenger_item.passenger

        if self._pass_selected!=passenger.name:
            self.parent.scene.draw_route_to(self._hid, passenger.destination)
            self._pass_selected = passenger.name
        else:
            pixname = passenger.image_name
            pix = self.people_pixes.access(pixname, 100)
            dialog = PassengerDialog(self)
            dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            dialog.update_gui(passenger, pix)
            dialog.exec_()

    def clear_pass(self):
        self.pass_list_entry.clear()
        self._pass_selected = ""

    def log_passengers(self, loc):

        if type(loc)==int:
            # the call is coming  from inside the house!
            all_passengers = self._cache_pass
        else:
            all_passengers = self.parent.scene.generate_passengers(loc)
            self._cache_pass = all_passengers
            self._hid = loc

        

        self.pass_list_entry.clear()
        for berth_key in all_passengers.keys():
            for passenger in all_passengers[berth_key]:
                if self.ui.berth_combo.currentText()!="Any":
                    if self.ui.berth_combo.currentText().lower() != berth_key.lower():
                        continue
                
                world = self.parent.scene.get_system(passenger.destination)
                dist = int(passenger.destination - self._hid) 
                if self.ui.comboBox.currentText()!="Any":
                    index = self.ui.comboBox.currentIndex()
                    if index==4:
                        if dist<4:
                            continue
                    elif index!=dist:
                        continue
                
                fare = fares[berth_key][dist-1]
                #entry = [PassengerItem(berth_key, passenger), PassengerItem(passenger.name, passenger)]
                self.pass_list_entry.appendRow(PassengerItem(passenger, berth_key, world.name, fare))

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
        if not this_retail.generated:
            this_retail.regenerate(self._world, self.ui.skill_spin.value())
            
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
        self.ui.edit_button.clicked.connect(self.edit_button)
        self._selected = None

    def edit_button(self):
        if self._selected is None:
            return 
        else:
            
            dialog = EditorDialog(self)
            dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            dialog.set_ui_to_world(self._selected)
            dialog.exec_()

    def update_ui(self, world:World, loc:HexID):
        self._selected = world

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
        self._selected = None
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

        self._calendar_widget = MultiHexCalendar(self, now)

        self.ui.tabWidget.addTab(self._planet_widget, "Planet")
        #self.ui.tabWidget.addTab(self._calendar_widget, "Calendar")
        self.ui.tabWidget.addTab(self._pass_widget, "Passengers")
        self.ui.tabWidget.addTab(self._trade_widget, "Trade")
        self.ui.tabWidget.addTab(self._notes_widget, "Notes")

        self.ui.verticalLayout.insertWidget(0, self._calendar_widget)

        self.scene = Clicker( self.ui.map_view, self, Clock(now))
        # Allow the graphics view to follow the mouse when it isn't being clicked, and associate the clicker control with the ui 
        self.ui.map_view.setScene( self.scene )
        self.ui.map_view.setMouseTracking(True)


        

        self.export_image()

        self.govs = []
        self._previous = None

    def closeEvent(self, event):
        self.scene.closeEvent(event)

        
    def planet_selected(self, world:World, loc:HexID):
        while len(self.govs)>0:
            first = self.govs.pop()
            first.deleteLater()
            self._planet_widget.ui.formLayout_2.removeWidget(first)
        
        self._planet_widget.update_ui(world, loc)
        self._trade_widget.update_ui(world)

        self._pass_widget.log_passengers(loc)
        self._notes_widget.set_text(world.notes())


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

        if self._previous is not None:
            prev_con = self.scene.all_connections(self._previous)
            for con in prev_con:
                self.scene.draw_route(self._previous, con, False)
        
        self._previous = loc
        new_con = self.scene.all_connections(loc)
        for con in new_con:
            self.scene.draw_route(loc, con, True)

    def select_none(self):
        if self._previous is not None:
            prev_con = self.scene.all_connections(self._previous)
            for con in prev_con:
                self.scene.draw_route(self._previous, con, False)
        self._previous = None

        self._planet_widget.clear_ui()
        self._pass_widget.clear_pass()
        self._trade_widget.clear()
        self._notes_widget.clear()
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


