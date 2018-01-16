# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'section.ui'
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
        self.lineEditName = QtWidgets.QLineEdit(Dialog)
        self.lineEditName.setObjectName("lineEditName")
        self.gridLayout.addWidget(self.lineEditName, 1, 1, 1, 1)
        self.lblName = QtWidgets.QLabel(Dialog)
        self.lblName.setObjectName("lblName")
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblOJT = QtWidgets.QLabel(Dialog)
        self.lblOJT.setObjectName("lblOJT")
        self.gridLayout.addWidget(self.lblOJT, 1, 2, 1, 1)
        self.radioYes = QtWidgets.QRadioButton(Dialog)
        self.radioYes.setObjectName("radioYes")
        self.gridLayout.addWidget(self.radioYes, 1, 3, 1, 1)
        self.radioNo = QtWidgets.QRadioButton(Dialog)
        self.radioNo.setObjectName("radioNo")
        self.gridLayout.addWidget(self.radioNo, 1, 4, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.treeSubjects = QtWidgets.QTreeView(Dialog)
        self.treeSubjects.setObjectName("treeSubjects")
        self.verticalLayout.addWidget(self.treeSubjects)
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
        Dialog.setWindowTitle(_translate("Dialog", "Section"))
        self.lblName.setText(_translate("Dialog", "Name"))
        self.lblOJT.setText(_translate("Dialog", "OJT"))
        self.radioYes.setText(_translate("Dialog", "Yes"))
        self.radioNo.setText(_translate("Dialog", "No"))
        self.btnFinish.setText(_translate("Dialog", "Finish"))
        self.btnCancel.setText(_translate("Dialog", "Cancel"))

