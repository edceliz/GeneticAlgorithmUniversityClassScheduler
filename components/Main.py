import psutil
import time
from PyQt5 import QtCore

from components import Instructor
from components import ResultViewer
from components import Room
from components import ScenarioManager
from components import Section
from components import Subject
from qt_ui.v1 import Main


class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)
        self.connectButtons()
        self.drawTrees()
        # Tab change listener
        self.tabWidget.currentChanged.connect(lambda idx: self.tabListener(idx))
        # Select default tab index
        self.tabWidget.setCurrentIndex(4)

    # Connect Main component buttons to respective actions
    def connectButtons(self):
        self.btnInstrAdd.clicked.connect(lambda: self.openInstructor())
        self.btnRoomAdd.clicked.connect(lambda: self.openRoom())
        self.btnSubjAdd.clicked.connect(lambda: self.openSubject())
        self.btnSecAdd.clicked.connect(lambda: self.openSection())
        self.btnScenResult.clicked.connect(lambda: self.openResult())
        self.btnScenGenerate.clicked.connect(lambda: self.openGenerate())

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

    def tabListener(self, index):
        if index == 4:
            self.scenTree.display()

    def openResult(self):
        ResultViewer.ResultViewer()

    def openGenerate(self):
        pass