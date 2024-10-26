# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'trade_goods.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(463, 547)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.trade_good_lbl = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.trade_good_lbl.setFont(font)
        self.trade_good_lbl.setObjectName("trade_good_lbl")
        self.verticalLayout.addWidget(self.trade_good_lbl)

        self.demand_lbl = QtWidgets.QLabel(Form)
        self.demand_lbl.setObjectName("demand_lbl")
        self.demand_table = QtWidgets.QListView(Form)
        self.demand_table.setObjectName("demand_table")
        self.verticalLayout.addWidget(self.demand_lbl)
        self.verticalLayout.addWidget(self.demand_table)


        self.supply_lbl = QtWidgets.QLabel(Form)
        self.supply_lbl.setObjectName("supply_lbl")
        self.verticalLayout.addWidget(self.supply_lbl)
        self.supply_table = QtWidgets.QListView(Form)
        self.supply_table.setObjectName("supply_table")
        self.verticalLayout.addWidget(self.supply_table)

        self.buyer_lbl = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.buyer_lbl.setFont(font)
        self.buyer_lbl.setObjectName("buyer_lbl")
        self.verticalLayout.addWidget(self.buyer_lbl)
        self.buyer_table = QtWidgets.QListView(Form)
        self.buyer_table.setObjectName("buyer_table")
        self.verticalLayout.addWidget(self.buyer_table)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.trade_good_lbl.setText(_translate("Form", "Trade Goods"))
        self.supply_lbl.setText(_translate("Form","Market Supply"))
        self.demand_lbl.setText(_translate("Form", "Market Demand"))
        self.buyer_lbl.setText(_translate("Form", "Market Prices"))
