from PyQt5 import QtCore, QtWidgets, QtGui
from components import Settings
import copy
import itertools
import numpy as np


class GeneticAlgorithm(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)
    running = True
    chromosomes = []
    data = {
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
            chr = Chromosome(self.data)
            # sections = copy.deepcopy(self.data['sections'])
            # sectionsSubjects = list(map(lambda section: sections[section][2], sections))
            # maxLength = max(len(subject) for subject in sectionsSubjects)
            # sharingPositions = {}
            # sharings = self.data['sharings']
            # for i in range(maxLength):
            #     for section in sections:
            #         if sections[section][2]:
            #             subjectToPlace = sections[section][2][-1]
            #             for sharing in sharings:
            #                 if subjectToPlace == sharings[sharing][0] and section in \
            #                         sharings[sharing][1]:
            #                     # Place and put it in sharing, if sharing is already in, skip
            #                     if sharing not in sharingPositions:
            #                         self.generateSubjectPlacement(sharings[sharing][1],
            #                                                             sharings[sharing][0])
            #                         sharingPositions[sharing] = 123
            #                     else:
            #                         pass
            #                 else:
            #                     self.generateSubjectPlacement(section, sections[section][2][-1])
            #                     pass
            #             sections[section][2].pop()

    def generateSubjectPlacement(self, sectionId, subjectId):
        subject = self.data['subjects'][subjectId]
        forceMeeting = self.settings['force_meeting_patterns']
        print(forceMeeting)
        hours = subject[1]
        type = subject[6]
        divisible = subject[5]
        room = False
        rooms = self.data['rooms']
        while not room:
            room = random.choice(list(self.data['rooms'].keys()), 1)[0]
            if type != 'any':
                room = room if rooms[room][1] == type else False
        meetingPattern = []
        meetingPatterns = [[0,2,4], [1,3]]
        if hours > 1.5 and ((hours / 3) % .5 == 0 or (hours / 2) % .5 == 0):
            if (hours / 3) % .5 == 0 and (hours / 2) % .5 == 0:
                print('{} is divisible by 2 and 3'.format(hours))
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

class Chromosome:
    fitness = 0
    mutationRate = 0
    data = {
        'sections': {},
        'sharings': {},
        'instructors': {},
        'rooms': {}
    }

    def __init__(self, data):
        self.rawData = data
        self.settings = Settings.getSettings()
        self.buildChromosome()
        print(self.insertSchedule([2, [2], 4, 1, [3], 0, 2]))

    def buildChromosome(self):
        rawData = self.rawData
        sections = rawData['sections']
        for section in sections:
            self.data['sections'][section] = {key: [] for key in sections[section][2]}
        sharings = rawData['sharings']
        for sharing in sharings:
            self.data['sharings'][sharing] = []
        instructors = rawData['instructors']
        for instructor in instructors:
            instructorTimetable = []
            for timeslotRow in instructors[instructor][2]:
                instructorTimetable.append([None if day == 'Available' else False for day in timeslotRow])
            self.data['instructors'][instructor] = instructorTimetable
        rooms = rawData['rooms']
        for room in rooms:
            roomTimetable = []
            for timeslotRow in rooms[room][2]:
                 roomTimetable.append([None if day == 'Available' else False for day in timeslotRow])
            self.data['rooms'][room] = roomTimetable

    # [roomId, [sectionId], subjectId, instructorID, [day/s], startingTS, length(, sharingId)]
    def insertSchedule(self, schedule):
        isValid = self.validateSchedule(schedule)
        if isValid is not True:
            return isValid
        # Insert into section, sharings, instructor, room
        data = self.data
        subjectDetails = [schedule[0], schedule[3], schedule[4], schedule[5], schedule[6]]
        print(subjectDetails)
        if len(schedule) > 7:
            data['sharings'][schedule[-1]] = subjectDetails
        for section in schedule[1]:
            data['sections'][section][schedule[2]] = subjectDetails
        for timeslot in range(schedule[5], schedule[5] + schedule[6]):
            for day in schedule[4]:
                data['instructors'][schedule[3]][timeslot][day] = schedule[1]
                data['rooms'][schedule[0]][timeslot][day] = schedule[1]
        return True

    def validateSchedule(self, schedule):
        if not self.isRoomTimeslotAvailable(schedule):
            return 1
        if not self.isSectionTimeslotAvailable(schedule):
            return 2
        if not self.isInstructorTimeslotAvailable(schedule):
            return 3
        return True

    def isRoomTimeslotAvailable(self, schedule):
        room = self.data['rooms'][schedule[0]]
        for timeslotRow in range(schedule[5], schedule[5] + schedule[6]):
            for day in schedule[4]:
                if room[timeslotRow][day] is not None:
                    return False
        return True

    def isSectionTimeslotAvailable(self, schedule):
        rooms = self.data['rooms']
        for room in rooms:
            for timeslotRow in range(schedule[5], schedule[5] + schedule[6]):
                for day in schedule[4]:
                    roomDayTimeslot = rooms[room][timeslotRow][day]
                    if not roomDayTimeslot:
                        continue
                    for section in schedule[1]:
                        if section in roomDayTimeslot:
                            return False
        return True

    def isInstructorTimeslotAvailable(self, schedule):
        instructor = self.data['instructors'][schedule[3]]
        for timeslotRow in range(schedule[5], schedule[5] + schedule[6]):
            for day in schedule[4]:
                if instructor[timeslotRow][day] is not None:
                    return False
        return True

    def getData(self):
        return self.data