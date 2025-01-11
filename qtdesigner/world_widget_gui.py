# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'world_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(327, 458)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.titleLayout.setObjectName("titleLayout")
        self.world_image = QtWidgets.QLabel(Form)
        self.world_image.setMaximumSize(QtCore.QSize(100, 100))
        self.world_image.setText("")
        #self.world_image.setPixmap(QtGui.QPixmap("../../spacemap/images/planets/RClassD1.png"))
        self.world_image.setScaledContents(True)
        self.world_image.setObjectName("world_image")
        self.titleLayout.addWidget(self.world_image)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.name_lbl = QtWidgets.QLabel(Form)
        self.name_lbl.setMaximumSize(QtCore.QSize(16777215, 50))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.name_lbl.setFont(font)
        self.name_lbl.setObjectName("name_lbl")
        self.verticalLayout_3.addWidget(self.name_lbl)
        self.desc_layout = QtWidgets.QLabel(Form)
        self.desc_layout.setMaximumSize(QtCore.QSize(16777215, 50))
        self.desc_layout.setObjectName("desc_layout")
        self.verticalLayout_3.addWidget(self.desc_layout)
        self.titleLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.titleLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
    

        self.size_lbl = QtWidgets.QLabel(Form)
        self.size_lbl.setObjectName("size_lbl")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.size_lbl)
        self.size_desc = QtWidgets.QLabel(Form)
        self.size_desc.setObjectName("size_desc")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.size_desc)

        self.atmo_lbl = QtWidgets.QLabel(Form)
        self.atmo_lbl.setObjectName("atmo_lbl")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.atmo_lbl)
        self.atmo_desc = QtWidgets.QLabel(Form)
        self.atmo_desc.setObjectName("atmo_desc")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.atmo_desc)

        self.pressure_lbl = QtWidgets.QLabel(Form)
        self.pressure_lbl.setObjectName("pressure_lbl")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.pressure_lbl)
        self.pressure_desc = QtWidgets.QLabel(Form)
        self.pressure_desc.setObjectName("pressure_desc")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pressure_desc)

        self.hydro_lbl = QtWidgets.QLabel(Form)
        self.hydro_lbl.setObjectName("hydro_lbl")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.hydro_lbl)
        self.hydro_desc = QtWidgets.QLabel(Form)
        self.hydro_desc.setObjectName("hydro_desc")
        #self.hydro_desc.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred, )
        #self.hydro_desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.hydro_desc.setWordWrap(True)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.hydro_desc)

        self.temp_lbl = QtWidgets.QLabel(Form)
        self.temp_lbl.setObjectName("temp_lbl")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.temp_lbl)
        self.tmp_desc = QtWidgets.QLabel(Form)
        self.tmp_desc.setObjectName("tmp_desc")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.tmp_desc)

        self.pop_lbl = QtWidgets.QLabel(Form)
        self.pop_lbl.setObjectName("pop_lbl")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.pop_lbl)
        self.pop_desc = QtWidgets.QLabel(Form)
        self.pop_desc.setObjectName("pop_desc")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.pop_desc)

        self.tech_lbl = QtWidgets.QLabel(Form)
        self.tech_lbl.setObjectName("tech_lbl")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.tech_lbl)
        self.tech_desc = QtWidgets.QLabel(Form)
        self.tech_desc.setObjectName("tech_desc")
        self.tech_desc.setWordWrap(True)
        
        #self.tech_desc.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred, )
        #self.tech_desc.setAlignment(QtCore.Qt.AlignTop)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.tech_desc)



        self.verticalLayout_2.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.name_lbl.setText(_translate("Form", "Servolos III"))
        self.desc_layout.setText(_translate("Form", "A112LE"))