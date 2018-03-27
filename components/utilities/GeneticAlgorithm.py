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
    tempChromosome = None
    tempSections = None

    def __init__(self, data):
        self.data = data
        self.settings = Settings.getSettings()
        super().__init__()

    def __del__(self):
        self.wait()

    def initialization(self):
        for i in range(self.settings['minimum_population']):
            self.tempChromosome = Chromosome(self.data)
            self.tempSections = sections = {key: [value[2], value[3]] for (key, value) in copy.deepcopy(self.data['sections']).items()}
            rooms = list(self.data['rooms'].keys())
            for section in sections:
                if sections[section][1]:
                    room = False
                    while not room:
                        candidate = np.random.choice(rooms)
                        if self.data['rooms'][candidate][1] == 'lec':
                            room = candidate
                    sections[section][1] = room
            # TODO: Sharing initialization priority
            self.generateSubjectPlacementsForSections(sections)
            self.chromosomes.append(self.tempChromosome)
            print('Done')

    def generateSubjectPlacementsForSections(self, sections):
        maxSubjects = max(len(subjects[0]) for subjects in sections.values())
        for i in range(maxSubjects):
            for section in sections:
                print(sections[section][0])
                if len(sections[section][0]):
                    self.generateSubjectPlacement(section, sections[section][0][-1])
                    if len(sections[section][0]) == 1:
                        sections[section][0] = []
                    else:
                        sections[section][0].pop()

    def generateSubjectPlacement(self, section, subject):
        generating = True
        generationAttempt = 0
        error = None
        rooms = list(self.data['rooms'].keys())
        room = self.tempSections[section][1]
        subjectTimeDetails = []
        instructor = None
        while generating:
            if error == 1 or error is None:
                if error == 1 or error == 2:
                    if not self.tempSections[section][1]:
                        room = np.random.choice([room, False])
                    if room:
                        subjectTimeDetails = self.generateTimeDetails(subject)
                while not room and not self.tempSections[section][1]:
                    candidate = np.random.choice(rooms)
                    if self.data['subjects'][subject][6] == self.data['rooms'][candidate][1]:
                        room = candidate
                # ADD LABORATORY SUPPORT FOR STAY IN ROOM!
            if error == 2 or error is None:
                subjectTimeDetails = self.generateTimeDetails(subject)
            if error == 3 or error is None:
                if error == 3:
                    instructor = np.random.choice([instructor, False])
                    if instructor:
                        subjectTimeDetails = self.generateTimeDetails(subject)
                    else:
                        instructor = np.random.choice(self.data['subjects'][subject][4])
                else:
                    instructor = np.random.choice(self.data['subjects'][subject][4])
            error = self.tempChromosome.insertSchedule([room, [section], subject, instructor, *subjectTimeDetails])
            if error is True:
                return True
            # if generationAttempt == self.settings['generation_tolerance']:
            #     print('reached attempt')
            #     return False
            generationAttempt += 1

    def generateTimeDetails(self, subject):
        meetingPatterns = [[0, 2, 4], [1, 3]]
        hours = self.data['subjects'][subject][1]
        if hours > 1.5 and ((hours / 3) % .5 == 0 or (hours / 2) % .5 == 0):
            if (hours / 3) % .5 == 0 and (hours / 2) % .5 == 0:
                meetingPattern = np.random.choice(meetingPatterns)
                if len(meetingPattern) == 3:
                    hours = hours / 3
                else:
                    hours = hours / 2
            elif (hours / 3) % .5 == 0:
                meetingPattern = meetingPatterns[0]
                hours = hours / 3
            else:
                meetingPattern = meetingPatterns[1]
                hours = hours / 2
        else:
            meetingPattern = [np.random.randint(0, 6)]
        hours = hours / .5
        startingTimeslot = False
        while not startingTimeslot:
            candidate = np.random.randint(0, self.settings['ending_time'] - self.settings['starting_time'] + 1)
            if (candidate + hours) < self.settings['ending_time'] - self.settings['starting_time']:
                startingTimeslot = candidate
        return [meetingPattern, startingTimeslot, int(hours)]

    def run(self):
        self.initialization()
        # raise SystemExit


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
        data = self.data
        subjectDetails = [schedule[0], schedule[3], schedule[4], schedule[5], schedule[6]]
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
