# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'instructor.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(716, 553)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(716, 553))
        Dialog.setMaximumSize(QtCore.QSize(716, 553))
        Dialog.setFocusPolicy(QtCore.Qt.NoFocus)
        Dialog.setModal(False)
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
        self.lblHours = QtWidgets.QLabel(Dialog)
        self.lblHours.setObjectName("lblHours")
        self.gridLayout.addWidget(self.lblHours, 0, 2, 1, 1)
        self.lineEditHours = QtWidgets.QLineEdit(Dialog)
        self.lineEditHours.setObjectName("lineEditHours")
        self.gridLayout.addWidget(self.lineEditHours, 0, 3, 1, 1)
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
        Dialog.setWindowTitle(_translate("Dialog", "Instructor"))
        self.lblName.setText(_translate("Dialog", "Name"))
        self.lblHours.setText(_translate("Dialog", "Available Hours"))
        self.btnFinish.setText(_translate("Dialog", "Finish"))
        self.btnCancel.setText(_translate("Dialog", "Cancel"))
