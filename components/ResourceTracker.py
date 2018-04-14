import os
import psutil


def getCPUUsage():
    return psutil.cpu_percent(1)


def getMemoryUsage():
    return [psutil.Process(os.getpid()).memory_info()[0], psutil.virtual_memory()[0]]


def getMemoryPercentage(memoryUsage):
    return round((memoryUsage[0] / memoryUsage[1]) * 100, 2)


def byteToMegabyte(byte):
    return round(byte / 1048576, 2)
