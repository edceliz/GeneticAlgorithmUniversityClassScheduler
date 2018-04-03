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
        # Generate population based on minimum population
        self.generateChromosome(self.settings['minimum_population'])

    def generateChromosome(self, quantity):
        for i in range(quantity):
            self.tempChromosome = Chromosome(self.data)
            # {id: [[subjectIds](, stay|roomId = False)]}
            self.tempSections = sections = {key: [value[2], value[3]] for (key, value) in
                                            copy.deepcopy(self.data['sections']).items()}
            # {id: [subjectId, [sections]]}
            self.tempSharings = sharings = copy.deepcopy(self.data['sharings'])
            # [roomIds]
            self.rooms = rooms = list(self.data['rooms'].keys())
            # Room selection for staying sections
            for section in sections:
                if sections[section][1]:
                    room = False
                    while not room:
                        candidate = np.random.choice(rooms)
                        if self.data['rooms'][candidate][1] == 'lec':
                            room = candidate
                    sections[section][1] = room
            # Remove subjects from sections that are already in sharing
            for sharing in sharings.values():
                for section in sharing[1]:
                    sections[section][0].remove(sharing[0])
            self.generateSubjectPlacementsForSharings(sharings)
            self.generateSubjectPlacementsForSections(sections)
            self.chromosomes.append(self.tempChromosome)
            # self.chromosomes = self.chromosomes + (self.tempChromosome,)

    def generateSubjectPlacementsForSharings(self, sharings):
        sharingOrder = list(sharings.keys())
        np.random.shuffle(sharingOrder)
        for sharing in sharingOrder:
            result = self.generateSubjectPlacement(sharings[sharing][1], sharings[sharing][0], sharing)
            if not result:
                self.tempChromosome.data['unplaced']['sharings'].append(sharing)

    # {id: [[subjectIds](, stay|roomId = False)]}
    def generateSubjectPlacementsForSections(self, sections):
        # Maximum length of section subjects
        maxSubjects = max(len(subjects[0]) for subjects in sections.values())
        # Put one random section subject per turn
        for i in range(maxSubjects):
            for section in sections:
                subjectList = sections[section][0]
                if not len(subjectList):
                    continue
                subjectToPlace = np.random.randint(0, len(subjectList))
                result = self.generateSubjectPlacement([section], subjectList[subjectToPlace])
                if not result:
                    self.tempChromosome.data['unplaced']['sections'][section].append(subjectList[subjectToPlace])
                sections[section][0].pop(subjectToPlace)

    # Section = [id], Subject = int (id)
    def generateSubjectPlacement(self, section, subject, sharing = False):
        generating = True
        generationAttempt = 0
        error = None

        stayInRoom = self.tempSections[section[0]][1]
        subjectDetails = self.data['subjects'][subject]

        room = stayInRoom if stayInRoom else None
        # [[day/s], startingTimeSlot, length]
        timeDetails = []
        instructor = None

        while generating:
            # Control generation to avoid impossible combinations
            generationAttempt += 1
            if generationAttempt > self.settings['generation_tolerance']:
                generating = False
                return False
            # Allow random meeting patterns if generation is taking long
            forceRandomMeeting = True if generationAttempt > self.settings['generation_tolerance'] / 2 else False
            # First time generation
            if not error:
                if not stayInRoom or (stayInRoom and subjectDetails[6] == 'lab'):
                    room = self.selectRoom(subject)
                if len(subjectDetails[4]) > 1:
                    instructor = self.selectInstructor(subject)
                elif len(subjectDetails[4]):
                    instructor = subjectDetails[4][0]
                else:
                    instructor = False
                timeDetails = self.selectTimeDetails(subject, forceRandomMeeting)
            else:
                # Randomly select if choosing new entry or replacing subject time details
                if error == 1 or error == 2:
                    if np.random.randint(0, 2):
                        error = 3
                    elif error == 1:
                        if not stayInRoom or (stayInRoom and subjectDetails[6] == 'lab'):
                            room = self.selectRoom(subject)
                        else:
                            error = 3
                    else:
                        if len(subjectDetails[4]) > 1:
                            instructor = self.selectInstructor(subject)
                        else:
                            error = 3
                # Select subject time details
                elif error == 3:
                    timeDetails = self.selectTimeDetails(subject, forceRandomMeeting)

            # [roomId, [sectionId], subjectId, instructorID, [day / s], startingTS, length(, sharingId)]
            scheduleToInsert = [room, section, subject, instructor, *timeDetails]
            if sharing:
                scheduleToInsert.append(sharing)
            error = self.tempChromosome.insertSchedule(scheduleToInsert)
            if error is False:
                generating = False
                return True

    def selectRoom(self, subject):
        room = None
        while not room:
            candidate = np.random.choice(self.rooms)
            if self.data['subjects'][subject][6] == self.data['rooms'][candidate][1]:
                room = candidate
        return room

    def selectInstructor(self, subject):
        instructor = None
        subjectInstructors = self.data['subjects'][subject][4]
        while not instructor and len(subjectInstructors):
            instructor = np.random.choice(subjectInstructors)
        return instructor

    def selectTimeDetails(self, subject, forceRandomMeeting):
        meetingPatterns = [[0, 2, 4], [1, 3]]
        days = [0, 1, 2, 3, 4, 5]
        np.random.shuffle(days)
        hours = self.data['subjects'][subject][1]
        # Check if hours can be splitted with minimum session of 1 hour or 2 timeslot
        if hours > 1.5 and ((hours / 3) % .5 == 0 or (hours / 2) % .5 == 0):
            # If hours is divisible by two and three
            if (hours / 3) % .5 == 0 and (hours / 2) % .5 == 0:
                meetingPattern = np.random.choice(meetingPatterns)
                if len(meetingPattern) == 3:
                    meetingPattern = days[0:3] if forceRandomMeeting else meetingPattern
                    hours = hours / 3
                else:
                    meetingPattern = days[0:2] if forceRandomMeeting else meetingPattern
                    hours = hours / 2
            elif (hours / 3) % .5 == 0:
                meetingPattern = days[0:3] if forceRandomMeeting else meetingPatterns[0]
                hours = hours / 3
            else:
                meetingPattern = days[0:2] if forceRandomMeeting else meetingPatterns[1]
                hours = hours / 2
        # Select random day slot
        else:
            meetingPattern = [np.random.randint(0, 6)]
        # To convert hours into timetable timeslots
        hours = hours / .5
        startingTimeslot = False
        # Starting slot selection
        startingTime = self.settings['starting_time']
        endingTime = self.settings['ending_time']
        while not startingTimeslot:
            candidate = np.random.randint(0, endingTime - startingTime + 1)
            # Validate if subject will not overpass operation time
            if (candidate + hours) < endingTime - startingTime:
                startingTimeslot = candidate
        return [meetingPattern, startingTimeslot, int(hours)]

    def run(self):
        self.initialization()
        print('Initialization complete!')
        raise SystemExit


class Chromosome:
    # data = {
    #     sections && sharings: {
    #         id: {
    #             details: {
    #                 subject: [roomId,
    #                   instructorId,
    #                   [day / s],
    #                   startingTS,
    #                   length
    #                 ]
    #             },
    #             schedule: [days]
    #         }
    #     },
    #     instructors && rooms: {
    #         id: [
    #             [days] // Timeslots
    #             [1, None, 1, None, 1, False] // Example
    #             // None = Vacant, False = Unavailable
    #         ]
    #     },
    #     unplaced: {
    #         'sharings': [], // List of unplaced sharings
    #         'sections': {
    #             id: [] // Section ID and unplaced subjects
    #         }
    #     }
    # }

    def __init__(self, data):
        self.fitness = 0
        self.mutationRate = 0
        self.data = {
            'sections': {},
            'sharings': {},
            'instructors': {},
            'rooms': {},
            'unplaced': {
                'sharings': [],
                'sections': {}
            }
        }
        self.rawData = data
        self.settings = Settings.getSettings()
        self.buildChromosome()

    def buildChromosome(self):
        rawData = self.rawData
        # {id: {details: [subject: []], schedule: [days]}}
        sections = rawData['sections']
        for section in sections:
            self.data['sections'][section] = {'details': {}, 'schedule': []}
            self.data['sections'][section]['details'] = {key: [] for key in sections[section][2]}
            sectionTimetable = []
            for timeslotRow in sections[section][1]:
                sectionTimetable.append([None if day == 'Available' else False for day in timeslotRow])
            self.data['sections'][section]['schedule'] = sectionTimetable
            self.data['unplaced']['sections'][section] = []
        # {id: [subjectId: [details]]}
        sharings = rawData['sharings']
        for sharing in sharings:
            self.data['sharings'][sharing] = []
        # {id: [days]}
        instructors = rawData['instructors']
        for instructor in instructors:
            instructorTimetable = []
            for timeslotRow in instructors[instructor][2]:
                instructorTimetable.append([None if day == 'Available' else False for day in timeslotRow])
            self.data['instructors'][instructor] = instructorTimetable
        # {id: [days]}
        rooms = rawData['rooms']
        for room in rooms:
            roomTimetable = []
            for timeslotRow in rooms[room][2]:
                roomTimetable.append([None if day == 'Available' else False for day in timeslotRow])
            self.data['rooms'][room] = roomTimetable

    # [roomId, [sectionId], subjectId, instructorID, [day/s], startingTS, length(, sharingId)]
    def insertSchedule(self, schedule):
        # Validate schedule details
        isValid = self.validateSchedule(schedule)
        if isValid is not True:
            return isValid
        data = self.data
        # [roomId, instructorId, [day/s], startingTS, length]
        subjectDetails = [schedule[0], schedule[3], schedule[4], schedule[5], schedule[6]]
        # Check if schedule is for sharing
        if len(schedule) > 7:
            data['sharings'][schedule[-1]] = subjectDetails
        # Insert details into section data
        for section in schedule[1]:
            data['sections'][section]['details'][schedule[2]] = subjectDetails
        # Update instructor and room timetable
        for timeslot in range(schedule[5], schedule[5] + schedule[6]):
            for day in schedule[4]:
                if schedule[3]:
                    data['instructors'][schedule[3]][timeslot][day] = schedule[1]
                data['rooms'][schedule[0]][timeslot][day] = schedule[1]
        # False signifies no error in insertion
        return False

    def validateSchedule(self, schedule):
        if not self.isRoomTimeslotAvailable(schedule):
            return 1
        if not self.isInstructorTimeslotAvailable(schedule):
            return 2
        if not self.isSectionTimeslotAvailable(schedule):
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
        sections = self.data['sections']
        # Check for each room if on the given subject range, the section has class
        for room in rooms:
            for timeslotRow in range(schedule[5], schedule[5] + schedule[6]):
                for day in schedule[4]:
                    roomDayTimeslot = rooms[room][timeslotRow][day]
                    # Check if timeslot is blank
                    if roomDayTimeslot is None:
                        continue
                    # Check if section is in timeslot
                    for section in schedule[1]:
                        if section in roomDayTimeslot:
                            return False
        # Check for section unavailable times
        for section in schedule[1]:
            for timeslotRow in range(schedule[5], schedule[5] + schedule[6]):
                for day in schedule[4]:
                    if sections[section]['schedule'][timeslotRow][day] is not None:
                        return False
        return True

    def isInstructorTimeslotAvailable(self, schedule):
        # Pass if no instructor is set
        if not schedule[3]:
            return True
        instructor = self.data['instructors'][schedule[3]]
        for timeslotRow in range(schedule[5], schedule[5] + schedule[6]):
            for day in schedule[4]:
                if instructor[timeslotRow][day] is not None:
                    return False
        return True

    def getData(self):
        return self.data