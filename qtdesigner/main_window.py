# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1045, 748)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("the vertical layout")
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(500, 16777215))
        self.tabWidget.setObjectName("tabWidget")
  

        #self.tabWidget.addTab(self.trade_tab, "")
  


        #self.tabWidget.addTab(self.pass_tab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.map_view = QtWidgets.QGraphicsView(self.centralwidget)
        #self.map_view.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black))
        self.map_view.setObjectName("map_view")
        self.horizontalLayout.addWidget(self.map_view)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1045, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #.tabWidget.setTabText(self.tabWidget.indexOf(self.trade_tab), _translate("MainWindow", "Trade"))
        #self.tabWidget.setTabText(self.tabWidget.indexOf(self.pass_tab), _translate("MainWindow", "Passengers"))
