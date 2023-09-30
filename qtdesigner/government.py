# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'person.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.formLayout_2 = QtWidgets.QFormLayout(Form)
        self.formLayout_2.setObjectName("formLayout_2")

        self.name_lbl = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.name_lbl.setFont(font)
        self.name_lbl.setObjectName("name_lbl")
        self.name_lbl.setWordWrap(True)
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.name_lbl)


        self.desc_lbl = QtWidgets.QLabel(Form)
        self.desc_lbl.setObjectName("desc_lbl")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.desc_lbl)
        self.desc_desc = QtWidgets.QLabel(Form)
        self.desc_desc.setWordWrap(True)
        self.desc_desc.setObjectName("desc_desc")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.desc_desc)

        self.title_lbl = QtWidgets.QLabel(Form)
        self.title_lbl.setObjectName("title_lbl")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.title_lbl)
        self.title_desc = QtWidgets.QLabel(Form)
        self.title_desc.setObjectName("title_desc")
        self.title_desc.setWordWrap(True)
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.title_desc)

        
        self.contraband_lbl = QtWidgets.QLabel(Form)
        self.contraband_lbl.setObjectName("contraband_lbl")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.contraband_lbl)
        self.contraband_desc = QtWidgets.QLabel(Form)
        self.contraband_desc.setObjectName("contraband_desc")
        self.contraband_desc.setWordWrap(True)
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.contraband_desc)
      
        self.strength_lbl = QtWidgets.QLabel(Form)
        self.strength_lbl.setObjectName("strength_lbl")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.strength_lbl)
        self.strength_desc = QtWidgets.QLabel(Form)
        self.strength_desc.setObjectName("strength_desc")
        self.strength_desc.setWordWrap(True)
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.strength_desc)
      

        #self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)
        

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.desc_lbl.setText(_translate("Form", "Description"))
        self.contraband_lbl.setText(_translate("Form", "Contraband"))
        self.title_lbl.setText(_translate("Form", "Title"))
        self.strength_lbl.setText(_translate("Form", "Strength"))
