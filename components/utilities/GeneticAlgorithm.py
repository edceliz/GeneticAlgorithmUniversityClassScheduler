from PyQt5 import QtCore, QtWidgets, QtGui
from components import Settings
import copy
import itertools
from numpy import random


class GeneticAlgorithm(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)
    running = True
    chromosomes = []
    data = {
        'results': [],
        'rooms': [],
        'instructors': [],
        'sections': [],
        'sharings': [],
        'subjects': []
    }

    def __init__(self, data):
        self.data = data
        self.settings = Settings.getSettings()
        super().__init__()

    def __del__(self):
        self.wait()

    def initialization(self):
        for i in range(1):
            # for i in range(self.settings['minimum_population']):
            chr = ScheduleChromosome(self.data['rooms'])
            sections = copy.deepcopy(self.data['sections'])
            sectionsSubjects = list(map(lambda section: sections[section][2], sections))
            maxLength = max(len(subject) for subject in sectionsSubjects)
            sharingPositions = {}
            sharings = self.data['sharings']
            for i in range(maxLength):
                for section in sections:
                    if sections[section][2]:
                        subjectToPlace = sections[section][2][-1]
                        for sharing in sharings:
                            if subjectToPlace == sharings[sharing][0] and section in \
                                    sharings[sharing][1]:
                                # Place and put it in sharing, if sharing is already in, skip
                                if sharing not in sharingPositions:
                                    self.generateSubjectPlacement(sharings[sharing][1],
                                                                        sharings[sharing][0])
                                    sharingPositions[sharing] = 123
                                else:
                                    pass
                            else:
                                self.generateSubjectPlacement(section, sections[section][2][-1])
                                pass
                        sections[section][2].pop()

    def generateSubjectPlacement(self, sectionId, subjectId):
        subject = self.data['subjects'][subjectId]
        hours = subject[1]
        type = subject[6]
        divisible = subject[5]
        room = False
        rooms = self.data['rooms']
        while not room:
            room = random.choice(list(self.data['rooms'].keys()), 1)[0]
            if type != 'any':
                room = room if rooms[room][1] == type else False
        # print(self.settings['force_meeting_patterns'])
        meetingPattern = []
        # TODO: Calculate room division and pattern
        if hours > 1.5 and ((hours / 3) % .5 == 0 or (hours / 2) % .5 == 0):
            print('{} is divisible'.format(hours))
        else:
            print('{} is not divisible'.format(hours))
            # Assign normal one day/week
            # meetingPattern =
        return [room, hours, meetingPattern]

    def evalSubjectsTaken(self):
        pass

    def run(self):
        self.initialization()
        raise SystemExit


class ScheduleChromosome:
    def __init__(self, rooms):
        self.fitness = 0
        self.mutationRate = 0
        self.data = {}
        for key in rooms.keys():
            roomSchedule = list(
                map(lambda day: list(map(lambda timeslot: 0 if timeslot == 'Available' else False, day)),
                    rooms[key][2]))
            self.data[key] = roomSchedule
        self.operatingHours = len(list(self.data.values())[0])

    def placeSubject(self, room, timeslotSize, days, startingSlot, subjectData):
        if not self.timeslotAvailable(room, timeslotSize, days, startingSlot):
            return False
        for timeslot in range(startingSlot, startingSlot + timeslotSize):
            timeslotData = self.data[room][timeslot]
            if isinstance(days, list):
                for day in days:
                    timeslotData[day] = subjectData
            else:
                timeslotData[days] = subjectData

    def timeslotAvailable(self, room, timeslotSize, days, startingSlot):
        for timeslot in range(startingSlot, startingSlot + timeslotSize):
            timeslotData = self.data[room][timeslot]
            if isinstance(days, list):
                for day in days:
                    if timeslotData[day] != 0 or timeslotData[day] is False: return False
            else:
                if timeslotData[days] != 0 or timeslotData[days] is False: return False
        return True

    def mapSubjectSlots(self):
        pass

    def getData(self):
        return self.data
