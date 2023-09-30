# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'planet_page.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(418, 403)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.code_lbl = QtWidgets.QLabel(Form)
        self.code_lbl.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.code_lbl.setFont(font)
        self.code_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.code_lbl.setObjectName("code_lbl")
        self.verticalLayout.addWidget(self.code_lbl)
        self.code_lbl_2 = QtWidgets.QLabel(Form)
        self.code_lbl_2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.code_lbl_2.setAlignment(QtCore.Qt.AlignCenter)
        self.code_lbl_2.setObjectName("code_lbl_2")
        self.verticalLayout.addWidget(self.code_lbl_2)
        self.toolBox = QtWidgets.QToolBox(Form)
        self.toolBox.setObjectName("toolBox")
        self.overview_page = QtWidgets.QWidget()
        self.overview_page.setGeometry(QtCore.QRect(0, 0, 400, 275))
        self.overview_page.setObjectName("overview_page")
        self.formLayout_2 = QtWidgets.QFormLayout(self.overview_page)
        self.formLayout_2.setObjectName("formLayout_2")
        self.starport_lbl = QtWidgets.QLabel(self.overview_page)
        self.starport_lbl.setObjectName("starport_lbl")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.starport_lbl)
        self.starport_desc = QtWidgets.QLabel(self.overview_page)
        self.starport_desc.setObjectName("starport_desc")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.starport_desc)

        # size, atmosphere, hydrodynamics, temperature
        # population, 



        self.size_lbl = QtWidgets.QLabel(self.overview_page)
        self.size_lbl.setObjectName("size_lbl")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.size_lbl)
        self.size_desc = QtWidgets.QLabel(self.overview_page)
        self.size_desc.setObjectName("size_desc")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.size_desc)

        self.atmo_lbl = QtWidgets.QLabel(self.overview_page)
        self.atmo_lbl.setObjectName("atmo_lbl")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.atmo_lbl)
        self.atmo_desc = QtWidgets.QLabel(self.overview_page)
        self.atmo_desc.setObjectName("atmo_desc")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.atmo_desc)

        self.pressure_lbl = QtWidgets.QLabel(self.overview_page)
        self.pressure_lbl.setObjectName("pressure_lbl")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.pressure_lbl)
        self.pressure_desc = QtWidgets.QLabel(self.overview_page)
        self.pressure_desc.setObjectName("pressure_desc")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pressure_desc)

        self.hydro_lbl = QtWidgets.QLabel(self.overview_page)
        self.hydro_lbl.setObjectName("hydro_lbl")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.hydro_lbl)
        self.hydro_desc = QtWidgets.QLabel(self.overview_page)
        self.hydro_desc.setObjectName("hydro_desc")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.hydro_desc)

        self.temp_lbl = QtWidgets.QLabel(self.overview_page)
        self.temp_lbl.setObjectName("temp_lbl")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.temp_lbl)
        self.tmp_desc = QtWidgets.QLabel(self.overview_page)
        self.tmp_desc.setObjectName("tmp_desc")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.tmp_desc)

        self.pop_lbl = QtWidgets.QLabel(self.overview_page)
        self.pop_lbl.setObjectName("pop_lbl")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.pop_lbl)
        self.pop_desc = QtWidgets.QLabel(self.overview_page)
        self.pop_desc.setObjectName("pop_desc")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.pop_desc)


        self.toolBox.addItem(self.overview_page, "")

        self.verticalLayout.addWidget(self.toolBox)

        self.retranslateUi(Form)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.code_lbl.setText(_translate("Form", "Planetusombo"))
        self.code_lbl_2.setText(_translate("Form", "1010 X-B73A11"))
        self.starport_lbl.setText(_translate("Form", "Starport"))
        self.size_lbl.setText(_translate("Form", "Size"))
        self.atmo_lbl.setText(_translate("Form", "Atmosphere"))
        self.pressure_lbl.setText(_translate("Form", "Pressure"))
        self.hydro_lbl.setText(_translate("Form", "Hydrodynamics"))
        self.pop_lbl.setText(_translate("Form", "Population"))
        self.temp_lbl.setText(_translate("Form", "Temperature"))
        self.starport_desc.setText(_translate("Form", "C - Routine"))

        self.toolBox.setItemText(self.toolBox.indexOf(self.overview_page), _translate("Form", "Overview"))
