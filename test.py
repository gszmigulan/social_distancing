import numpy
from harvesters.core import Harvester
import traceback
import sys
import cv2
import numpy as np
import time
import logic
import yolo
import statistics
import camera


def file_lengthy(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def get_and_clean(fname):
    with open(fname) as f:
        lines = [int(i) for i in f]
    open(fname, 'w').close()
    sr = statistics.mean(lines)
    return sr

get_and_clean("y.txt")

