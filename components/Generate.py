from PyQt5 import QtCore, QtWidgets, QtGui
from qt_ui.v1 import Generate as Parent
from components import Database as db
import json
from components import ScheduleParser
from components.utilities import ResourceTracker
from components.utilities import GeneticAlgorithm
from components.utilities import ScenarioComposer

class Generate:
    totalResource = {
        'cpu': [],
        'memory': []
    }
    tick = 0
    data = {
        'results': [],
        'rooms': [],
        'instructors': [],
        'sections': [],
        'sharings': [],
        'subjects': []
    }

    def __init__(self):
        self.dialog = dialog = QtWidgets.QDialog()
        # Initialize custom dialog
        self.parent = parent = Parent.Ui_Dialog()
        # Add parent to custom dialog
        parent.setupUi(dialog)
        self.running = True
        parent.btnPause.clicked.connect(self.togglePause)
        self.startWorkers()
        dialog.exec_()

    def togglePause(self):
        self.toggleState()
        self.parent.btnPause.setText('Pause Generation' if self.running else 'Resume Generation')

    def toggleState(self):
        self.running = not self.running
        if self.running:
            self.resourceWorker.running = True
        else:
            self.resourceWorker.running = False

    def startWorkers(self):
        self.resourceWorker = ResourceTrackerWorker()
        self.resourceWorker.signal.connect(lambda resource: self.updateResource(resource))
        self.resourceWorker.start()
        composer = ScenarioComposer.ScenarioComposer()
        composer = composer.getScenarioData()
        self.data.update(composer)
        self.geneticAlgorithm = GeneticAlgorithm.GeneticAlgorithm(self.data)
        # self.geneticAlgorithm.start()

    def updateResource(self, resource):
        self.tick += 1
        if self.tick == 3:
            self.tick = 0
        else:
            self.totalResource['cpu'].append(resource[0])
            self.totalResource['memory'].append(resource[1][1])
        self.parent.lblCPU.setText('CPU Usage: {}%'.format(resource[0]))
        self.parent.lblMemory.setText('Memory Usage: {}% - {} MB'.format(resource[1][0], resource[1][1]))

    def cleanDatabase(self):
        conn = db.getConnection()
        cursor = conn.cursor()
        # PENDING WORK
        conn.commit()
        conn.close()

    def setupRooms(self):
        pass

class ResourceTrackerWorker(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)
    running = True

    def __init__(self):
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        while(True):
            self.sleep(1)
            if self.running is True:
                cpu = ResourceTracker.getCPUUsage()
                memory = ResourceTracker.getMemoryUsage()
                memory = [ResourceTracker.getMemoryPercentage(memory), ResourceTracker.byteToMegabyte(memory[0])]
                self.signal.emit([cpu, memory])