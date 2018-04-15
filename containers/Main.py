from PyQt5 import QtCore
from containers import Generate, Instructor, ResultViewer, Room, Subject, Section
from components import Settings, Database, Timetable, ImportExportHandler as ioHandler
from py_ui import Main
import json
import gc

class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(parent)
        self.connectButtons()
        self.settings = Settings.getSettings()
        self.loadSettings()
        self.handleSettings()
        self.drawTrees()
        self.tabWidget.currentChanged.connect(self.tabListener)
        self.tabWidget.setCurrentIndex(0)

    # Connect Main component buttons to respective actions
    def connectButtons(self):
        self.btnInstrAdd.clicked.connect(lambda: self.openInstructor())
        self.btnRoomAdd.clicked.connect(lambda: self.openRoom())
        self.btnSubjAdd.clicked.connect(lambda: self.openSubject())
        self.btnSecAdd.clicked.connect(lambda: self.openSection())
        self.btnScenResult.clicked.connect(lambda: self.openResult())
        self.btnScenGenerate.clicked.connect(lambda: self.openGenerate())
        self.btnInstrImport.clicked.connect(self.importInstructors)
        self.btnRoomImport.clicked.connect(self.importRooms)
        self.btnSubjImport.clicked.connect(self.importSubjects)
        self.actionSave_As.triggered.connect(self.saveAs)
        self.actionOpen.triggered.connect(self.load)
        self.actionSettings.triggered.connect(lambda: self.tabWidget.setCurrentIndex(4))
        self.actionExit.triggered.connect(exit)
        self.actionNew.triggered.connect(lambda: self.new())

    # Initialize trees and tables
    def drawTrees(self):
        self.instrTree = Instructor.Tree(self.treeInstr)
        self.roomTree = Room.Tree(self.treeRoom)
        self.subjTree = Subject.Tree(self.treeSubj)
        self.secTree = Section.Tree(self.treeSec)

    # Handle component openings

    def openInstructor(self, id=False):
        Instructor.Instructor(id)
        self.instrTree.display()

    def openRoom(self, id=False):
        Room.Room(id)
        self.roomTree.display()

    def openSubject(self, id=False):
        Subject.Subject(id)
        self.subjTree.display()

    def openSection(self, id=False):
        Section.Section(id)
        self.secTree.display()

    def tabListener(self, index):
        self.instrTree.display()
        self.roomTree.display()
        self.subjTree.display()
        self.secTree.display()
        if index == 4:
            self.checkContents()

    def checkContents(self):
        conn = Database.getConnection()
        cursor = conn.cursor()
        disabled = False
        cursor.execute('SELECT id FROM rooms LIMIT 1')
        if cursor.fetchone():
            disabled = True
        cursor.execute('SELECT id FROM instructors LIMIT 1')
        if cursor.fetchone():
            disabled = True
        cursor.execute('SELECT id FROM sections LIMIT 1')
        if cursor.fetchone():
            disabled = True
        cursor.execute('SELECT id FROM subjects LIMIT 1')
        if cursor.fetchone():
            disabled = True
        self.timeStarting.setDisabled(disabled)
        self.timeEnding.setDisabled(disabled)
        self.btnScenGenerate.setDisabled(not disabled)
        conn.close()

    def openResult(self):
        ResultViewer.ResultViewer()

    def openGenerate(self):
        gc.collect()
        result = Generate.Generate()
        if not len(result.topChromosomes):
            return False
        self.openResult()

    def importInstructors(self):
        instructors = ioHandler.getCSVFile('instructors')
        if instructors:
            instructors.pop(0)
            instructors.pop(0)
            blankSchedule = json.dumps(Timetable.generateRawTable())
            for instructor in instructors:
                Instructor.Instructor.insertInstructor([instructor[0], float(instructor[1]), blankSchedule])
            self.tabListener(0)

    def importRooms(self):
        rooms = ioHandler.getCSVFile('rooms')
        if rooms:
            rooms.pop(0)
            rooms.pop(0)
            blankSchedule = json.dumps(Timetable.generateRawTable())
            for room in rooms:
                Room.Room.insertRoom([room[0], blankSchedule, room[1]])
            self.tabListener(1)

    def importSubjects(self):
        subjects = ioHandler.getCSVFile('subjects')
        if subjects:
            subjects.pop(0)
            subjects.pop(0)
            for subject in subjects:
                Subject.Subject.insertSubject(
                    [subject[1], float(subject[3]), subject[0], '', json.dumps([]), int(subject[4]), subject[2]])
        self.tabListener(2)

    def saveAs(self):
        ioHandler.saveAs()

    def load(self):
        ioHandler.load()
        self.tabWidget.setCurrentIndex(0)
        self.tabListener(0)

    def loadSettings(self):
        self.timeStarting.setTime(QtCore.QTime(int(self.settings['starting_time'] / 2), 0))
        self.timeEnding.setTime(QtCore.QTime(int(self.settings['ending_time'] / 2) + 1, 0))
        if self.settings['lunchbreak']:
            self.radioLunchYes.setChecked(True)
        else:
            self.radioLunchNo.setChecked(True)
        self.editMinPop.setValue(self.settings['minimum_population'])
        self.editMaxPop.setValue(self.settings['maximum_population'])
        self.editMaxGen.setValue(self.settings['maximum_generations'])
        self.editMaxCreation.setValue(self.settings['generation_tolerance'])
        self.editMut.setValue(self.settings['mutation_rate_adjustment_trigger'])
        self.editMaxFit.setValue(self.settings['maximum_fitness'])
        self.editElite.setValue(int(self.settings['elite_percent'] * 100))
        self.editDev.setValue(self.settings['deviation_tolerance'])
        self.matrix = matrix = self.settings['evaluation_matrix']
        self.editSbj.setValue(matrix['subject_placement'])
        self.editLun.setValue(matrix['lunch_break'])
        self.editSec.setValue(matrix['student_rest'])
        self.editIdle.setValue(matrix['idle_time'])
        self.editInstrRest.setValue(matrix['instructor_rest'])
        self.editInstrLoad.setValue(matrix['instructor_load'])
        self.editMeet.setValue(matrix['meeting_pattern'])
        self.matrixSum = sum(matrix.values())
        self.lblTotal.setText('Total: {}%'.format(self.matrixSum))

    # Handle Settings
    def handleSettings(self):
        self.timeStarting.timeChanged.connect(self.handleStartingTime)
        self.timeEnding.timeChanged.connect(self.handleEndingTime)
        self.radioLunchYes.toggled.connect(lambda state: self.updateSettings('lunchbreak', state))
        self.editMinPop.valueChanged.connect(self.handleMinPop)
        self.editMaxPop.valueChanged.connect(self.handleMaxPop)
        self.editMaxGen.valueChanged.connect(lambda value: self.updateSettings('maximum_generations', value))
        self.editMaxCreation.valueChanged.connect(lambda value: self.updateSettings('generation_tolerance', value))
        self.editMut.valueChanged.connect(
            lambda value: self.updateSettings('mutation_rate_adjustment_trigger', round(value, 2)))
        self.editMaxFit.valueChanged.connect(lambda value: self.updateSettings('maximum_fitness', value))
        self.editElite.valueChanged.connect(lambda value: self.updateSettings('elite_percent', round(value / 100, 2)))
        self.editDev.valueChanged.connect(lambda value: self.updateSettings('deviation_tolerance', value))
        self.editSbj.valueChanged.connect(lambda value: self.handleMatrix('subject_placement', value, self.editSbj))
        self.editLun.valueChanged.connect(lambda value: self.handleMatrix('lunch_break', value, self.editLun))
        self.editSec.valueChanged.connect(lambda value: self.handleMatrix('student_rest', value, self.editSec))
        self.editIdle.valueChanged.connect(lambda value: self.handleMatrix('idle_time', value, self.editIdle))
        self.editInstrRest.valueChanged.connect(
            lambda value: self.handleMatrix('instructor_rest', value, self.editInstrRest))
        self.editInstrLoad.valueChanged.connect(
            lambda value: self.handleMatrix('instructor_load', value, self.editInstrLoad))
        self.editMeet.valueChanged.connect(lambda value: self.handleMatrix('meeting_pattern', value, self.editMeet))

    def handleStartingTime(self, time):
        if time.hour() * 2 >= self.settings['ending_time']:
            self.timeStarting.setTime(QtCore.QTime(int(self.settings['starting_time'] / 2), 0))
        else:
            self.updateSettings('starting_time', time.hour() * 2)

    def handleEndingTime(self, time):
        if (time.hour() * 2) - 1 <= self.settings['starting_time']:
            self.timeEnding.setTime(QtCore.QTime(int(self.settings['ending_time'] / 2) + 1, 0))
        else:
            self.updateSettings('ending_time', (time.hour() * 2) - 1)

    def handleMinPop(self, value):
        if value > self.settings['maximum_population']:
            self.editMinPop.setValue(self.settings['minimum_population'])
        else:
            self.updateSettings('minimum_population', value)

    def handleMaxPop(self, value):
        if value < self.settings['minimum_population']:
            self.editMaxPop.setValue(self.settings['maximum_population'])
        else:
            self.updateSettings('maximum_population', value)

    def handleMatrix(self, key, value, obj):
        difference = self.matrix[key] - value
        if self.matrixSum - difference > 100:
            obj.setValue(self.matrix[key])
        else:
            self.updateSettings('evaluation_matrix', value, key)
        self.matrixSum = sum(self.settings['evaluation_matrix'].values())
        self.matrix = self.settings['evaluation_matrix']
        self.lblTotal.setText('Total: {}%'.format(self.matrixSum))

    def updateSettings(self, key, value, secondKey=False):
        Settings.setSettings(key, value, secondKey)
        self.settings = Settings.getSettings()

    def new(self):
        ioHandler.removeTables()
        Database.setup()
        self.tabListener(0)
