from components import Instructor
from components import ResultViewer
from components import Room
from components import ScenarioManager
from components import Section
from components import Subject
from components import Generate
from components.utilities import ImportExportHandler as ioHandler
from qt_ui.v1 import Main
import json
from components import Timetable

class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)
        self.connectButtons()
        self.drawTrees()
        # Tab change listener
        self.tabWidget.currentChanged.connect(self.tabListener)
        # Select default tab index
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

    # Initialize trees and tables
    def drawTrees(self):
        self.instrTree = Instructor.Tree(self.treeInstr)
        self.roomTree = Room.Tree(self.treeRoom)
        self.subjTree = Subject.Tree(self.treeSubj)
        self.secTree = Section.Tree(self.treeSec)
        self.scenTree = ScenarioManager.Tree(self.treeScen)

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

    def tabListener(self):
        self.instrTree.display()
        self.roomTree.display()
        self.subjTree.display()
        self.secTree.display()
        self.scenTree.display()

    def openResult(self):
        ResultViewer.ResultViewer()

    def openGenerate(self):
        Generate.Generate()

    def importInstructors(self):
        instructors = ioHandler.getCSVFile('instructors')
        if instructors:
            instructors.pop(0)
            instructors.pop(0)
            blankSchedule = json.dumps(Timetable.generateRawTable())
            for instructor in instructors:
                Instructor.Instructor.insertInstructor([instructor[0], float(instructor[1]), blankSchedule])
            self.tabListener()

    def importRooms(self):
        rooms = ioHandler.getCSVFile('rooms')
        if rooms:
            rooms.pop(0)
            rooms.pop(0)
            blankSchedule = json.dumps(Timetable.generateRawTable())
            for room in rooms:
                Room.Room.insertRoom([room[0], blankSchedule, room[1]])
            self.tabListener()

    def importSubjects(self):
        subjects = ioHandler.getCSVFile('subjects')
        if subjects:
            subjects.pop(0)
            subjects.pop(0)
            for subject in subjects:
                Subject.Subject.insertSubject([subject[1], float(subject[3]), subject[0], '', json.dumps([]), int(subject[4]), subject[2]])
        self.tabListener()

    def saveAs(self):
        ioHandler.saveAs()

    def load(self):
        ioHandler.load()
        self.tabListener()