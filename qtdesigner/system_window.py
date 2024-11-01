# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'system_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(759, 516)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.system_label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(False)
        font.setUnderline(False)
        self.system_label.setFont(font)
        self.system_label.setAlignment(QtCore.Qt.AlignCenter)
        self.system_label.setObjectName("system_label")
        self.verticalLayout.addWidget(self.system_label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.toolBox = QtWidgets.QToolBox(Dialog)
        self.toolBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 200, 345))
        self.page.setObjectName("page")
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 200, 345))
        self.page_2.setObjectName("page_2")
        self.toolBox.addItem(self.page_2, "")
        self.horizontalLayout.addWidget(self.toolBox)
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.diagButtonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.diagButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.diagButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.diagButtonBox.setObjectName("diagButtonBox")
        self.verticalLayout.addWidget(self.diagButtonBox)

        self.retranslateUi(Dialog)
        self.toolBox.setCurrentIndex(1)
        self.diagButtonBox.accepted.connect(Dialog.accept) # type: ignore
        self.diagButtonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.system_label.setText(_translate("Dialog", "The Template Name System"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Dialog", "Page 1"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("Dialog", "Page 2"))
