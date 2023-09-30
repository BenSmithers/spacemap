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
        self.buttonBox = QtWidgets.QDialogButtonBox(Form)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        
        self.name_lbl = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.name_lbl.setFont(font)
        self.name_lbl.setObjectName("name_lbl")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.name_lbl)

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.label_2)

        self.app_lbl = QtWidgets.QLabel(Form)
        self.app_lbl.setObjectName("app_lbl")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.app_lbl)
        self.app_desc = QtWidgets.QLabel(Form)
        self.app_desc.setObjectName("app_desc")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.app_desc)

        self.Needs_lbl = QtWidgets.QLabel(Form)
        self.Needs_lbl.setObjectName("Needs_lbl")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.Needs_lbl)
        self.Needs_desc = QtWidgets.QLabel(Form)
        self.Needs_desc.setObjectName("Needs_desc")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.Needs_desc)

        
        self.quirks_lbl = QtWidgets.QLabel(Form)
        self.quirks_lbl.setObjectName("quirks_lbl")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.quirks_lbl)
        self.quirks_desc = QtWidgets.QLabel(Form)
        self.quirks_desc.setObjectName("quirks_desc")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.quirks_desc)
        

        self.wants_lbl = QtWidgets.QLabel(Form)
        self.wants_lbl.setObjectName("wants_lbl")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.wants_lbl)
        self.wants_desc = QtWidgets.QLabel(Form)
        self.wants_desc.setObjectName("wants_desc")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.wants_desc)

        self.probs_lbl = QtWidgets.QLabel(Form)
        self.probs_lbl.setObjectName("probs_lbl")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.probs_lbl)
        self.probs_desc = QtWidgets.QLabel(Form)
        self.probs_desc.setObjectName("probs_desc")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.probs_desc)

        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)
        

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.name_lbl.setText(_translate("Form", "Frank Frankovich (he/him)"))
        self.app_lbl.setText(_translate("Form", "Appearance"))
        self.quirks_lbl.setText(_translate("Form", "Quirks"))
        self.Needs_lbl.setText(_translate("Form", "Motivations"))
        self.wants_lbl.setText(_translate("Form", "Wants"))
        self.probs_lbl.setText(_translate("Form", "Problems"))
        self.label_2.setText(_translate("Form", ""))
