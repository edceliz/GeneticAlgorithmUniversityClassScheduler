import random


def colorGenerator():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]


def textColor(rgb):
    return [0, 0, 0] if (((rgb[0] * 299) + (rgb[1] * 587) + (rgb[2] * 114)) / 1000) > 123 else [255, 255, 255]
