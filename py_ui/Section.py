# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'section2.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(716, 553)
        Dialog.setMinimumSize(QtCore.QSize(731, 553))  # 553
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 697, 759))  # 697
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 9, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.lblName = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.lblName.setObjectName("lblName")
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lineEditName = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.lineEditName.setObjectName("lineEditName")
        self.gridLayout.addWidget(self.lineEditName, 1, 1, 1, 1)
        self.checkStay = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.checkStay.setObjectName("checkStay")
        self.gridLayout.addWidget(self.checkStay, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.treeSubjects = QtWidgets.QTreeView(self.scrollAreaWidgetContents)
        self.treeSubjects.setMinimumSize(QtCore.QSize(0, 200))
        self.treeSubjects.setHeaderHidden(False)
        self.treeSubjects.setObjectName("treeSubjects")
        self.verticalLayout.addWidget(self.treeSubjects)
        self.tableSchedule = QtWidgets.QTableView(self.scrollAreaWidgetContents)
        self.tableSchedule.setMinimumSize(QtCore.QSize(0, 476))
        self.tableSchedule.setObjectName("tableSchedule")
        self.verticalLayout.addWidget(self.tableSchedule)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnFinish = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.btnFinish.setObjectName("btnFinish")
        self.horizontalLayout_2.addWidget(self.btnFinish)
        self.btnCancel = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.lblName.setText(_translate("Dialog", "Name"))
        self.checkStay.setText(_translate("Dialog", "Stay in Room"))
        self.btnFinish.setText(_translate("Dialog", "Finish"))
        self.btnCancel.setText(_translate("Dialog", "Cancel"))
