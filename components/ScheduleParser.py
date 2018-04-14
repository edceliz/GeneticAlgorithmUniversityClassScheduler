from PyQt5 import QtCore, QtWidgets, QtGui
from components import Settings, TableModel, Utilities
import json


class ScheduleParser:
    # Section / Room View
    # Subject Name + Instructor
    # Instructor View
    # Subject Name + Instructor + Section

    # table = QTableView, data = []
    def __init__(self, table, data):
        self.table = table
        header = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']]
        with open('timeslots.json') as json_file:
            self.timeslots = timeslots = json.load(json_file)['timeslots']
        self.settings = settings = Settings.getSettings()
        header.append(timeslots[settings['starting_time']:settings['ending_time'] + 1])
        temporaryData = []
        for i in range(settings['ending_time'] + 1 - settings['starting_time']):
            temporaryData.append(['', '', '', '', '', ''])
        self.model = ScheduleParserModel(header, temporaryData)
        table.setModel(self.model)
        table.setFocusPolicy(QtCore.Qt.NoFocus)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.parseData(data)

    # data = [{'color': None, 'text': '', 'instances': [[day, startingTS, endingTS]]}]
    def parseData(self, data):
        view = self.table
        model = self.model
        for entry in data:
            entry['color'] = Utilities.colorGenerator()
            for instance in entry['instances']:
                index = model.index(instance[1], instance[0])
                view.setSpan(instance[1], instance[0], instance[2] - instance[1], 1)
                item = QtGui.QStandardItem(entry['text'])
                item.setBackground(QtGui.QBrush(QtGui.QColor(*entry['color'])))
                item.setForeground(QtGui.QBrush(QtGui.QColor(*Utilities.textColor(entry['color']))))
                model.setData(index, item)

    def subjectGenerator(self):
        print(self.settings['starting_time'])


class ScheduleParserModel(TableModel.TableModel):
    def __init__(self, header, data):
        super().__init__(header, data)

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False
        elif role is None:
            self.data[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def data(self, index, role):
        if not index.isValid() or not self.data[index.row()][index.column()]:
            return QtCore.QVariant()
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        elif role == QtCore.Qt.BackgroundRole:
            return self.data[index.row()][index.column()].background()
        elif role == QtCore.Qt.ForegroundRole:
            return self.data[index.row()][index.column()].foreground()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return self.data[index.row()][index.column()].text()
