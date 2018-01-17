from PyQt5 import QtWidgets, QtGui
from qt_ui.v1 import Instructor as Parent
from components import Timetable

class Instructor():
    def __init__(self, id = False):
        dialog = QtWidgets.QDialog()
        parent = Parent.Ui_Dialog()
        parent.setupUi(dialog)
        table = Timetable.Timetable(parent.tableSchedule)
        if id:
            self.fillForm(id)
        dialog.exec_()

    def fillForm(self, id):
        pass

def drawTree(tree):
    model = QtGui.QStandardItemModel()
    model.setHorizontalHeaderLabels(['ID', 'Available', 'Name', 'Hours', 'Edit'])
    tree.setModel(model)
    tree.setColumnHidden(0, True)
