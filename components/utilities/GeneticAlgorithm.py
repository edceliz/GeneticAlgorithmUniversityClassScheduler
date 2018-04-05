from PyQt5 import QtCore
from components import Settings
import copy
import itertools
import numpy as np


class GeneticAlgorithm(QtCore.QThread):
    messageSignal = QtCore.pyqtSignal(object)
    metaSignal = QtCore.pyqtSignal(object)
    statusSignal = QtCore.pyqtSignal(object)

    averageFitness = 0
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

    # INITIALIZATION BLOCK
    #
    def initialization(self):
        # Generate population based on minimum population
        self.generateChromosome(self.settings['minimum_population'])

    def generateChromosome(self, quantity):
        for i in range(quantity):
            self.messageSignal.emit('Creating #{}/{} Chromosome'.format(i, quantity))
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
    def generateSubjectPlacement(self, section, subject, sharing=False):
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
        if hours > 1.5 and ((hours / 3) % .5 == 0 or (hours / 2) % .5 == 0) and self.data['subjects'][subject][5]:
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
    #
    # INITIALIZATION BLOCK

    # EVALUATION BLOCK
    #
    def evaluate(self):
        totalChromosomeFitness = 0
        for index, chromosome in enumerate(self.chromosomes):
            self.messageSignal.emit('Evaluating Chromosome #{}/{}'.format(index + 1, len(self.chromosomes)))
            chromosome.fitness = self.evaluateAll(chromosome)
            totalChromosomeFitness += chromosome.fitness
            self.averageFitness = totalChromosomeFitness / len(self.chromosomes)
            self.metaSignal.emit([round(self.averageFitness, 2)])

    # Evaluation weight depends on settings
    def evaluateAll(self, chromosome):
        subjectPlacement = self.evaluateSubjectPlacements(chromosome)
        lunchBreak = self.evaluateLunchBreak(chromosome) if self.settings['lunchbreak'] else 100
        studentRest = self.evaluateStudentRest(chromosome)
        instructorRest = self.evaluateInstructorRest(chromosome)
        idleTime = self.evaluateStudentIdleTime(chromosome)
        meetingPattern = self.evaluateMeetingPattern(chromosome)
        instructorLoad = self.evaluateInstructorLoad(chromosome)
        chromosome.fitnessDetails = [subjectPlacement, lunchBreak, studentRest, instructorRest, idleTime,
                                     meetingPattern, instructorLoad]
        matrix = self.settings['evaluation_matrix']
        return round(
            (subjectPlacement * matrix['subject_placement'] / 100) +
            (lunchBreak * matrix['lunch_break'] / 100) +
            (studentRest * matrix['student_rest'] / 100) +
            (instructorRest * matrix['instructor_rest'] / 100) +
            (idleTime * matrix['idle_time'] / 100) +
            (meetingPattern * matrix['meeting_pattern'] / 100) +
            (instructorLoad * matrix['instructor_load'] / 100),
            2
        )

    # = ((subjects - unplacedSubjects) / subjects) * 100
    def evaluateSubjectPlacements(self, chromosome):
        sections = copy.deepcopy({key: value[2] for key, value in self.data['sections'].items()})
        sharings = self.data['sharings']
        chromosomeUnplacedData = chromosome.data['unplaced']
        # Number of subjects that are in sharing
        sharingSubjects = 0
        # Remove section subjects that are shared
        for sharing in sharings.values():
            # Sharing subjects is increased based on number of sections sharing the subject
            sharingSubjects += len(sharing[1])
            for section in sharing[1]:
                sections[section].remove(sharing[0])
        # Combined list of section subjects
        sectionSubjects = len(list(itertools.chain.from_iterable(sections.values())))
        # Combined list of subjects
        totalSubjects = sectionSubjects + sharingSubjects
        # Number of shared subjects that are not placed
        unplacedSharingSubjects = 0
        for sharing in chromosomeUnplacedData['sharings']:
            # Sharing subjects is increased based on number of sections sharing the subject
            unplacedSharingSubjects += len(sharings[sharing][1])
        # Length of unplaced section subjects
        unplacedSectionSubjects = len(list(itertools.chain.from_iterable(chromosomeUnplacedData['sections'].values())))
        totalUnplacedSubjects = unplacedSharingSubjects + unplacedSectionSubjects
        return round(((totalSubjects - totalUnplacedSubjects) / totalSubjects) * 100, 2)

    # = ((sectionDays - noLunchDays) / sectionDays) * 100
    def evaluateLunchBreak(self, chromosome):
        sectionDays = 0
        noLunchDays = 0
        for section in chromosome.data['sections'].values():
            # [roomId, instructorId, [day / s], startingTS, length]
            details = section['details']
            # A temporary map for days and lunch period
            # {day: [22, 23, 24, 25]}
            # TS 22-25 : 11 AM - 1 PM
            tempScheduleMap = {key: [22, 23, 24, 25] for key in range(6)}
            # Days that the section used
            tempSectionDays = []
            # Loop through each subject and remove lunch period timeslots that are occupied.
            for subject in details.values():
                if not len(subject):
                    continue
                for day in subject[2]:
                    if day not in tempSectionDays:
                        tempSectionDays.append(day)
                    # Check if subject is in lunch period
                    for timeslot in range(subject[3], subject[3] + subject[4]):
                        if timeslot in tempScheduleMap[day]:
                            tempScheduleMap[day].remove(timeslot)
            # If whole day's lunch period is taken, count it as no lunch break
            for day in tempScheduleMap.values():
                if not len(day):
                    noLunchDays += 1
            sectionDays += len(tempSectionDays)
        return round(((sectionDays - noLunchDays) / sectionDays) * 100, 2)

    # = ((sectionDays - noRestDays) / sectionDays) * 100
    def evaluateStudentRest(self, chromosome):
        sectionDays = 0
        noRestDays = 0
        for section in chromosome.data['sections'].values():
            # Sections week
            week = {day: [] for day in range(6)}
            for subject in section['details'].values():
                if not len(subject):
                    continue
                # Add section subject timeslots to sections week
                for day in subject[2]:
                    for timeslot in range(subject[3], subject[3] + subject[4]):
                        week[day].append(timeslot)
                        week[day].sort()
            for day in week.values():
                if not len(day):
                    continue
                sectionDays += 1
                if len(day) < 6:
                    continue
                hasViolated = False
                # Steps of how many three hours per day a section has (Increments of 30 minutes)
                for threeHours in range(6, len(day) + 1):
                    if hasViolated:
                        continue
                    # Compare consecutive timeslot to section's day timeslot
                    if [timeslot for timeslot in range(day[threeHours - 6], day[threeHours - 6] + 6)] == day[
                                                                                                         threeHours - 6: threeHours]:
                        hasViolated = True
                        noRestDays += 1
        return round(((sectionDays - noRestDays) / sectionDays) * 100, 2)

    # = ((instructorTeachingDays - noRestDays) / instructorTeachingDays) * 100
    def evaluateInstructorRest(self, chromosome):
        instructorTeachingDays = 0
        noRestDays = 0
        for instructor in chromosome.data['instructors'].values():
            # Instructor week
            week = {day: [] for day in range(6)}
            for timeslot, timeslotRow in enumerate(instructor):
                for day, value in enumerate(timeslotRow):
                    # Add timeslot to instructor week if teaching
                    if value:
                        week[day].append(timeslot)
            for day in week.values():
                if not len(day):
                    continue
                instructorTeachingDays += 1
                if len(day) < 6:
                    continue
                hasViolated = False
                # Steps of how many three hours per day a section has (Increments of 30 minutes)
                for threeHours in range(6, len(day) + 1):
                    if hasViolated:
                        continue
                    # Compare consecutive timeslot to section's day timeslot
                    if [timeslot for timeslot in range(day[threeHours - 6], day[threeHours - 6] + 6)] == day[
                                                                                                         threeHours - 6: threeHours]:
                        hasViolated = True
                        noRestDays += 1
        return round(((instructorTeachingDays - noRestDays) / instructorTeachingDays) * 100, 2)

    # = ((sectionDays - idleDays) / sectionDays) * 100
    def evaluateStudentIdleTime(self, chromosome):
        sectionDays = 0
        idleDays = 0
        for section in chromosome.data['sections'].values():
            week = {day: [] for day in range(6)}
            for subject in section['details'].values():
                if not len(subject):
                    continue
                # Add section subject timeslots to sections week
                for day in subject[2]:
                    week[day].append([timeslot for timeslot in range(subject[3], subject[3] + subject[4])])
                    week[day].sort()
            for day in week.values():
                if not len(day):
                    continue
                sectionDays += 1
                # For every 6 TS that the day occupies, there is 1 TS allowable break
                allowedBreaks = round((len(list(itertools.chain.from_iterable(day))) / 6), 2)
                # If the decimal of allowed breaks is greater than .6, consider it as an addition
                if (allowedBreaks > 1 and allowedBreaks % 1 > 0.60) or allowedBreaks % 1 > .80:
                    allowedBreaks += 1
                for index, timeslots in enumerate(day):
                    if index == len(day) - 1 or allowedBreaks < 0:
                        continue
                    # Consume the allowable breaks with the gap between each subject of the day
                    if timeslots[-1] != day[index + 1][0] - 1:
                        allowedBreaks -= timeslots[-1] + day[index + 1][0] - 1
                    if allowedBreaks < 0:
                        idleDays += 1
        return round(((sectionDays - idleDays) / sectionDays) * 100, 2)

    # = ((placedSubjects - badPattern) / placedSubjects) * 100
    def evaluateMeetingPattern(self, chromosome):
        placedSubjects = 0
        badPattern = 0
        for section in chromosome.data['sections'].values():
            for subject in section['details'].values():
                if not len(subject) or len(subject[2]) == 1:
                    continue
                placedSubjects += 1
                # Check if subject has unusual pattern
                if subject[2] not in [[0, 2, 4], [1, 3]]:
                    badPattern += 1
        return round(((placedSubjects - badPattern) / placedSubjects) * 100, 2)

    def evaluateInstructorLoad(self, chromosome):
        activeInstructors = {}
        activeSubjects = []
        # Get list of active subjects
        for section in self.data['sections'].values():
            activeSubjects += section[2]
        subjects = self.data['subjects']
        sharings = self.data['sharings']
        # Get list of active instructors and their potential load
        for subject in activeSubjects:
            # Exclude subjects that have less than 1 candidate instructor
            if len(subjects[subject][4]) <= 1:
                continue
            for instructor in subjects[subject][4]:
                if instructor not in activeInstructors.keys():
                    activeInstructors[instructor] = [0, 0]
                activeInstructors[instructor][0] += int(subjects[subject][1] / .5)
        # Remove load from instructors that is duplicated due to sharing
        for sharing in sharings.values():
            subject = subjects[sharing[0]]
            if len(subject[4]) <= 1:
                continue
            for instructor in subject[4]:
                activeInstructors[instructor][0] -= int(subject[1] / .5) * (len(sharing[1]) - 1)
        # Fill up active instructors with actual load
        for instructor, details in chromosome.data['instructors'].items():
            for timeslotRow in details:
                for day in timeslotRow:
                    if day and instructor in activeInstructors.keys():
                        activeInstructors[instructor][1] += 1
        instructorLoadAverage = 0
        # Calculate the average instructor load. Closer to 50% means equal distribution which is better
        for instructor in activeInstructors.values():
            instructorLoadAverage += (instructor[1] / instructor[0]) * 100
        instructorLoadAverage = round(((instructorLoadAverage / len(activeInstructors)) / 50) * 100, 2)
        return instructorLoadAverage
    #
    # EVALUATION BLOCK

    def selection(self):
        pass

    def crossover(self):
        pass

    def mutation(self):
        pass

    def adapting(self):
        pass

    def run(self):
        self.messageSignal.emit('Started Initialization')
        self.initialization()
        self.messageSignal.emit('Initialization Complete')
        generation = 0
        while self.running:
            generation += 1
            if self.settings['maximum_generations'] < generation:
                self.messageSignal.emit('Hit the maximum generation!')
                self.statusSignal.emit(1)
                self.running = False
                continue
            self.messageSignal.emit('Started Evaluation')
            self.evaluate()
            self.metaSignal.emit([round(self.averageFitness, 2), generation])
            self.messageSignal.emit('Started Selection')
            self.selection()
            self.messageSignal.emit('Started Crossover')
            self.crossover()
            self.messageSignal.emit('Started Mutation')
            self.mutation()
            self.messageSignal.emit('Started Adaptation')
            self.adapting()


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
        self.fitnessDetails = []
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
