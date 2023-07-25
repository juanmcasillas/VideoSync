import sys


from collections import namedtuple
import subprocess
import tempfile
import os
import os.path
from manager import HRMManager
from mapper import *
import .gpxpy
import gpxtoolbox
from metrics import *
from helpers import *

from collections import deque
import numpy as np
import argparse
import imutils
import cv2

import math
import datetime
import time
import timecode
import pygame
import pygame.locals

from engine import Engine
from preferences import Preferences

if __name__ == "__main__":

    width= 1280
    height=720
    fps=50.0


    prefs = Preferences()
    engine = Engine(prefs, fps)

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode([width,height],pygame.SRCALPHA,32)
    prefs.SetDisplayMode(screen)

    background = pygame.Surface([width,height],pygame.SRCALPHA,32)
    #background.convert()


    engine.CreateFonts()
    engine.HRGauge()
    engine.HRECGGauge()
    engine.TimeGauge()
    engine.BearingGauge()
    clock = pygame.time.Clock()



    hr = 30
    bearing = 0

    while True:
        background.fill((0,0,0,255))

        #engine.slope.update(data_series[gpx_index].slope ) # normalized slope
        #engine.distance.update(distance / 1000.0)        # in Km
        #engine.distance.update(distance)                  # in m
        #engine.elevation.update(gpx_point.elevation)      # in meters
        #engine.speed.update(data_series[gpx_index].speed)                      # in km/h
        engine.time.update(datetime.datetime.now().timetuple())
        #engine.gps.update(gpx_point)
        #engine.gpsmap.update(gpx_point)
        #engine.altmap.update(gpx_index-1)

        #engine.power.update(gpx_point.extensions["power"])
        #engine.power.update(gpx_index * 20.0)
        engine.hr.update(int(hr))
        engine.hrecg.update(int(hr))
        engine.bearing.update(int(bearing))
        #engine.cadence.update(gpx_point.extensions["cad"])
        #engine.temp.update(gpx_point.extensions["temperature"])
        engine.hr.draw(background)
        engine.hrecg.draw(background)
        engine.time.draw(background)
        engine.bearing.draw(background)

        screen.blit(background, (0, 0))
        pygame.display.flip()
        clock.tick(fps)
        hr += 0.1
        bearing += 1

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit(0)
                break
            elif event.type == pygame.locals.KEYDOWN and (event.key == pygame.locals.K_ESCAPE or event.key == pygame.locals.K_q):
                pygame.quit()
                sys.exit(0)
                break

    pygame.quit()