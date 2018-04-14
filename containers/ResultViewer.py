from PyQt5 import QtWidgets
from components import Settings, Database as db, ScheduleParser
from py_ui import Result as Parent
import pickle
import json
import csv
import copy


class ResultViewer:
    def __init__(self):
        self.dialog = dialog = QtWidgets.QDialog()
        # Initialize custom dialog
        self.parent = parent = Parent.Ui_Dialog()
        # Add parent to custom dialog
        parent.setupUi(dialog)
        self.table = self.parent.tableResult
        self.run = True
        self.settings = Settings.getSettings()
        self.result = { 'data': [] }
        self.getLastResult()
        if self.run:
            self.parseResultDetails()
            self.connectWidgets()
            self.updateTable(0)
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
        self.parent.btnExport.clicked.connect(self.export)

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
        self.updateEntries(0)
        self.updateTable(0)

    def updateEntries(self, index):
        if index == 0:
            key = 'sections'
        elif index == 1:
            key = 'rooms'
        else:
            key = 'instructors'
        self.entryKeys = []
        self.changingKeys = True
        self.parent.cmbEntry.clear()
        for id, entry in self.rawData[key].items():
            self.entryKeys.append(id)
            self.parent.cmbEntry.addItem(entry[0])
        self.changingKeys = False
        self.updateTable(self.parent.cmbEntry.currentIndex())

    def updateTable(self, index):
        if self.changingKeys:
            return False
        chromosome = self.result['data'][self.parent.cmbChromosome.currentIndex()]
        category = self.parent.cmbCategory.currentIndex()
        # {secId: {'details': {sbjId: [roomId, instructorId, [day/s], startingTS, length]}}}
        sections = chromosome['sections']
        rawData = self.rawData
        data = []
        # Section
        if category == 0:
            subjects = sections[self.entryKeys[index]]['details']
            for subject, details in subjects.items():
                if not len(details):
                    continue
                instructor = '' if not details[1] else rawData['instructors'][details[1]][0]
                data.append({'color': None, 'text': '{} \n {} \n {}'.format(rawData['subjects'][subject][2],
                                                                            rawData['rooms'][details[0]][0],
                                                                            instructor),
                             'instances': [[day, details[3], details[3] + details[4]] for day in details[2]]})
        # Room
        elif category == 1:
            for section, details in sections.items():
                for subject, subjectDetail in details['details'].items():
                    if not len(subjectDetail):
                        continue
                    if subjectDetail[0] != self.entryKeys[index]:
                        continue
                    instructor = '' if not subjectDetail[1] else rawData['instructors'][subjectDetail[1]][0]
                    data.append({'color': None, 'text': '{} \n {} \n {}'.format(rawData['subjects'][subject][2],
                                                                                rawData['sections'][section][0],
                                                                                instructor),
                                 'instances': [[day, subjectDetail[3], subjectDetail[3] + subjectDetail[4]] for day in
                                               subjectDetail[2]]})
        # Instructor
        else:
            for section, details in sections.items():
                for subject, subjectDetail in details['details'].items():
                    if not len(subjectDetail):
                        continue
                    if subjectDetail[1] != self.entryKeys[index]:
                        continue
                    data.append({'color': None, 'text': '{} \n {} \n {}'.format(rawData['subjects'][subject][2],
                                                                                rawData['rooms'][subjectDetail[0]][0],
                                                                                rawData['sections'][section][0]),
                                 'instances': [[day, subjectDetail[3], subjectDetail[3] + subjectDetail[4]] for day in
                                               subjectDetail[2]]})
        self.loadTable(data)

    def loadTable(self, data=[]):
        self.table.reset()
        self.table.clearSpans()
        ScheduleParser.ScheduleParser(self.table, data)

    def export(self):
        directory = QtWidgets.QFileDialog().getExistingDirectory(None, 'Select Directory for Export')
        if not directory:
            return False
        with open('timeslots.json') as json_file:
            timeslots = json.load(json_file)['timeslots']
        fieldnames = ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        rawData = self.rawData
        chromosome = self.result['data'][self.parent.cmbChromosome.currentIndex()]
        # Create schedule for sections
        with open('{}/sections_schedule.csv'.format(directory), 'w', newline='') as file:
            writer = csv.writer(file, dialect='excel')
            for section, subjects in chromosome['sections'].items():
                writer.writerow([self.rawData['sections'][section][0]])
                writer.writerow(fieldnames)
                schedule = [['' for j in range(6)] for i in
                            range(self.settings['ending_time'] - self.settings['starting_time'] + 1)]
                for subject, details in subjects['details'].items():
                    if not len(details):
                        continue
                    instructor = '' if not details[1] else rawData['instructors'][details[1]][0]
                    for timeslot in range(details[3], details[3] + details[4]):
                        for day in details[2]:
                            schedule[timeslot][day] = '{} - {} - {}'.format(rawData['subjects'][subject][2],
                                                                            rawData['rooms'][details[0]][0],
                                                                            instructor)
                for timeslot in range(self.settings['starting_time'], self.settings['ending_time'] + 1):
                    writer.writerow([timeslots[timeslot], *schedule[timeslot - self.settings['starting_time']]])
                writer.writerow([''])
        # Create schedule for instructors
        with open('{}/instructors_schedule.csv'.format(directory), 'w', newline='') as file:
            writer = csv.writer(file, dialect='excel')
            for instructor in rawData['instructors'].keys():
                writer.writerow([rawData['instructors'][instructor][0]])
                writer.writerow(fieldnames)
                schedule = [['' for j in range(6)] for i in
                            range(self.settings['ending_time'] - self.settings['starting_time'] + 1)]
                for section, subjects in chromosome['sections'].items():
                    for subject, details in subjects['details'].items():
                        if not len(details) or details[1] != instructor:
                            continue
                        for timeslot in range(details[3], details[3] + details[4]):
                            for day in details[2]:
                                schedule[timeslot][day] = '{} - {} - {}'.format(rawData['subjects'][subject][2],
                                                                                rawData['rooms'][details[0]][0],
                                                                                rawData['sections'][section][0])
                    for timeslot in range(self.settings['starting_time'], self.settings['ending_time'] + 1):
                        writer.writerow([timeslots[timeslot], *schedule[timeslot - self.settings['starting_time']]])
                writer.writerow([''])
        # Create schedule for rooms
        with open('{}/rooms_schedule.csv'.format(directory), 'w', newline='') as file:
            writer = csv.writer(file, dialect='excel')
            for room in rawData['rooms'].keys():
                writer.writerow([rawData['rooms'][room][0]])
                writer.writerow(fieldnames)
                schedule = [['' for j in range(6)] for i in
                            range(self.settings['ending_time'] - self.settings['starting_time'] + 1)]
                for section, subjects in chromosome['sections'].items():
                    for subject, details in subjects['details'].items():
                        if not len(details) or details[0] != room:
                            continue
                        instructor = '' if not details[1] else rawData['instructors'][details[1]][0]
                        for timeslot in range(details[3], details[3] + details[4]):
                            for day in details[2]:
                                schedule[timeslot][day] = '{} - {} - {}'.format(rawData['subjects'][subject][2],
                                                                                rawData['sections'][section][0],
                                                                                instructor)
                for timeslot in range(self.settings['starting_time'], self.settings['ending_time'] + 1):
                    writer.writerow([timeslots[timeslot], *schedule[timeslot - self.settings['starting_time']]])
                writer.writerow([''])
