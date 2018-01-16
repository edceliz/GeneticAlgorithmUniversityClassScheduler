from qt_ui.v1 import Main
from components import Instructor

class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(parent)
        self.connectButtons()
        self.drawTrees()

    def connectButtons(self):
        self.btnInstrAdd.clicked.connect(Instructor.Instructor)

    def drawTrees(self):
        Instructor.drawTree(self.treeInstr)