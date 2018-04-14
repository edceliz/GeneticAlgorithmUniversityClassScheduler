# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'room.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(716, 553)
        Dialog.setMinimumSize(QtCore.QSize(716, 553))
        Dialog.setMaximumSize(QtCore.QSize(716, 553))
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setObjectName("gridLayout")
        self.lblName = QtWidgets.QLabel(Dialog)
        self.lblName.setObjectName("lblName")
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.lineEditName = QtWidgets.QLineEdit(Dialog)
        self.lineEditName.setObjectName("lineEditName")
        self.gridLayout.addWidget(self.lineEditName, 0, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioLec = QtWidgets.QRadioButton(self.groupBox)
        self.radioLec.setObjectName("radioLec")
        self.horizontalLayout_2.addWidget(self.radioLec)
        self.radioLab = QtWidgets.QRadioButton(self.groupBox)
        self.radioLab.setObjectName("radioLab")
        self.horizontalLayout_2.addWidget(self.radioLab)
        self.gridLayout.addWidget(self.groupBox, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tableSchedule = QtWidgets.QTableView(Dialog)
        self.tableSchedule.setObjectName("tableSchedule")
        self.verticalLayout.addWidget(self.tableSchedule)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnFinish = QtWidgets.QPushButton(Dialog)
        self.btnFinish.setObjectName("btnFinish")
        self.horizontalLayout.addWidget(self.btnFinish)
        self.btnCancel = QtWidgets.QPushButton(Dialog)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Room"))
        self.lblName.setText(_translate("Dialog", "Name"))
        self.groupBox.setTitle(_translate("Dialog", "Type"))
        self.radioLec.setText(_translate("Dialog", "Lecture"))
        self.radioLab.setText(_translate("Dialog", "Laboratory"))
        self.btnFinish.setText(_translate("Dialog", "Finish"))
        self.btnCancel.setText(_translate("Dialog", "Cancel"))
