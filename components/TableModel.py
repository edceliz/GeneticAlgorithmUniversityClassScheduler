from PyQt5 import QtCore


# Standard table model requires 2D header and complete dataset
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, header, data):
        super().__init__()
        self.data = data
        self.header = header

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return self.data[index.row()][index.column()]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.data[0])

    def headerData(self, p_int, Qt_Orientation, role=None):
        if Qt_Orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[0][p_int])
        elif Qt_Orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[1][p_int])
        return QtCore.QVariant()

    def setData(self, index, value, role=None):
        if not index.isValid():
            return False
        self.data[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        return True
