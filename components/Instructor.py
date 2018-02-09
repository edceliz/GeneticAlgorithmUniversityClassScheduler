from PyQt5 import QtWidgets, QtGui
from qt_ui.v1 import Instructor as Parent
from components import Timetable
from components import Database as db
import json

class Instructor:
    def __init__(self, id):
        self.id = id
        # New instance of dialog
        self.dialog = dialog = QtWidgets.QDialog()
        # Initialize custom dialog
        self.parent = parent = Parent.Ui_Dialog()
        # Add parent to custom dialog
        parent.setupUi(dialog)
        # Connect timetable widget with custom timetable model
        if id:
            self.fillForm()
        else:
            self.table = Timetable.Timetable(parent.tableSchedule)
        parent.btnFinish.clicked.connect(self.finish)
        parent.btnCancel.clicked.connect(self.dialog.close)

        dialog.exec_()

    def fillForm(self):
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, hours, schedule FROM instructors WHERE id = ?', [self.id])
        result = cursor.fetchone()
        conn.close()
        self.parent.lineEditName.setText(str(result[0]))
        self.parent.lineEditHours.setText(str(result[1]))
        self.table = Timetable.Timetable(self.parent.tableSchedule, json.loads(result[2]))

    def finish(self):
        if not self.parent.lineEditName.text():
            return False
        name = self.parent.lineEditName.text()
        try:
            hours = int(self.parent.lineEditHours.text())
            if hours <= 0 or hours > 100:
                return False
        except:
            return False
        conn = db.getConnection()
        cursor = conn.cursor()
        if self.id:
            cursor.execute('UPDATE instructors SET name = ?, hours = ?, schedule = ? WHERE id = ?', [name, hours, json.dumps(self.table.getData()), self.id])
        else:
            cursor.execute('INSERT INTO instructors (name, hours, schedule) VALUES (?, ?, ?)', [name, hours, json.dumps(self.table.getData())])
        conn.commit()
        conn.close()
        self.dialog.close()

class Tree:
    def __init__(self, tree):
        self.tree = tree
        self.model = model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['ID', 'Available', 'Name', 'Hours', 'Operation'])
        tree.setModel(model)
        tree.setColumnHidden(0, True)
        model.itemChanged.connect(lambda item: self.toggleAvailability(item))
        self.display()

    def toggleAvailability(self, item):
        id = self.model.data(self.model.index(item.row(), 0))
        newValue = 1 if item.checkState() == 2 else 0
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('UPDATE instructors SET active = ?  WHERE id = ?', [newValue, id])
        conn.commit()
        conn.close()

    def display(self):
        self.model.removeRows(0, self.model.rowCount())
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, active, hours, name FROM instructors')
        result = cursor.fetchall()
        conn.close()
        for instr in result:
            id = QtGui.QStandardItem(str(instr[0]))
            id.setEditable(False)
            availability = QtGui.QStandardItem()
            availability.setCheckable(True)
            availability.setCheckState(2 if instr[1] == 1 else 0)
            availability.setEditable(False)
            hours = QtGui.QStandardItem(str(instr[2]))
            hours.setEditable(False)
            name = QtGui.QStandardItem(instr[3])
            name.setEditable(False)
            edit = QtGui.QStandardItem()
            edit.setEditable(False)
            self.model.appendRow([id, availability, name, hours, edit])
            frameEdit = QtWidgets.QFrame()
            btnEdit = QtWidgets.QPushButton('Edit', frameEdit)
            btnEdit.clicked.connect(lambda state, id = instr[0]: self.edit(id))
            btnDelete = QtWidgets.QPushButton('Delete', frameEdit)
            btnDelete.clicked.connect(lambda state, id = instr[0]: self.delete(id))
            frameLayout = QtWidgets.QHBoxLayout(frameEdit)
            frameLayout.setContentsMargins(0, 0, 0, 0)
            frameLayout.addWidget(btnEdit)
            frameLayout.addWidget(btnDelete)
            self.tree.setIndexWidget(edit.index(), frameEdit)

    def edit(self, id):
        Instructor(id)
        self.display()

    def delete(self, id):
        confirm = QtWidgets.QMessageBox()
        confirm.setIcon(QtWidgets.QMessageBox.Warning)
        confirm.setText('Are you sure you want to delete this entry?')
        confirm.setWindowTitle('Confirm Delete')
        confirm.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        result = confirm.exec_()
        if result == 16384:
            conn = db.getConnection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM instructors WHERE id = ?', [id])
            conn.commit()
            conn.close()
            self.display()
