from qt_ui.v1 import Main
from components import Instructor
from components import Room
from components import Subject
from components import Section

class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)
        self.connectButtons()
        self.drawTrees()
        self.tabWidget.setCurrentIndex(3)

    # Connect Main component buttons to respective actions
    def connectButtons(self):
        self.btnInstrAdd.clicked.connect(lambda: self.openInstructor())
        self.btnRoomAdd.clicked.connect(lambda: self.openRoom())
        self.btnSubjAdd.clicked.connect(lambda: self.openSubject())
        self.btnSecAdd.clicked.connect(lambda: self.openSection())

    # Initialize trees and tables
    def drawTrees(self):
        self.instrTree = Instructor.Tree(self.treeInstr)
        self.roomTree = Room.Tree(self.treeRoom)
        self.subjTree = Subject.Tree(self.treeSubj)
        self.secTree = Section.Tree(self.treeSec)

    # Open Instructor Edit Modal
    def openInstructor(self, id = False):
        Instructor.Instructor(id)
        self.instrTree.display()

    def openRoom(self, id = False):
        Room.Room(id)
        self.roomTree.display()

    def openSubject(self, id = False):
        Subject.Subject(id)
        self.subjTree.display()

    def openSection(self, id = False):
        Section.Section(id)
        self.secTree.display()