import json


class Settings:
    def __init__(self):
        with open('settings.json') as json_file:
            self.settings = json.load(json_file)

    def getSetting(self, key):
        return self.settings[key]


def getSetting(key):
    with open('settings.json') as json_file:
        settings = json.load(json_file)
    return settings[key]


def getSettings():
    with open('settings.json') as json_file:
        settings = json.load(json_file)
    return settings


def setSettings(key, value, secondKey=False):
    settings = getSettings()
    if secondKey:
        settings[key][secondKey] = value
    else:
        settings[key] = value
    with open('settings.json', 'w') as json_file:
        json_file.write(json.dumps(settings))

# Default Settings
# {
#   "starting_time": 12,
#   "ending_time": 35,
#   "minimum_population": 50,
#   "maximum_population": 100,
#   "maximum_generations": 50,
#   "generation_tolerance": 1500,
#   "mutation_rate_adjustment_trigger": 0.08,
#   "lunchbreak": true,
#   "elite_percent": 0.05,
#   "deviation_tolerance": 55,
#   "evaluation_matrix": {
#     "subject_placement": 40,
#     "lunch_break": 10,
#     "student_rest": 10,
#     "instructor_rest": 10,
#     "idle_time": 10,
#     "meeting_pattern": 10,
#     "instructor_load": 10
#   },
#   "maximum_fitness": 100
# }
