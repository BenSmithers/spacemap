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

        """
        add labels for Person birthday, attributes, profession, skills, hair, eyes, etc

        Text should wrap rather than extend off the side of the dialog
        """ 
        self.birthday_lbl = QtWidgets.QLabel(Form)
        self.birthday_lbl.setObjectName("birthday_lbl")
        self.birthday_lbl.setText("Birthday: ")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.birthday_lbl)
        self.birthday_val = QtWidgets.QLabel(Form)
        self.birthday_val.setObjectName("birthday_val")
        self.birthday_val.setText("2500-01-01")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.birthday_val)  

        self.attributes_lbl = QtWidgets.QLabel(Form) 
        self.attributes_lbl.setObjectName("attributes_lbl")
        self.attributes_lbl.setText("Attributes: ")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.attributes_lbl)
        self.attributes_val = QtWidgets.QLabel(Form)
        self.attributes_val.setObjectName("attributes_val")
        self.attributes_val.setText("STR 10, DEX 10, END 10, INT 10, EDU 10, SOC 10")
        # enable wrap
        self.attributes_val.setWordWrap(True)
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.attributes_val)

        self.profession_lbl = QtWidgets.QLabel(Form) 
        self.profession_lbl.setObjectName("profession_lbl")
        self.profession_lbl.setText("Profession: ")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.profession_lbl)
        self.profession_val = QtWidgets.QLabel(Form)
        self.profession_val.setObjectName("profession_val")
        self.profession_val.setText("Merchant")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.profession_val)    

        self.skills_lbl = QtWidgets.QLabel(Form) 
        self.skills_lbl.setObjectName("skills_lbl")
        self.skills_lbl.setText("Skills: ") 
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.skills_lbl)
        self.skills_val = QtWidgets.QLabel(Form)
        self.skills_val.setObjectName("skills_val")
        self.skills_val.setText("Pilot 2, Trade 1, ...")
        self.skills_lbl.setWordWrap(True)
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.skills_val)    
        self.hair_lbl = QtWidgets.QLabel(Form) 
        self.hair_lbl.setObjectName("hair_lbl")
        self.hair_lbl.setText("Hair: ")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.hair_lbl)
        self.hair_val = QtWidgets.QLabel(Form)
        self.hair_val.setObjectName("hair_val")
        self.hair_val.setText("Brown, Short, Straight")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.hair_val)    
        self.eyes_lbl = QtWidgets.QLabel(Form) 
        self.eyes_lbl.setObjectName("eyes_lbl")
        self.eyes_lbl.setText("Eyes: ")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.eyes_lbl)
        self.eyes_val = QtWidgets.QLabel(Form)
        self.eyes_val.setObjectName("eyes_val")
        self.eyes_val.setText("Brown")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.eyes_val)
        
        self.wants_lbl = QtWidgets.QLabel(Form) 
        self.wants_lbl.setObjectName("wants_lbl")
        self.wants_lbl.setText("Wants: ")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.wants_lbl)
        self.wants_val = QtWidgets.QLabel(Form)
        self.wants_val.setObjectName("wants_val")
        self.wants_val.setText("Food, Medicine, Technology")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.wants_val) 

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(8, QtWidgets.QFormLayout.SpanningRole, self.label_2)


        self.formLayout_2.setWidget(9, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)
        

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.name_lbl.setText(_translate("Form", "Frank Frankovich (he/him)"))
        
        self.label_2.setText(_translate("Form", ""))
