from PyQt5 import QtWidgets, QtGui
from qt_ui.v1 import Section as Parent
from components import Timetable
from components import Database as db
from components import Share
import json

class Section:
    def __init__(self, id):
        self.id = id
        self.shareId = []
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
        self.setupSubjects()
        parent.btnFinish.clicked.connect(self.finish)
        parent.btnCancel.clicked.connect(self.dialog.close)
        dialog.exec_()

    def setupSubjects(self):
        self.tree = tree = self.parent.treeSubjects
        self.model = model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['ID', 'Available', 'Shared', 'Subject Code', 'Subject Name', 'Share ID'])
        tree.setModel(model)
        tree.setColumnHidden(0, True)
        tree.setColumnHidden(5, True)
        model.itemChanged.connect(lambda item: self.toggleSharing(item))
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, code FROM subjects')
        subjects = cursor.fetchall()
        currentSubjects = []
        if self.id:
            cursor.execute('SELECT subjects FROM sections WHERE id = ?', [self.id])
            currentSubjects = list(map(lambda id: int(id), json.loads(cursor.fetchall()[0][0])))
        # TODO: Implement shared subjects
        # SHARED SUBJECTS NOT YET SUPPORTED!
        sharedSubjects = []
        # for index in range(currentSubjects):
            # cursor.execute('SELECT id, sections FROM sharings WHERE subjectId = ?', [currentSubjects[index]])
        conn.close()
        for subject in subjects:
            subjectId = QtGui.QStandardItem(str(subject[0]))
            subjectId.setEditable(False)
            availability = QtGui.QStandardItem()
            availability.setCheckable(True)
            availability.setEditable(False)
            availability.setCheckState(2 if subject[0] in currentSubjects else 0)
            shared = QtGui.QStandardItem('')
            shared.setCheckable(True)
            shared.setEditable(False)
            code = QtGui.QStandardItem(subject[2])
            code.setEditable(False)
            name = QtGui.QStandardItem(subject[1])
            name.setEditable(False)
            shareId = QtGui.QStandardItem()
            shareId.setEditable(False)
            model.appendRow([subjectId, availability, shared, code, name, shareId])

    def toggleSharing(self, item):
        if item.column() != 2:
            return False
        subjectId = self.model.data(self.model.index(item.row(), 0))
        shareToggle = self.model.item(item.row(), 2).checkState()
        if shareToggle == 2 and not self.model.item(item.row(), 2).text():
            shareData = Share.Share(subjectId, self.id).getShareData()
            if not shareData[0]:
                return False
            shareId = shareData[0]
            self.shareId.append(shareId)
            self.model.item(item.row(), 5).setText(str(shareId))
            self.model.item(item.row(), 2).setText(shareData[1])
        elif shareToggle == 0 and self.model.item(item.row(), 2).text():
            self.shareId.remove(int(self.model.item(item.row(), 5).text()))
            self.model.item(item.row(), 5).setText('')
            self.model.item(item.row(), 2).setText('')

    def fillForm(self):
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, schedule, stay FROM sections WHERE id = ?', [self.id])
        result = cursor.fetchone()
        conn.close()
        self.parent.lineEditName.setText(str(result[0]))
        self.parent.checkStay.setChecked(result[2])
        self.table = Timetable.Timetable(self.parent.tableSchedule, json.loads(result[1]))

    def finish(self):
        if not self.parent.lineEditName.text():
            return False
        name = self.parent.lineEditName.text()
        stay = 1 if self.parent.checkStay.isChecked() else 0
        schedule = json.dumps(self.table.getData())
        subjects = []
        for row in range(self.model.rowCount()):
            if self.model.item(row, 1).checkState() == 2:
                subjects.append(self.model.item(row, 0).text())
        subjects = json.dumps(subjects)
        # TODO: Add sharing support
        conn = db.getConnection()
        cursor = conn.cursor()
        if self.id:
            # TODO: Add update
            pass
        else:
            cursor.execute('INSERT INTO sections(name, schedule, subjects, stay) VALUES (?, ?, ?, ?)', [name, schedule, subjects, stay])
        conn.commit()
        conn.close()
        self.dialog.close()

class Tree:
    def __init__(self, tree):
        self.tree = tree
        self.model = model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['ID', 'Available', 'Name', 'Stay in Room', 'Operation'])
        tree.setModel(model)
        tree.setColumnHidden(0, True)
        model.itemChanged.connect(lambda item: self.toggleAvailability(item))
        self.display()

    def toggleAvailability(self, item):
        id = self.model.data(self.model.index(item.row(), 0))
        newValue = 1 if item.checkState() == 2 else 0
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('UPDATE sections SET active = ?  WHERE id = ?', [newValue, id])
        conn.commit()
        conn.close()

    def display(self):
        self.model.removeRows(0, self.model.rowCount())
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, active, name, stay FROM sections')
        result = cursor.fetchall()
        conn.close()
        for instr in result:
            id = QtGui.QStandardItem(str(instr[0]))
            id.setEditable(False)
            availability = QtGui.QStandardItem()
            availability.setCheckable(True)
            availability.setCheckState(2 if instr[1] == 1 else 0)
            availability.setEditable(False)
            name = QtGui.QStandardItem(instr[2])
            stay = QtGui.QStandardItem('TRUE' if instr[3] == 1 else 'FALSE')
            stay.setEditable(False)
            name.setEditable(False)
            edit = QtGui.QStandardItem()
            edit.setEditable(False)
            self.model.appendRow([id, availability, name, stay, edit])
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
        Section(id)
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
            cursor.execute('DELETE FROM sections WHERE id = ?', [id])
            conn.commit()
            conn.close()
            self.display()
