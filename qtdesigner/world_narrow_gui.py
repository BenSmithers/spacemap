# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'world_widget_narrow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(169, 267)
        Form.setMinimumSize(QtCore.QSize(150, 0))
        Form.setMaximumSize(QtCore.QSize(169, 16777215))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.world_image = QtWidgets.QLabel(Form)
        self.world_image.setMaximumSize(QtCore.QSize(100, 100))
        self.world_image.setText("")
        self.world_image.setPixmap(QtGui.QPixmap("../../spacemap/images/planets/RClassD1.png"))
        self.world_image.setScaledContents(True)
        self.world_image.setObjectName("world_image")
        self.verticalLayout_2.addWidget(self.world_image)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.name_lbl = QtWidgets.QLabel(Form)
        self.name_lbl.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.name_lbl.setFont(font)
        self.name_lbl.setAutoFillBackground(False)
        self.name_lbl.setObjectName("name_lbl")
        self.horizontalLayout.addWidget(self.name_lbl)
        self.desc_layout = QtWidgets.QLabel(Form)
        self.desc_layout.setMaximumSize(QtCore.QSize(16777215, 50))
        self.desc_layout.setObjectName("desc_layout")
        self.horizontalLayout.addWidget(self.desc_layout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.name_lbl.setText(_translate("Form", "Servolos III"))
        self.desc_layout.setText(_translate("Form", "A112LE"))