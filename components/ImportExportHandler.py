from PyQt5 import QtWidgets
from components import Database as db
import csv


def getCSVFile(type):
    fileName = QtWidgets.QFileDialog().getOpenFileName(None, 'Import CSV File', '', 'CSV File (*.csv)')
    if not fileName[0]:
        return False
    file = open(fileName[0], 'r')
    with file:
        fileContent = csv.reader(file)
        content = []
        for index, row in enumerate(fileContent):
            if not index and row[0] != type:
                return False
            content.append(row)
    if not fileContent.line_num:
        return False
    return content


def saveAs():
    fileName = QtWidgets.QFileDialog.getSaveFileName(None, 'Save GAS Scenario', '', 'GAS Scenario (*.gas)')
    if not fileName[0]:
        return False
    with open(fileName[0], 'w+') as file:
        conn = db.getConnection()
        for line in conn.iterdump():
            file.write('{}\n'.format(line))
        conn.close()


def load():
    fileName = QtWidgets.QFileDialog().getOpenFileName(None, 'Load GAS Scenario', '', 'GAS Scenario (*.gas)')
    if not fileName[0]:
        return False
    with open(fileName[0], 'r') as file:
        conn = db.getConnection()
        cursor = conn.cursor()
        tables = list(cursor.execute("SELECT name FROM sqlite_master WHERE type IS 'table'"))
        cursor.executescript(';'.join(['DROP TABLE IF EXISTS {}'.format(table[0]) for table in tables]))
        cursor.executescript(file.read())
        conn.close()


def removeTables():
    conn = db.getConnection()
    cursor = conn.cursor()
    tables = list(cursor.execute("SELECT name FROM sqlite_master WHERE type IS 'table'"))
    cursor.executescript(';'.join(['DROP TABLE IF EXISTS {}'.format(table[0]) for table in tables]))
    conn.close()
