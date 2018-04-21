from PyQt5 import QtCore
from components import Settings
from operator import itemgetter
from collections import Counter
import copy
import itertools
import numpy as np


class GeneticAlgorithm(QtCore.QThread):
    # Current phase of the algorithm
    statusSignal = QtCore.pyqtSignal(str)
    # Genetic algorithm variable details
    detailsSignal = QtCore.pyqtSignal(list)
    # Running process type
    operationSignal = QtCore.pyqtSignal(int)
    # List of chromosomes for preview
    dataSignal = QtCore.pyqtSignal(list)

    def __init__(self, data):
        self.averageFitness = 0
        self.pastAverageFitness = 0
        self.running = True
        self.chromosomes = []
        self.data = {
            'rooms': [],
            'instructors': [],
            'sections': [],
            'sharings': [],
            'subjects': []
        }
        self.stayInRoomAssignments = {}
        self.tournamentSize = .04
        self.elitePercent = .05
        self.mutationRate = .10
        self.lowVariety = 55
        self.highestFitness = 0
        self.lowestFitness = 100
        self.elites = []
        self.matingPool = []
        self.offsprings = []
        self.tempChromosome = None
        self.tempSections = None
        self.data = data
        self.settings = Settings.getSettings()
        self.stopWhenMaxFitnessAt = self.settings['maximum_fitness']
        super().__init__()

    def initialization(self):
        # Generate population based on minimum population
        self.generateChromosome(self.settings['minimum_population'])

    def generateChromosome(self, quantity):
        for i in range(quantity):
            self.statusSignal.emit('Creating #{} of {} Chromosomes'.format(i, quantity))
            self.tempChromosome = Chromosome(self.data)
            # {id: [[subjectIds](, stay|roomId = False)]}
            self.tempSections = sections = {key: [value[2], value[3]] for (key, value) in
                                            copy.deepcopy(self.data['sections']).items()}
            # {id: [subjectId, [sections]]}
            self.tempSharings = sharings = copy.deepcopy(self.data['sharings'])
            # [roomIds]
            self.rooms = rooms = list(self.data['rooms'].keys())
            # Distributed Room selection for staying sections
            if not len(self.stayInRoomAssignments):
                selectedRooms = []
                for section in sections:
                    if sections[section][1]:
                        room = False
                        attempts = 0
                        while not room:
                            attempts += 1
                            candidate = np.random.choice(rooms)
                            if attempts == self.settings['generation_tolerance']:
                                room = candidate
                            if self.data['rooms'][candidate][1] == 'lec':
                                if candidate not in selectedRooms:
                                    selectedRooms.append(copy.deepcopy(candidate))
                                    room = candidate
                        sections[section][1] = room
                        self.stayInRoomAssignments[section] = room
            else:
                for section, room in self.stayInRoomAssignments.items():
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

        stayInRoom = False if section[0] not in self.stayInRoomAssignments.keys() else self.stayInRoomAssignments[
            section[0]]
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

    def evaluate(self):
        totalChromosomeFitness = 0
        self.pastAverageFitness = copy.deepcopy(self.averageFitness)
        self.lowestFitness = 100
        self.highestFitness = 0
        for index, chromosome in enumerate(self.chromosomes):
            self.statusSignal.emit('Evaluating #{} of {} Chromosomes'.format(index + 1, len(self.chromosomes)))
            chromosome.fitness = self.evaluateAll(chromosome)
            totalChromosomeFitness += chromosome.fitness
            self.averageFitness = totalChromosomeFitness / len(self.chromosomes)
            self.highestFitness = chromosome.fitness if chromosome.fitness > self.highestFitness else self.highestFitness
            self.lowestFitness = chromosome.fitness if chromosome.fitness < self.lowestFitness else self.lowestFitness
        chromosomeFitness = sorted(enumerate(map(lambda chromosome: chromosome.fitness, self.chromosomes)),
                                   key=itemgetter(1))
        # Emit top five chromosomes
        self.dataSignal.emit(
            list(map(lambda chromosome: [self.chromosomes[chromosome[0]], chromosome[1]], chromosomeFitness[-5:])))

    # Evaluation weight depends on settings
    def evaluateAll(self, chromosome):
        subjectPlacement = self.evaluateSubjectPlacements(chromosome)
        lunchBreak = self.evaluateLunchBreak(chromosome) if self.settings['lunchbreak'] else 100
        studentRest = self.evaluateStudentRest(chromosome)
        instructorRest = self.evaluateInstructorRest(chromosome)
        idleTime = self.evaluateStudentIdleTime(chromosome)
        meetingPattern = self.evaluateMeetingPattern(chromosome)
        instructorLoad = self.evaluateInstructorLoad(chromosome)
        chromosome.fitnessDetails = copy.deepcopy([subjectPlacement, lunchBreak, studentRest, instructorRest, idleTime,
                                     meetingPattern, instructorLoad])
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
        if not instructorTeachingDays:
            return 100.00
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
        if not len(activeInstructors):
            return 100.00
        instructorLoadAverage = round(instructorLoadAverage / len(activeInstructors), 2)
        return instructorLoadAverage

    def getAllFitness(self):
        return [chromosome.fitness for chromosome in self.chromosomes]

    def adapt(self):
        deviation = self.getFitnessDeviation()
        self.alignPopulation(deviation[0], deviation[1])
        self.adjustMutationRate()

    # sigma = [sigma], sigmaInstances = {sigma: instance%}
    def getFitnessDeviation(self):
        populationCount = len(self.chromosomes)
        fitnesses = [chromosome.fitness for chromosome in self.chromosomes]
        mean = np.mean(fitnesses)
        sigmas = [int(fitness - mean) for fitness in fitnesses]
        sigmaInstances = {sigma: (instance / populationCount) * 100 for sigma, instance in
                          dict(Counter(sigmas)).items()}
        return [sigmas, sigmaInstances]

    def alignPopulation(self, sigmas, sigmaInstances):
        populationCount = len(self.chromosomes)
        sigmaStartingInstance = list(sigmaInstances.values())[0]
        if sigmaStartingInstance > self.lowVariety:
            # Add the excess percentage of instances on first sigma to population
            generate = int((int(sigmaStartingInstance - self.lowVariety) / 100) * populationCount)
            while generate + populationCount > self.settings['maximum_population']:
                generate -= 1
            self.generateChromosome(generate)
        else:
            # Remove the excess percentage of instances on first sigma to population
            sortedSigmas = sorted(enumerate(sigmas), key=itemgetter(1))
            remove = int((int(self.lowVariety - sigmaStartingInstance) / 100) * populationCount)
            while populationCount - remove < self.settings['minimum_population']:
                remove -= 1
            remove = [sortedSigmas[index][0] for index in range(remove)]
            self.chromosomes = [chromosome for index, chromosome in enumerate(self.chromosomes) if index not in remove]

    # Increase mutation rate for low performing generations and decrease for good performance
    def adjustMutationRate(self):
        if (self.averageFitness - self.pastAverageFitness < 0) or (
                abs(self.averageFitness - self.pastAverageFitness) <= self.settings[
            'mutation_rate_adjustment_trigger']) and not self.mutationRate >= 100:
            self.mutationRate += .05
        elif self.mutationRate > .10:
            self.mutationRate -= .05
        self.mutationRate = round(self.mutationRate, 2)

    # Selects top 5% of population and performs tournament to generate remaining candidates
    def selection(self):
        population = len(self.chromosomes)
        chromosomeFitness = [self.chromosomes[chromosome].fitness for chromosome in range(len(self.chromosomes))]
        # Select number of elites that will ensure there will be even offspring to be generated
        eliteCount = round(population * self.elitePercent)
        if population % 2 == 0:
            eliteCount = eliteCount if eliteCount % 2 == 0 else eliteCount + 1
        else:
            eliteCount = eliteCount if eliteCount % 2 != 0 else eliteCount + 1
        self.statusSignal.emit('Selecting {} Elites'.format(eliteCount))
        sortedFitness = sorted(enumerate(chromosomeFitness), key=itemgetter(1))
        elites = list(map(lambda chromosome: chromosome[0], sortedFitness[eliteCount * -1:]))
        matingPool = []
        matingPoolSize = int((population - eliteCount) / 2)
        tournamentSize = int(self.tournamentSize * population)
        if tournamentSize > 25:
            tournamentSize = 25
        # Fill mating pool with couples selected by multiple tournaments
        for i in range(matingPoolSize):
            self.statusSignal.emit('Creating #{} of {} Couples'.format(i + 1, matingPoolSize))
            couple = []
            while len(couple) != 2:
                winner = self.createTournament(tournamentSize, chromosomeFitness)
                if winner not in couple:
                    couple.append(winner)
            matingPool.append(couple)
        self.elites = elites
        self.matingPool = matingPool

    # size = int, population = [fitness]
    def createTournament(self, size, population):
        participants = []
        # Select participants
        for i in range(size):
            candidate = False
            while candidate is False:
                candidate = np.random.randint(0, len(population))
                if candidate in participants:
                    candidate = False
                    continue
            participants.append(candidate)
        winner = participants[0]
        for participant in participants:
            if population[participant] > population[winner]:
                winner = participant
        return winner

    def crossover(self):
        offspringCount = 1
        self.offsprings = []
        for couple in self.matingPool:
            self.statusSignal.emit(
                'Creating #{} of {} Offsprings'.format(offspringCount, len(self.chromosomes) - len(self.elites)))
            self.offsprings.append(self.createOffspring(couple))
            offspringCount += 1
            couple.reverse()
            self.statusSignal.emit(
                'Creating #{} of {} Offsprings'.format(offspringCount, len(self.chromosomes) - len(self.elites)))
            self.offsprings.append(self.createOffspring(couple))
            offspringCount += 1
        self.elites = list(map(lambda elite: copy.deepcopy(self.chromosomes[elite]), self.elites))
        self.chromosomes = self.offsprings + self.elites

    # Returns a chromosome containing a mix of parents genes
    def createOffspring(self, parent):
        self.tempChromosome = offspring = Chromosome(self.data)
        parentA = self.chromosomes[parent[0]]
        parentB = self.chromosomes[parent[1]]
        parentAShareables = {
            'sharings': {},
            'sections': {}
        }
        # Parent A shall provide half of its genes
        parentASharings = parentA.data['sharings']
        if len(parentASharings) > 1:
            # Amount of sharings to get
            sharingCarve = round(len(parentASharings) / 3)
            # Middlemost element with bias to left
            startingPoint = int(len(parentASharings) / 2) - (sharingCarve - 1)
            for index in range(startingPoint, startingPoint + sharingCarve):
                # Take note that index does not mean it is the key of the sharings
                # [{sharingId: details}]
                sharings = [id for id in parentASharings.keys()]
                for sharing in sharings[startingPoint:startingPoint + sharingCarve]:
                    parentAShareables['sharings'][sharing] = parentASharings[sharing]
        # Raw list of parent A sections with reduced subjects from sharings
        parentASections = {}
        for section, value in copy.deepcopy(parentA.data['sections']).items():
            parentASections[section] = value['details']
        for sharing in self.data['sharings'].values():
            for section in sharing[1]:
                parentASections[section].pop(sharing[0])
        parentASections = {key: value for key, value in filter(lambda item: len(item[1]) > 1, parentASections.items())}
        # Calculate the shareables of each section
        for section, values in parentASections.items():
            # Amount of section subjects to share
            sectionCarve = round(len(values) / 3)
            # Middlemost element with bias to left
            startingPoint = int(len(values) / 2) - (sectionCarve - 1)
            subjects = [id for id in values.keys()]
            for index in range(startingPoint, startingPoint + sectionCarve):
                if section not in parentAShareables['sections']:
                    parentAShareables['sections'][section] = {}
                parentAShareables['sections'][section][subjects[index]] = values[subjects[index]]
        parentBShareables = {
            'sharings': {},
            'sections': {}
        }
        # Add remaining sharings from parent B
        for id, sharing in parentB.data['sharings'].items():
            if id not in parentAShareables['sharings'].keys():
                parentBShareables['sharings'][id] = sharing
        # Create list of parent B sections
        parentBSections = {}
        for section, value in copy.deepcopy(parentB.data['sections']).items():
            parentBSections[section] = value['details']
        for sharing in self.data['sharings'].values():
            for section in sharing[1]:
                parentBSections[section].pop(sharing[0])
        # Create list of subjects that are not in parent A shareables
        for section in parentBSections:
            parentBShareables['sections'][section] = {}
            for id, subject in parentBSections[section].items():
                if not (id in list(parentAShareables['sections'][section].keys())):
                    parentBShareables['sections'][section][id] = subject
        # List of unplaced sharings with or without data
        unplacedSharings = {}
        # Insert parent A sharings into chromosome
        sharings = self.data['sharings']
        for id, sharing in parentAShareables['sharings'].items():
            if not len(sharing):
                unplacedSharings[id] = []
                continue
            offspring.insertSchedule([sharing[0], sharings[id][1], sharings[id][0], sharing[1], *sharing[2:5], id])
        # Add parent B subjects in random manner
        parentBSharings = list(parentBShareables['sharings'].keys())
        np.random.shuffle(parentBSharings)
        for id in parentBSharings:
            sharing = parentBShareables['sharings'][id]
            if not len(sharing):
                unplacedSharings[id] = []
                continue
            if offspring.insertSchedule([sharing[0], sharings[id][1], sharings[id][0], sharing[1], *sharing[2:5], id]):
                unplacedSharings[id] = sharing
        # List of unplaced subjects with or without data
        unplacedSectionSubjects = {}
        # Insert parent A section subjects into chromosome
        for section, subjects in parentAShareables['sections'].items():
            if section not in unplacedSectionSubjects.keys():
                unplacedSectionSubjects[section] = {}
            for subject, details in subjects.items():
                if not len(details):
                    unplacedSectionSubjects[section][subject] = []
                    continue
                if offspring.insertSchedule([details[0], [section], subject, details[1], *details[2:5]]):
                    unplacedSectionSubjects[section][subject] = details
        # Insert parent B section subjects into chromosome
        for section, subjects in parentBShareables['sections'].items():
            if section not in unplacedSectionSubjects.keys():
                unplacedSectionSubjects[section] = {}
            for subject, details in subjects.items():
                if not len(details):
                    unplacedSectionSubjects[section][subject] = []
                    continue
                if offspring.insertSchedule([details[0], [section], subject, details[1], *details[2:5]]):
                    unplacedSectionSubjects[section][subject] = details
        # Attempt to insert unplaced sharings
        for sharing in copy.deepcopy(unplacedSharings).keys():
            if self.generateSubjectPlacement(sharings[sharing][1], sharings[sharing][0], sharing):
                unplacedSharings.pop(sharing)
        # Attempt to insert unplaced section subjects
        for section, subjects in copy.deepcopy(unplacedSectionSubjects).items():
            for subject, detail in subjects.items():
                if self.generateSubjectPlacement([section], subject):
                    unplacedSectionSubjects[section].pop(subject)
        return offspring

    def mutation(self):
        sharings = self.data['sharings']
        sections = self.data['sections']
        mutationCandidates = {
            'sections': {},
            'sharings': [key for key in sharings.keys()]
        }
        # Prepare clean list of subject placement with consideration for sharing
        for section, data in copy.deepcopy(sections).items():
            mutationCandidates['sections'][section] = data[2]
        for sharing in sharings.values():
            for section in sharing[1]:
                mutationCandidates['sections'][section].remove(sharing[0])
        if not len(mutationCandidates['sharings']):
            mutationCandidates.pop('sharings')
        for section in copy.deepcopy(mutationCandidates['sections']):
            if not len(mutationCandidates['sections'][section]):
                mutationCandidates['sections'].pop(section)
        # Randomly select chromosomes to mutate
        for index, chromosome in enumerate(copy.deepcopy(self.chromosomes)):
            if np.random.randint(100) > (self.mutationRate * 100) - 1:
                continue
            self.statusSignal.emit('Mutating Chromosome #{}'.format(index + 1))
            self.tempChromosome = Chromosome(self.data)
            # Select a gene to mutate
            mutating = np.random.choice(list(mutationCandidates.keys()))
            if mutating == 'sections':
                section = np.random.choice(list(mutationCandidates['sections'].keys()))
                mutating = ['sections', section, np.random.choice(mutationCandidates['sections'][section])]
            else:
                mutating = ['sharing', np.random.choice(mutationCandidates['sharings'])]
            # Replicate chromosome except the mutating gene
            for sharing in mutationCandidates['sharings'] if 'sharings' in mutationCandidates else []:
                if mutating[0] == 'sharing' and sharing == mutating[1]:
                    continue
                details = chromosome.data['sharings'][sharing]
                if len(details):
                    self.tempChromosome.insertSchedule(
                        [details[0], sharings[sharing][1], sharings[sharing][0], details[1], *details[2:5], sharing])
            for section, subjects in mutationCandidates['sections'].items():
                for subject in subjects:
                    if mutating[0] == 'sections' and mutating[1] == section and mutating[2] == subject:
                        continue
                    details = chromosome.data['sections'][section]['details'][subject]
                    if len(details):
                        self.tempChromosome.insertSchedule([details[0], [section], subject, details[1], *details[2:5]])
            # Generate mutation
            if mutating[0] == 'sharing':
                self.generateSubjectPlacement(sharings[mutating[1]][1], sharings[mutating[1]][0], mutating[1])
            else:
                self.generateSubjectPlacement([mutating[1]], mutating[2])
            self.chromosomes[index] = copy.deepcopy(self.tempChromosome)

    def run(self):
        self.statusSignal.emit('Initializing')
        self.initialization()
        generation = 0
        runThread = True
        while (runThread):
            if self.running:
                generation += 1
                self.statusSignal.emit('Preparing Evaluation')
                self.evaluate()
                self.detailsSignal.emit(
                    [generation, len(self.chromosomes), int(self.mutationRate * 100), round(self.averageFitness, 2),
                     round(self.pastAverageFitness, 2), self.highestFitness, self.lowestFitness])
                if self.highestFitness >= self.settings['maximum_fitness']:
                    self.statusSignal.emit('Reached the Highest Fitness')
                    self.operationSignal.emit(1)
                    self.running = runThread = False
                    break
                if self.settings['maximum_generations'] < generation - 1:
                    self.statusSignal.emit('Hit Maximum Generations')
                    self.operationSignal.emit(1)
                    self.running = runThread = False
                    break
                self.statusSignal.emit('Tweaking Environment')
                self.adapt()
                self.statusSignal.emit('Preparing Selection')
                self.selection()
                self.statusSignal.emit('Preparing Crossover')
                self.crossover()
                self.statusSignal.emit('Preparing Mutation')
                self.mutation()


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
        isValid = self.validateSchedule(copy.deepcopy(schedule))
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
        # Check if instructor can still teach
        maxLoad = self.rawData['instructors'][schedule[3]][1] * 2
        for timeslotRow in instructor:
            for day in timeslotRow:
                if day:
                    maxLoad -= 1
        if maxLoad < 0:
            return False
        return True
