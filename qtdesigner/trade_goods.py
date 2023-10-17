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

        self.generate_retailer_button = QtWidgets.QPushButton()
        self.generate_retailer_button.setText("Generate Retailer")
        self.verticalLayout.addWidget(self.generate_retailer_button)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.retailer_lbl = QtWidgets.QLabel(Form)
        self.retailer_lbl.setObjectName("retailer_lbl")
        self.horizontalLayout_2.addWidget(self.retailer_lbl)
        self.retailer_combo = QtWidgets.QComboBox(Form)
        self.retailer_combo.setObjectName("retailer_combo")
        
        self.horizontalLayout_2.addWidget(self.retailer_combo)
        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.type_lbl = QtWidgets.QLabel(Form)
        self.type_lbl.setObjectName("type_lbl")
        self.horizontalLayout.addWidget(self.type_lbl)
        self.type_combo = QtWidgets.QComboBox(Form)
        self.type_combo.setObjectName("type_combo")
        self.type_combo.addItem("")
        self.horizontalLayout.addWidget(self.type_combo)
        self.verticalLayout.addLayout(self.horizontalLayout)


        self.trade_good_table = QtWidgets.QTableView(Form)
        self.trade_good_table.setObjectName("trade_good_table")
        self.verticalLayout.addWidget(self.trade_good_table)
        self.buyer_lbl = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.buyer_lbl.setFont(font)
        self.buyer_lbl.setObjectName("buyer_lbl")
        self.verticalLayout.addWidget(self.buyer_lbl)
        self.buyer_table = QtWidgets.QTableView(Form)
        self.buyer_table.setObjectName("buyer_table")
        self.verticalLayout.addWidget(self.buyer_table)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.trade_good_lbl.setText(_translate("Form", "Trade Goods"))
        self.type_lbl.setText(_translate("Form", "Type"))
        self.type_combo.setItemText(0, _translate("Form", "Any"))
        self.buyer_lbl.setText(_translate("Form", "Buyers"))
        self.retailer_lbl.setText(_translate("Form", "Retailer"))
