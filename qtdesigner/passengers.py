# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'passengers.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(421, 348)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.berth_lbl = QtWidgets.QLabel(Form)
        self.berth_lbl.setObjectName("berth_lbl")
        self.horizontalLayout.addWidget(self.berth_lbl)
        self.berth_combo = QtWidgets.QComboBox(Form)
        self.berth_combo.setObjectName("berth_combo")
        self.berth_combo.addItem("")
        self.berth_combo.addItem("")
        self.berth_combo.addItem("")
        self.berth_combo.addItem("")
        self.berth_combo.addItem("")
        self.horizontalLayout.addWidget(self.berth_combo)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = QtWidgets.QTableView(Form)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Passengers"))
        self.berth_lbl.setText(_translate("Form", "Berth:"))
        self.berth_combo.setItemText(0, _translate("Form", "Any"))
        self.berth_combo.setItemText(1, _translate("Form", "Low"))
        self.berth_combo.setItemText(2, _translate("Form", "Basic"))
        self.berth_combo.setItemText(3, _translate("Form", "Middle"))
        self.berth_combo.setItemText(4, _translate("Form", "High"))
        self.label_2.setText(_translate("Form", "Destination Distance"))
        self.comboBox.setItemText(0, _translate("Form", "Any"))
        self.comboBox.setItemText(1, _translate("Form", "One Jump"))
        self.comboBox.setItemText(2, _translate("Form", "Two Jumps"))
        self.comboBox.setItemText(3, _translate("Form", "Three Jumps"))
        self.comboBox.setItemText(4, _translate("Form", "Four or More"))
