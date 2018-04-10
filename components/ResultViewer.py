from PyQt5 import QtWidgets, QtGui
from components import Database as db
import pickle
import copy
from qt_ui.v1 import Result as Parent
from components import ScheduleParser

class ResultViewer:
    def __init__(self, result):
        self.result = result
        self.dialog = dialog = QtWidgets.QDialog()
        # Initialize custom dialog
        self.parent = parent = Parent.Ui_Dialog()
        # Add parent to custom dialog
        parent.setupUi(dialog)
        self.run = True
        if not len(self.result['data']):
            self.getLastResult()
        self.parseResultDetails()
        self.connectWidgets()
        self.table = table = self.parent.tableResult
        self.updateTable(0)
        if self.run:
            dialog.exec_()

    def getLastResult(self):
        conn = db.getConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM results WHERE id = (SELECT MAX(id) FROM results)')
        result = cursor.fetchone()
        conn.close()
        if result:
            self.result = pickle.loads(result[0])
        else:
            messageBox = QtWidgets.QMessageBox()
            messageBox.setWindowTitle('No Data')
            messageBox.setIcon(QtWidgets.QMessageBox.Information)
            messageBox.setText('You haven\'t generated a solution yet!')
            messageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            messageBox.exec_()
            self.run = False

    def parseResultDetails(self):
        if not len(self.result['data']):
            return False
        result = self.result
        self.rawData = copy.deepcopy(result['rawData'])
        self.parent.lblTime.setText('Generation Time: {}'.format(result['time']))
        self.parent.lblCPU.setText('Average CPU Usage: {}%'.format(round(result['resource']['cpu']), 2))
        self.parent.lblMemory.setText('Average Mem Usage: {} MB'.format(round(result['resource']['memory']), 2))
        self.updateEntries(0)
        self.updateDetails(0)

    def connectWidgets(self):
        self.parent.cmbChromosome.currentIndexChanged.connect(self.updateDetails)
        self.parent.cmbCategory.currentIndexChanged.connect(self.updateEntries)
        self.parent.cmbEntry.currentIndexChanged.connect(self.updateTable)

    def updateDetails(self, index):
        parent = self.parent
        meta = self.result['meta'][index]
        parent.lblFit.setText('Total Fitness: {}%'.format(meta[0]))
        parent.lblSbj.setText('Subject Placement: {}%'.format(meta[1][0]))
        parent.lblSecRest.setText('Section Rest: {}%'.format(meta[1][2]))
        parent.lblSecIdle.setText('Section Idle Time: {}%'.format(meta[1][4]))
        parent.lblInstrRest.setText('Instructor Rest: {}%'.format(meta[1][3]))
        parent.lblInstrLoad.setText('Instructor Load: {}%'.format(meta[1][6]))
        parent.lblLunch.setText('Lunch Break: {}%'.format(meta[1][1]))
        parent.lblMeet.setText('Meeting Pattern: {}%'.format(meta[1][5]))
        parent.cmbCategory.setCurrentIndex(0)
        parent.cmbEntry.setCurrentIndex(0)

    def updateEntries(self, index):
        if index == 0:
            key = 'sections'
        elif index == 1:
            key = 'rooms'
        else:
            key = 'instructors'
        self.parent.cmbEntry.clear()
        for entry in self.rawData[key].values():
            self.parent.cmbEntry.addItem(entry[0])

    def updateTable(self, index):
        # TODO: Render table based on category and entry
        self.loadTable([{'color': None, 'text': '', 'instances': [[index, 0, 3]]}])

    def loadTable(self, data = []):
        self.table.reset()
        self.table.clearSpans()
        ScheduleParser.ScheduleParser(self.table, data)