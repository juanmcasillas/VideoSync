#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
# ############################################################################
#
# hudint.py
# 27/07/2023 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# Python Overlay 2.0 (VideoSync) main program. This program creates a HUD
# overlay based on the telemetry of FIT or GPX files. See 
# https://github.com/juanmcasillas/VideoSync for more info about it Project
# started on 07/07/2016 !s
#
# ############################################################################

##
## don't forget to save the .dll into site-packages,
## and add site-packages to the PATH
## set PATH=%PATH%;C:\Python27\Lib\site-packages
##
## see this for inspiration
## https://www.youtube.com/watch?v=tuSntvYjThU

## Only TCX & FIT files are supported. GPX only support ATEMP & HR
## extensions
##            <gpxtpx:atemp>24.0</gpxtpx:atemp>
##            <gpxtpx:hr>75</gpxtpx:hr>
##
## TCX and FIT files support
##    Cadence
##    HR
##    POWER
##
## NO TCX PARSER AVAILABLE FOR NOW :(
##
## INTEGRATED VERSION (RENDERED) with GAUGES.
##

## install xcode, and xcode-command-line-tools (xcode 5.1.1 for 10.8.5)
## install brew (dependencies)
## compile opencv3
##
##cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local \
##	-D PYTHON2_PACKAGES_PATH=/usr/lib/python2.7/site-packages \
##	-D PYTHON2_LIBRARY=/Library/Frameworks/Python.framework/Versions/2.7/bin \
##	-D PYTHON2_INCLUDE_DIR=/Library/Frameworks/Python.framework/Headers \
##	-D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=OFF \
##	-D BUILD_EXAMPLES=OFF ..
## export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/lib:$DYLD_FALLBACK_LIBRARY_PATH
## export PYTHONPATH=/usr/lib/python2.7/site-packages:$PYTHONPATH


## 07/July/2016    BASIC Skel running. Features
##    - create merged video with audio                    * done 08/07/16
##    - create composite layer (for FCP, for example)     * partial
##    - Drop shadows on text                              * done 08/07/16
##    - Optimize map drawing
##    - Basic interface (speed, slope, elev ...)
##    - Advanced (Bike information)



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
import gauges
import pytz

# experimental gopro2gpx

from gopro2gpx import gopro2gpx

from engine import Engine
from baseconfig import BaseConfig

class ClipInfo:
    def __init__(self, video_file, stream, offset=0, duration=0):
        
        ffmhelper = FFMPEGAdapter()

        self.video_file    = video_file
        json_metadata      = ffmhelper.GetJsonMetadata(self.video_file,tag="format") 
    
        #metadata           = metaDataFile(self.video_file)
        #self.duration_m    = metadata.get('duration')
        #self.creation_date = metadata.get('creation_date')
        #
        #
        
        self.duration_m    = float(json_metadata["duration"])
        # creation date in the go_pro file, is in Localtime,
        # so figure out the current localtime, and do the
        # trick to convert to UTC.
        local_tz = datetime.datetime.utcnow().astimezone().tzinfo
        self.creation_date = datetime.datetime.fromisoformat(json_metadata["tags"]["creation_time"])
        self.creation_date = self.creation_date.replace(tzinfo=local_tz)
        self.creation_date = self.creation_date.astimezone(pytz.UTC)
        
        self.width         = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH ))
        self.height        = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT ))
        self.frames        = stream.get(cv2.CAP_PROP_FRAME_COUNT )
        self.fps           = stream.get(cv2.CAP_PROP_FPS )
        self.length        = self.frames / self.fps
        self.offset        = float(offset)
        self.duration      = float(duration)
        # distance in msecs from start. Changes each time we 
        # read a frame.
        #self.msec          = stream.get(cv2.CAP_PROP_POS_MSEC )
        # Metadata DATETIME is in LOCALTIME format.
        self.start_time = self.creation_date + timedelta(seconds=self.offset)
        
     

        # adjust crop_duration value
        if self.duration > 0:
            self.crop_duration = self.duration
            if self.crop_duration > self.duration_m-self.offset:
                self.crop_duration = self.duration_m-self.offset
        else: 
            self.crop_duration = self.duration_m-self.offset
        
        
        self.gpx_info    = None

    def show_video_info(self):
        print("Video Information -[B]--------------------------------------------- ")
        print("File:         \t%s"   % self.video_file)
        print("WIDTH:        \t%d"   % self.width)
        print("HEIGHT:       \t%d"   % self.height)
        print("FPS:          \t%f"   % self.fps)
        print("FRAMES:       \t%d"   % self.frames)
        print("LENGTH(FPS):  \t%3.2f"% (self.frames * (1.0/self.fps)))
        
        print("LENGTH:       \t%f s" % self.length)
        print("Duration:     \t%s"   % self.duration_m)
        print("CDate:        \t%s"   % self.creation_date)
        print("Offset:       \t%s s" % self.offset)
        print("Duration:     \t%s s" % self.duration)
        print("Start_Time:   \t%s"   % self.start_time)
        print("Crop Duration:\t%s s" % self.crop_duration)
        print("Video Information -[E]--------------------------------------------- ")

    def show_gpx_info(self):

        print("GPX Information -[B]----------------------------------------------- ")
        print("File:           \t%s"   % self.gpx_info.gpx_file)
        print("Mode:           \t%s"   % self.gpx_info.gpx_mode)
        print("start range:    \t%s"   % self.gpx_info.start_time)
        print("end range:      \t%s"   % self.gpx_info.end_time)
        print("len range:      \t%d"   % self.gpx_info.points_len)
        print("len (all):      \t%d"   % self.gpx_info.points_all)
        print("start (all):    \t%s"   % self.gpx_info.start_time_all)
        print("end (all):      \t%s"   % self.gpx_info.end_time_all)
        print("duration (all): \t%s"   % (self.gpx_info.end_time_all - self.gpx_info.start_time_all))
        print("GPX Information -[E]----------------------------------------------- ")


    




# ############################################################################
#
# MAIN
#
# ############################################################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--offset", help="Offset in seconds from Video Start", action="store", default=0)
    parser.add_argument("-d", "--duration", help="Duration in seconds from Video Start or offset", action="store", default=0)
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-f", "--fake", help="Use GPX start date insted the vioeo one (for debug)", action="store_true")
    parser.add_argument("-l", "--layer", help="Create a layer to use in Final Cut (Overlay)", action="store_true")
    parser.add_argument("-s", "--show", help="Show frames during encoding", action="store_true")
    parser.add_argument("-i", "--only-info", help="Show info then exit", action="store_true", default=False)
    parser.add_argument("-g", "--gopro", help="Read the GPX data from goproFile", action="store_true", default=False)
    parser.add_argument("-t", "--title", help="Title to write")
    parser.add_argument("config_file", help="XML configuration file")
    parser.add_argument("gpx_file", help="GPX 1.1 file [fit|gpx]")
    parser.add_argument("video_file", help="Video to be tagged")
    parser.add_argument("output_file", help="Generated video with HUD info")
    args = parser.parse_args()

    hrmmanager = HRMManager(verbose=args.verbose)
    stream = cv2.VideoCapture(args.video_file)
    clip_info = ClipInfo(args.video_file, stream, offset=args.offset, duration=args.duration)



    clip_info.show_video_info()

    # Video Loaded. Now, I have to load the GPX file and get the points in
    # the interval marked for video. Do some trick to match the current
    # video to the GPX (I have no real data).
    # autodectect file, and get the parser acording to extension

    if args.gopro:
        if args.verbose > 1:
            print("Running Gopro2GPX first")

        file_name, file_extension = os.path.splitext(args.video_file)
        gopro_args = EmptyClass()
        gopro_args.verbose = args.verbose
        gopro_args.outputfile = file_name # adds automatically .gpx
        gopro_args.files = [ args.video_file ]
        gopro_args.binary = False
        gopro_args.skip = True
        gopro2gpx.main_core(gopro_args)
        args.gpx_file = "%s.gpx" % file_name

        if args.verbose > 1:
            print("Done. Mapped file to %s" % args.gpx_file)


    fname,fext = os.path.splitext(args.gpx_file)
    mode = fext.lower().replace('.','')
    gpx_points,gpx_info,gpx_map_points = hrmmanager.GetTimeRange(mode,
                                                  args.gpx_file, 
                                                  clip_info.start_time, 
                                                  clip_info.crop_duration,
                                                  clip_info.creation_date,
                                                  fake_time=args.fake)

    clip_info.gpx_info = gpx_info             
    clip_info.show_gpx_info()

    if args.only_info:
        exit(0)

    # TODO: check if video is in range from GPX data.

    if not gpx_points:
        print(("Error, can't guess type for %s. Can't parse it. Ensure is FIT or GPX file." % args.gpx_file))
        sys.exit(1)

    data_series = CreateSeries(gpx_points)
    data_series = Smooth(data_series, [ "slope", "speed" ],len(gpx_points) )
    
    # save dump for testing
    if False:
        gpx_item = GPXItem(gpx_points)
        gpxtxt = gpx_item.CreateGPX11(gpx_points)
        f = open("salida.gpx", "w+")
        f.write(gpxtxt)
        f.close()

    if False:
        print(data_series[0].header())
        for i in data_series:
            print(i)
        sys.exit(0)
        
    # init things

    engine = Engine((clip_info.width, clip_info.height), clip_info.fps)
    pygame.init()
    pygame.font.init()
    #screen=pygame.display.set_mode([width,height]) #small screen
    #screen=pygame.display.set_mode([320,200]) #small screen
    screen = pygame.display.set_mode([clip_info.width,clip_info.height],pygame.SRCALPHA,32)

    #engine.CreateFonts()
    #engine.CreateGauges() ## some customization for KM/H, units, etc.
    engine.ReadConfigFromFile(args.config_file)
    engine.Init()

    #engine.title.update(args.title)

    # set title (create a gauge called TITLE)
    #text = engine.fonts.default.render("HUD v 1.0", 1, prefs.colors.foreground)
    #textpos = text.get_rect(centerx=background.get_width()/2)

    # create the output video
    # AUDIO IS DISCARDED SO LETS WORK WITH FFMPEG TO ADD THE AUDIO LAYER IF NEEDED


    fourcc = cv2.VideoWriter_fourcc(*'X264') # DIVX, XVID, MJPG, X264, WMV1, WMV2, AVC1 (works: XVID)
    ostream = cv2.VideoWriter(args.output_file,fourcc, clip_info.fps, (clip_info.width,clip_info.height))

    #
    # POINT INFO:
    # BEGIN [ POINTS ] END
    # BEGIN and END points are inserted to do some nice calculations
    #

    gpx_index = 0
    gpx_point = gpx_points[gpx_index]
    gpx_point_prev = gpx_points[gpx_index]


    # note that VIDEO_START = GPXPOINT_START
    # watch out FAKE TIME INFO.

    if args.fake: 
        clip_info.start_time = gpx_points[0].time

    # set the current_time

    current_time = clip_info.creation_date # the begining of the clip, instead start_date
    frame_counter = 0

    # if we want to create a matte (-l) for FCP.

    if args.layer:
        # match the openCV frame format
        background_surface_np = np.zeros( (clip_info.height, clip_info.width, 3), np.uint8 )


    # begin calculate things #################################################
    # TODO this create the elevation and OSM map. If not found, don't use


    do_osm = False
    do_altgraph = False

    #<class 'gauges.OSMMapGauge'>
    #<class 'gauges.AltGraphGauge'>

    for item in engine.config.elements:
       
        if type(item) == type(gauges.OSMMapGauge()):
            do_osm = True
        if type(item) == type(gauges.AltGraphGauge()):
            do_altgraph = True
            
    if do_osm:
        osmmaps = engine.GetItemsByName("osmmap")
        for i in osmmaps:
            i.set_points(gpx_map_points)
            i.CreateMap()

    if do_altgraph:
        altgraph = engine.GetItemsByName("altgraph")
        for i in altgraph:
            i.set_points(gpx_points)
            i.CreateMap()


    distance = 0.0
    delta = 0

    #
    # if instrumentation, don't read all the frames. Read first one,
    # extract delta, and work on it (to speed up the things a little)
    # also don't copy audio
    #

    metrics = BaseConfig()

    metrics.slope = None
    metrics.elevation = None
    metrics.distance = None
    metrics.speed = None
    metrics.title = args.title
    #metrics.time = datetime.datetime.now().timetuple()
    metrics.time = datetime.datetime.now()
    metrics.cadence = None
    metrics.temp = None
    metrics.hr = None
    metrics.power = None
    metrics.position_index = 0
    metrics.current_position =  gpx_points[0]
    metrics.bearing = None




    while True:

        # grab the current frame
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        
        (grabbed, frame) = stream.read()
        if args.video_file and not grabbed:
            break


        # time pointers explained.
        # get the frame delta interval

        #  clip_info.creation_date
        # |         clip_info.offset
        # |         | 
        # v         v
        # B---------x---------------------------------x-----E
        #           [     clip_info.crop_duration in seconds    ]
        #           ^       ^
        #           |       | current_time (adding the delta from the beginning)
        #           clip_info.start_time
        #
        # 1) wait to delta is equal to offset (in seconds)
        # 2) while current time < clip_info.start_time + duration, do the work
        # 3) end.


        delta = stream.get(cv2.CAP_PROP_POS_MSEC)           # current position of the file relative to the start.
        tdelta = datetime.timedelta(milliseconds=delta)
        current_time = clip_info.creation_date + tdelta     # absolute pointer from the begining of the video.
        
        frame_time = (frame_counter % clip_info.fps) * 1.0/clip_info.fps  #between 0.x and 0 (when frame change happens)
        
        # skip the offset and calculate duration

        if datetime.timedelta(milliseconds=delta).total_seconds() < clip_info.offset:
            if args.verbose >2:
                print("CROPPING: Skipping frame %3.3f" % tdelta.total_seconds())
            continue
 
        if current_time > clip_info.start_time + datetime.timedelta(seconds=clip_info.crop_duration):
            if args.verbose >2:
                print("CROPPING: duration reached, exit")
            break

        # print("Current Time:%s , UTC: %s" % (current_time, gpxtoolbox.utc_to_local(gpx_point.time) ))
        # if current_time > gpxtoolbox.utc_to_local(gpx_point.time):
        if current_time > gpx_point.time:
            #
            # move point. If last one, stick to it if it is the same, skip it ahead
            #
 
            if gpx_index + 1 < len(gpx_points):
                
                gpx_index += 1
                gpx_point = gpx_points[gpx_index]
                gpx_point_prev = gpx_points[gpx_index-1]

                distance += Distance(gpx_point_prev, gpx_point)

        # update graphics engine with data.
        # engine.Update(metrics)
        # sys.exit(0)
        
        if engine.config.interpolate:
            metrics.slope = Interpolate( gpx_point_prev.time , data_series[gpx_index-1].slope, gpx_point.time , data_series[gpx_index].slope,  frame_time )
            metrics.elevation = Interpolate( gpx_point_prev.time , gpx_point_prev.elevation, gpx_point.time , gpx_point.elevation,  frame_time ) 
            # this fucking shit brokes everything jumping back and forth
            
            metrics.distance = distance + DistanceI(gpx_point_prev, gpx_point, current_time, "#" )
            
            metrics.speed = Interpolate( gpx_point_prev.time , data_series[gpx_index-1].speed, gpx_point.time , data_series[gpx_index].speed,  frame_time )
            metrics.bearing = Interpolate( gpx_point_prev.time , data_series[gpx_index-1].bearing, gpx_point.time , data_series[gpx_index].bearing,  frame_time )
        else:

            metrics.slope = data_series[gpx_index].slope
            metrics.elevation = gpx_point.elevation
            metrics.distance = distance
            metrics.speed = data_series[gpx_index].speed
            metrics.bearing = data_series[gpx_index].bearing

        
        metrics.time = current_time
        # should be previous ?
        metrics.position_index = gpx_index
        metrics.current_position =  gpx_point
        

        if "extensions" in list(gpx_point.__dict__.keys()) and gpx_point.extensions:

            for ext_item in [ "cadence", "temperature", "hr", "power"]:

                if ext_item in list(gpx_point.extensions.keys()):
                    
                    if engine.config.interpolate:
                        metrics.__dict__[ext_item] = Interpolate( gpx_point_prev.time , gpx_point_prev.extensions[ext_item],
                                                                  gpx_point.time , gpx_point.extensions[ext_item],
                                                                  frame_time )
                    else:
                        metrics.__dict__[ext_item] = gpx_point.extensions[ext_item]
               

        # update graphics engine with data.
        # test, doesn't change metrics.__dict__['power'] = frame_counter
        # print("-" * 80)
        engine.Update(metrics)
        ##engine.Print()



        #           
        #
        # annotate with PYGAME the required information.
        # set here the graphics, etc.
        #
        if args.layer:
            sf = cvimage_to_pygame(background_surface_np)
        else:
            sf = cvimage_to_pygame(frame)


        # print("=" * 80)
        # print(metrics)
        # print("=" * 80)

        # prepare overlay to be written
        engine.Draw(sf)

        # move to window
        frame = pygame_to_cvimage(sf)

        # write the data output
        ostream.write(frame)

        # show the frame to our screen and increment the frame counter

        if args.show:
            cv2.imshow("Frame", frame)
        #key = cv2.waitKey(1) & 0xFF
        key = cv2.pollKey()

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
        


        if frame_counter % clip_info.fps == 0 and frame_counter >0:
            print(("FPS: %s frames: %08d/%d distance: %05.2f elevation: %05.2f speed: %05.2f slope: %05.2f" % (
                current_time, frame_counter, clip_info.frames, 
                metrics.distance, metrics.elevation, metrics.speed, metrics.slope)))

        frame_counter += 1
        ### end while

    # cleanup the camera and close any open windows

    ostream.release()
    stream.release()
    cv2.destroyAllWindows()
    pygame.quit()
    
    ## TODO
    # create and restore the file
    encoder = FFMPEGAdapter()
    encoder.CopyAudioStream(args.video_file, args.output_file, offset=clip_info.offset, duration=clip_info.duration)


    # working
    # http://b.tile.openstreetmap.org/19/255795/197932.png
    # 
    # non working
    # http://b.tile.openstreetmap.org/19/1023205/791754.png
    # http://b.tile.openstreetmap.org/21/1023205/791754.png