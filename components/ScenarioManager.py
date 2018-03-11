from PyQt5 import QtWidgets, QtGui
from components import Database as db
import json

class Tree:
    def __init__(self, tree):
        self.tree = tree
        self.model = model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Sections'])
        tree.setModel(model)
        self.display()

    def display(self):
        # Sections
        # Subjects
        # Rooms + Instructors

        # Clear model
        self.model.removeRows(0, self.model.rowCount())
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, subjects FROM sections WHERE active = 1')
        sections = cursor.fetchall()
        cursor.execute('SELECT id, code, name, type, instructors FROM subjects')
        subjects = cursor.fetchall()
        cursor.execute('SELECT id, name FROM instructors WHERE active = 1')
        instructors = cursor.fetchall()
        conn.close()
        # Convert instructors into dictionary
        instructors = dict(instructors)
        # Convert subjects into dictionary
        subjects = list(map(lambda subject: {subject[0]: subject[1:5]}, subjects))
        subjectDict = {}
        for subject in subjects:
            subjectDict[list(subject.keys())[0]] = list(subject.values())[0]
        subjects = subjectDict
        # Start displaying section information
        for section in sections:
            sectionName = QtGui.QStandardItem(section[0])
            # List section subjects
            for subject in list(map(lambda id: int(id), json.loads(section[1]))):
                sectionSubject = QtGui.QStandardItem(subjects[subject][1])
                # List subject instructors
                subjectInstructors = list(map(lambda id: int(id), json.loads(subjects[subject][3])))
                for instructor in subjectInstructors:
                    if instructor not in instructors:
                        continue
                    sectionSubject.appendRow([QtGui.QStandardItem(instructors[instructor])])
                sectionName.appendRow([sectionSubject])
            self.model.appendRow([sectionName])
        self.tree.expandToDepth(0)