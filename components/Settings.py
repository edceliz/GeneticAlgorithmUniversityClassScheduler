import json

# TODO: Complete settings component plan
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