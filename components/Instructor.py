from PyQt5 import QtWidgets, QtGui
from qt_ui.v1 import Instructor as Parent

class Instructor():
    def __init__(self, id = False):
        dialog = QtWidgets.QDialog()
        parent = Parent.Ui_Dialog()
        parent.setupUi(dialog)
        dialog.exec_()
        if id:
            self.fillForm(id)

    def fillForm(self, id):
        pass

def drawTree(tree):
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(['Available', 'Name', 'Hours', 'Edit'])
    tree.setModel(model)