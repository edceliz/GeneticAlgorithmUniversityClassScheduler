import random
from numpy import random as np


def colorGenerator():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]


def textColor(rgb):
    return [0, 0, 0] if (((rgb[0] * 299) + (rgb[1] * 587) + (rgb[2] * 114)) / 1000) > 123 else [255, 255, 255]

if __name__ == '__main__':
    for i in range(3):
        settings = []
        settings.append(np.randint(50, 200))
        settings.append(np.randint(settings[0], 200))
        settings.append(np.randint(50, 150))
        settings.append(np.randint(1500, 4500))
        settings.append(round(np.random() / 5, 2))
        settings.append(np.randint(90, 100))
        settings.append(np.randint(0, 10))
        settings.append(np.randint(50, 75))
        print(settings)