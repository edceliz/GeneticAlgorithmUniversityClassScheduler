from PyQt5 import QtCore, QtWidgets
from qt_ui.v1 import Generate as Parent
from components import Database as db
import pickle
from sqlite3 import Binary
from components import ScheduleParser
from numpy import mean
from components.utilities import ResourceTracker
from components.utilities import GeneticAlgorithm
from components.utilities import ScenarioComposer
import copy


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
    topChromosomes = []
    meta = []

    def __init__(self):
        self.dialog = dialog = QtWidgets.QDialog()
        # Initialize custom dialog
        self.parent = parent = Parent.Ui_Dialog()
        # Add parent to custom dialog
        parent.setupUi(dialog)
        dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        self.time = QtCore.QTime(0, 0)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)
        self.running = True
        parent.btnPause.clicked.connect(self.togglePause)
        parent.btnStop.clicked.connect(self.stopOperation)
        self.startWorkers()
        dialog.exec_()

    def togglePause(self):
        self.toggleState()
        self.parent.btnPause.setText('Pause Generation' if self.running else 'Resume Generation')

    def toggleState(self, state=None):
        self.running = (not self.running) if state is None else state
        self.resourceWorker.running = self.running
        self.geneticAlgorithm.running = self.running

    def startWorkers(self):
        self.resourceWorker = ResourceTrackerWorker()
        self.resourceWorker.signal.connect(lambda resource: self.updateResource(resource))
        self.resourceWorker.start()
        composer = ScenarioComposer.ScenarioComposer()
        composer = composer.getScenarioData()
        self.data.update(composer)
        self.geneticAlgorithm = GeneticAlgorithm.GeneticAlgorithm(self.data)
        self.geneticAlgorithm.statusSignal.connect(self.updateStatus)
        self.geneticAlgorithm.detailsSignal.connect(self.updateDetails)
        self.geneticAlgorithm.dataSignal.connect(self.updateView)
        self.geneticAlgorithm.operationSignal.connect(self.updateOperation)
        self.geneticAlgorithm.start()

    def updateStatus(self, status):
        self.parent.lblStatus.setText('Status: {}'.format(status))

    def updateDetails(self, details):
        self.parent.boxGen.setTitle('Generation #{}'.format(details[0]))
        self.parent.lblPopulation.setText('Population: {}'.format(details[1]))
        self.parent.lblMutation.setText('Mutation Rate: {}%'.format(details[2]))
        self.parent.lblFitness.setText('Average Fitness: {}%'.format(details[3]))
        self.parent.lblPreviousFitness.setText('Previous Average Fitness: {}%'.format(details[4]))
        self.parent.lblHighestFitness.setText('Highest Fitness: {}%'.format(details[5]))
        self.parent.lblLowestFitness.setText('Lowest Fitness: {}%'.format(details[6]))

    def updateView(self, chromosomes):
        chromosomes.reverse()
        self.topChromosomes = copy.deepcopy(chromosomes)

    def updateOperation(self, type):
        self.toggleState(False)

    def updateTime(self):
        self.time = self.time.addSecs(1)
        self.parent.lblTime.setText('Elapsed Time: {}'.format(self.time.toString('hh:mm:ss')))

    def stopOperation(self):
        self.toggleState()
        self.resourceWorker.terminate()
        self.geneticAlgorithm.terminate()
        self.timer.stop()
        if len(self.topChromosomes):
            self.parent.btnStop.setText('View Result')
            self.parent.btnStop.clicked.disconnect(self.stopOperation)
            self.parent.btnStop.clicked.connect(self.dialog.close)
            self.parent.lblCPU.setText('CPU Usage: Stopped')
            self.parent.lblMemory.setText('Memory Usage: Stopped')
            self.parent.lblStatus.setText('Status: Stopped')
            self.totalResource['cpu'] = mean(self.totalResource['cpu'])
            self.totalResource['memory'] = mean(self.totalResource['memory'])
            print(self.topChromosomes)
            self.meta = [[chromosome[1], chromosome[0].fitnessDetails] for chromosome in
                         self.topChromosomes]
            print([meta[1] for meta in self.meta])
            conn = db.getConnection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO results (content) VALUES (?)', [Binary(
                pickle.dumps({'data': [chromosome[0].data for chromosome in self.topChromosomes],
                              'meta': self.meta,
                              'time': self.time.toString('hh:mm:ss'), 'resource': self.totalResource,
                              'rawData': self.data},
                             pickle.HIGHEST_PROTOCOL))])
            conn.commit()
            conn.close()
        else:
            self.dialog.close()

    def updateResource(self, resource):
        self.tick += 1
        if self.tick == 3:
            self.tick = 0
        else:
            self.totalResource['cpu'].append(resource[0])
            self.totalResource['memory'].append(resource[1][1])
        self.parent.lblCPU.setText('CPU Usage: {}%'.format(resource[0]))
        self.parent.lblMemory.setText('Memory Usage: {}% - {} MB'.format(resource[1][0], resource[1][1]))


class ResourceTrackerWorker(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)
    running = True

    def __init__(self):
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        while (True):
            self.sleep(1)
            if self.running is True:
                cpu = ResourceTracker.getCPUUsage()
                memory = ResourceTracker.getMemoryUsage()
                memory = [ResourceTracker.getMemoryPercentage(memory), ResourceTracker.byteToMegabyte(memory[0])]
                self.signal.emit([cpu, memory])
