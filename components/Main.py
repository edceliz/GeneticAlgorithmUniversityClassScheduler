from qt_ui.v1 import Main
from components import Instructor

class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)
        self.connectButtons()
        self.drawTrees()

    # Connect Main component buttons to respective actions
    def connectButtons(self):
        self.btnInstrAdd.clicked.connect(lambda: self.openInstructor())

    # Initialize trees and tables
    def drawTrees(self):
        self.instrTree = Instructor.Tree(self.treeInstr)

    # Open Instructor Edit Modal
    def openInstructor(self, id = False):
        Instructor.Instructor(id)
        self.instrTree.display()