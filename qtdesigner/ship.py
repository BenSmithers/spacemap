# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ship.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(448, 558)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox = QtWidgets.QComboBox(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.textBox = QtWidgets.QTextBrowser(Form)
        self.textBox.setObjectName("textBox")
        self.verticalLayout.addWidget(self.textBox)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.formLayout = QtWidgets.QFormLayout(self.tab)
        self.formLayout.setObjectName("formLayout")
        self.desc = QtWidgets.QLabel(self.tab)
        self.desc.setObjectName("desc")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.desc)
        
        self.route_lbl = QtWidgets.QLabel(self.tab)
        self.route_lbl.setObjectName("route_lbl")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.route_lbl)
        self.route = QtWidgets.QLabel(self.tab)
        self.route.setObjectName("route")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.route)

        self.carg_lbl = QtWidgets.QLabel(self.tab)
        self.carg_lbl.setObjectName("carg_lbl")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.carg_lbl)
        self.cargo = QtWidgets.QTextBrowser(self.tab)
        self.cargo.setObjectName("cargo")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.cargo)
        self.speed_lbl = QtWidgets.QLabel(self.tab)
        self.speed_lbl.setObjectName("speed_lbl")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.speed_lbl)
        self.speed = QtWidgets.QLabel(self.tab)
        self.speed.setObjectName("speed")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.speed)
        self.tabWidget.addTab(self.tab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Form)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.desc.setText(_translate("Form", "A medium freighter ship"))
        self.route_lbl.setText(_translate("Form", "Location:"))

        self.carg_lbl.setText(_translate("Form", "Cargo:"))
        self.speed_lbl.setText(_translate("Form", "Speed"))
        self.speed.setText(_translate("Form", "N days / hex"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Ship"))
