# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor_window.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(435, 451)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.label_15 = QtWidgets.QLabel(Form)
        self.label_15.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_15.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.verticalLayout.addWidget(self.label_15)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.atmo_desc = QtWidgets.QSpinBox(Form)
        self.atmo_desc.setObjectName("atmo_desc")
        self.gridLayout.addWidget(self.atmo_desc, 0, 1, 1, 1)
        self.starport_desc = QtWidgets.QLabel(Form)
        self.starport_desc.setObjectName("starport_desc")
        self.gridLayout.addWidget(self.starport_desc, 2, 2, 1, 1)
        self.temp_desc = QtWidgets.QLabel(Form)
        self.temp_desc.setObjectName("temp_desc")
        self.gridLayout.addWidget(self.temp_desc, 3, 2, 1, 1)
        self.tl_desc = QtWidgets.QLabel(Form)
        self.tl_desc.setObjectName("tl_desc")
        self.gridLayout.addWidget(self.tl_desc, 6, 2, 1, 1)
        self.tl_lbl = QtWidgets.QLabel(Form)
        self.tl_lbl.setObjectName("tl_lbl")
        self.gridLayout.addWidget(self.tl_lbl, 6, 0, 1, 1)
        self.size_lbl = QtWidgets.QLabel(Form)
        self.size_lbl.setObjectName("size_lbl")
        self.gridLayout.addWidget(self.size_lbl, 1, 0, 1, 1)
        self.hydro_spin = QtWidgets.QSpinBox(Form)
        self.hydro_spin.setObjectName("hydro_spin")
        self.gridLayout.addWidget(self.hydro_spin, 4, 1, 1, 1)
        self.hydro_desc = QtWidgets.QLabel(Form)
        self.hydro_desc.setObjectName("hydro_desc")
        self.gridLayout.addWidget(self.hydro_desc, 4, 2, 1, 1)
        self.pop_spin = QtWidgets.QSpinBox(Form)
        self.pop_spin.setObjectName("pop_spin")
        self.gridLayout.addWidget(self.pop_spin, 5, 1, 1, 1)
        self.atmo_lbl = QtWidgets.QLabel(Form)
        self.atmo_lbl.setObjectName("atmo_lbl")
        self.gridLayout.addWidget(self.atmo_lbl, 0, 0, 1, 1)
        self.pop_lbl = QtWidgets.QLabel(Form)
        self.pop_lbl.setObjectName("pop_lbl")
        self.gridLayout.addWidget(self.pop_lbl, 5, 0, 1, 1)
        self.size_desc = QtWidgets.QLabel(Form)
        self.size_desc.setObjectName("size_desc")
        self.gridLayout.addWidget(self.size_desc, 1, 2, 1, 1)
        self.label_13 = QtWidgets.QLabel(Form)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 7, 0, 1, 1)
        self.tl_spin = QtWidgets.QSpinBox(Form)
        self.tl_spin.setObjectName("tl_spin")
        self.gridLayout.addWidget(self.tl_spin, 6, 1, 1, 1)
        self.size_spin = QtWidgets.QSpinBox(Form)
        self.size_spin.setObjectName("size_spin")
        self.gridLayout.addWidget(self.size_spin, 1, 1, 1, 1)
        self.temp_spin = QtWidgets.QSpinBox(Form)
        self.temp_spin.setObjectName("temp_spin")
        self.gridLayout.addWidget(self.temp_spin, 3, 1, 1, 1)
        self.starport_combo = QtWidgets.QComboBox(Form)
        self.starport_combo.setObjectName("starport_combo")
        self.starport_combo.addItem("")
        self.starport_combo.addItem("")
        self.starport_combo.addItem("")
        self.starport_combo.addItem("")
        self.starport_combo.addItem("")
        self.starport_combo.addItem("")
        self.gridLayout.addWidget(self.starport_combo, 2, 1, 1, 1)
        self.pop_desc = QtWidgets.QLabel(Form)
        self.pop_desc.setObjectName("pop_desc")
        self.gridLayout.addWidget(self.pop_desc, 5, 2, 1, 1)
        self.hydro_lbl = QtWidgets.QLabel(Form)
        self.hydro_lbl.setObjectName("hydro_lbl")
        self.gridLayout.addWidget(self.hydro_lbl, 4, 0, 1, 1)
        self.atmo_spin = QtWidgets.QLabel(Form)
        self.atmo_spin.setObjectName("atmo_spin")
        self.gridLayout.addWidget(self.atmo_spin, 0, 2, 1, 1)
        self.starport_lbl = QtWidgets.QLabel(Form)
        self.starport_lbl.setObjectName("starport_lbl")
        self.gridLayout.addWidget(self.starport_lbl, 2, 0, 1, 1)
        self.trade_code_desc = QtWidgets.QLabel(Form)
        self.trade_code_desc.setObjectName("trade_code_desc")
        self.gridLayout.addWidget(self.trade_code_desc, 7, 2, 1, 1)
        self.temp_lbl = QtWidgets.QLabel(Form)
        self.temp_lbl.setObjectName("temp_lbl")
        self.gridLayout.addWidget(self.temp_lbl, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Form)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Discard|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lineEdit.setText(_translate("Form", "Mert"))
        self.label_15.setText(_translate("Form", "E4357877"))
        self.starport_desc.setText(_translate("Form", "Frontier"))
        self.temp_desc.setText(_translate("Form", "Scalding"))
        self.tl_desc.setText(_translate("Form", "8 - pre-stellar) "))
        self.tl_lbl.setText(_translate("Form", "Tech Level"))
        self.size_lbl.setText(_translate("Form", "Size"))
        self.hydro_desc.setText(_translate("Form", "Dessert"))
        self.atmo_lbl.setText(_translate("Form", "Atmosophere:"))
        self.pop_lbl.setText(_translate("Form", "Population"))
        self.size_desc.setText(_translate("Form", "0.35 g at the surface"))
        self.label_13.setText(_translate("Form", "Trade Codes"))
        self.starport_combo.setItemText(0, _translate("Form", "A"))
        self.starport_combo.setItemText(1, _translate("Form", "B"))
        self.starport_combo.setItemText(2, _translate("Form", "C"))
        self.starport_combo.setItemText(3, _translate("Form", "D"))
        self.starport_combo.setItemText(4, _translate("Form", "E"))
        self.starport_combo.setItemText(5, _translate("Form", "X"))
        self.pop_desc.setText(_translate("Form", "About X"))
        self.hydro_lbl.setText(_translate("Form", "Hydrodynamics"))
        self.atmo_spin.setText(_translate("Form", ": description"))
        self.starport_lbl.setText(_translate("Form", "Starport:"))
        self.trade_code_desc.setText(_translate("Form", "Auto-Generated"))
        self.temp_lbl.setText(_translate("Form", "Temperature"))
