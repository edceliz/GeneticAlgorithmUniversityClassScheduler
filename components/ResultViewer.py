from PyQt5 import QtWidgets, QtGui
from components import Database as db
import json
from qt_ui.v1 import Result as Parent
from components import ScheduleParser

class ResultViewer:
    def __init__(self):
        self.dialog = dialog = QtWidgets.QDialog()
        # Initialize custom dialog
        self.parent = parent = Parent.Ui_Dialog()
        # Add parent to custom dialog
        parent.setupUi(dialog)
        self.table = table = self.parent.tableSchedule
        self.loadTable()
        dialog.exec_()

    def loadTable(self, data = []):
        ScheduleParser.ScheduleParser(self.table, data)