from components import Database as db
import json


class ScenarioComposer:
    def __init__(self):
        self.conn = db.getConnection()
        self.cursor = self.conn.cursor()

    def getInstructors(self):
        self.cursor.execute('SELECT id, name, hours, schedule FROM instructors WHERE active = 1')
        instructors = self.listToDictionary(self.cursor.fetchall())
        instructors = self.jsonToList(instructors, 2)
        return instructors

    def getRooms(self):
        self.cursor.execute('SELECT id, name, type, schedule FROM rooms WHERE active = 1')
        rooms = self.listToDictionary(self.cursor.fetchall())
        rooms = self.jsonToList(rooms, 2)
        return rooms

    def getSubjects(self):
        self.cursor.execute('SELECT id, name, hours, code, description, instructors, divisible, type FROM subjects')
        subjects = self.listToDictionary(self.cursor.fetchall())
        subjects = self.jsonToList(subjects, 4)
        subjects = self.stringToInt(subjects, 4)
        return subjects

    def getSections(self):
        self.cursor.execute('SELECT id, name, schedule, subjects, stay FROM sections WHERE active = 1')
        sections = self.listToDictionary(self.cursor.fetchall())
        sections = self.jsonToList(sections, 1)
        sections = self.jsonToList(sections, 2)
        sections = self.stringToInt(sections, 2)
        return sections

    def getSharings(self):
        self.cursor.execute('SELECT id, subjectId, sections FROM sharings WHERE final = 1')
        sharings = self.listToDictionary(self.cursor.fetchall())
        sharings = self.jsonToList(sharings, 1)
        sharings = self.stringToInt(sharings, 1)
        return sharings

    def listToDictionary(self, toDict):
        return {entry[0]: list(entry[1:]) for entry in toDict}

    def jsonToList(self, dictionary, index):
        for key, value in dictionary.items():
            dictionary[key][index] = json.loads(value[index])
        return dictionary

    def stringToInt(self, dictionary, index):
        for key, value in dictionary.items():
            dictionary[key][index] = list(map(int, value[index]))
        return dictionary

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()

    def getScenarioData(self):
        data = {
            'instructors': self.getInstructors(),
            'sharings': self.getSharings(),
            'sections': self.getSections(),
            'subjects': self.getSubjects(),
            'rooms': self.getRooms()
        }
        self.closeConnection()
        return data
