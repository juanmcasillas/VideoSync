import sys


from collections import namedtuple
import subprocess
import tempfile
import os
import os.path
from manager import HRMManager
from mapper import *
import gpxpy
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
from baseconfig import BaseConfig

if __name__ == "__main__":



    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Configuration File")
    parser.add_argument("gpx_file", help="GPX file")
    args = parser.parse_args()

    width = 1280
    height = 720
    resolution = (width, height) # width, height
    fps = 50.0

    hrmmanager = HRMManager(verbose=True, overwrite=True)
    gpx_points = hrmmanager.GetTimeRangeFIT(args.gpx_file, 0, -1, fake_time=True)
    data_series = CreateSeries(gpx_points)
    data_series = Smooth(data_series, [ "slope" ])

    pygame.init()
    pygame.font.init()


    engine = Engine(resolution, fps)

    screen = pygame.display.set_mode([width,height],pygame.SRCALPHA,32)
    background = pygame.Surface([width,height],pygame.SRCALPHA,32)
    #background.convert()

    engine.ReadConfigFromFile(args.config)
    engine.Init()
    clock = pygame.time.Clock()



    metrics = BaseConfig()

    metrics.slope = 0.0
    metrics.elevation = 0.0
    metrics.distance = 0.0
    metrics.speed = 0.0
    metrics.title = "This is the title inserted into a label"
    metrics.time = datetime.datetime.now().timetuple()
    metrics.cadence = 0.0
    metrics.temperature = 34
    metrics.hr = 0.0
    metrics.power = 0.0
    metrics.position_index = len(gpx_points)/2
    metrics.current_position =  gpx_points[metrics.position_index]
    metrics.bearing = 0.0


    osmmaps = engine.GetItemsByName("osmmap")
    for i in osmmaps:
        i.set_points(gpx_points)
        i.CreateMap()

    altgraph = engine.GetItemsByName("altgraph")
    for i in altgraph:
        i.set_points(gpx_points)
        i.CreateMap()


    while True:
        background.fill((0,0,0,255))


        #engine.time.update(datetime.datetime.now().timetuple())
        #engine.hr.update(int(hr))

        engine.Update(metrics)
        engine.Draw(background)

        screen.blit(background, (0, 0))
        pygame.display.flip()
        clock.tick(fps)

        metrics.distance += 0.1
        metrics.speed += 0.2
        metrics.hr += 0.3
        metrics.slope += 0.4
        metrics.elevation += 0.5
        metrics.time = datetime.datetime.now().timetuple()
        metrics.cadence += 0.1
        metrics.temperature += 0.1
        metrics.power += 1
        metrics.position_index = len(gpx_points)/2 + random.randrange(100)
        metrics.current_position = gpx_points[metrics.position_index]
        metrics.bearing += 1




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