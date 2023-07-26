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

## pip install imutils
## pip install timecode
## pip install hachoir-core
## pip install hachoir-parser
## pip install hachoir-metadata
## pygame!


## PIP reqs
## need timecode
## need opencv
## need hachoir-core
## need hachoir-parser
## need hachoir-metadata

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

from engine import Engine
from baseconfig import BaseConfig






## ############################################################################
##
## MAIN
##
## ############################################################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--offset", help="Offset in seconds from Video Start", action="store", default=0)
    parser.add_argument("-v", "--verbose", help="Show data about file and processing", action="count")
    parser.add_argument("-f", "--fake", help="Use GPX start date insted the vioeo one (for debug)", action="store_true")
    parser.add_argument("-l", "--layer", help="Create a layer to use in Final Cut (Overlay)", action="store_true")
    parser.add_argument("-s", "--show", help="Show frames during encoding", action="store_true")
    parser.add_argument("-t", "--title", help="Title to write")
    parser.add_argument("config_file", help="XML configuration file")
    parser.add_argument("gpx_file", help="GPX 1.1 file [fit|gpx]")
    parser.add_argument("video_file", help="Video to be tagged")
    parser.add_argument("output_file", help="Generated video with HUD info")
    args = parser.parse_args()

    hrmmanager = HRMManager(verbose=args.verbose)
    metadata = metaDataFile(args.video_file)

    stream = cv2.VideoCapture(args.video_file)

    duration_m = metadata.get('duration')
    creation_date = metadata.get('creation_date')
    width =  int(stream.get(cv2.CAP_PROP_FRAME_WIDTH ))
    height = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT ))
    frames = stream.get(cv2.CAP_PROP_FRAME_COUNT )
    fps = stream.get(cv2.CAP_PROP_FPS )


    print("Video Information ------------------------------------------------- ")
    print(("File:\t%s" % args.video_file))
    #print("MSEC: %d" % stream.get(cv2.CAP_PROP_POS_MSEC ))
    print(("WIDTH:\t%d" % stream.get(cv2.CAP_PROP_FRAME_WIDTH)))
    print(("HEIGHT:\t%d" % stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print(("FPS:\t%f" % stream.get(cv2.CAP_PROP_FPS )))
    print(("FRAMES:\t%d" % stream.get(cv2.CAP_PROP_FRAME_COUNT )))
    print(("LENGTH:\t%f" % ( frames / fps )))
    print(("Length:\t%s" % duration_m))
    print(("CDate:\t%s"  % creation_date))
    print(("Offset:\t%s" % args.offset))
    print("Video Information ------------------------------------------------- ")

    # Video Loaded. Now, I have to load the GPX file and get the points in
    # the interval marked for video. Do some trick to match the current
    # video to the GPX (I have no real data).

    # autodectect file, and get the parser acording to extension

    fname,fext = os.path.splitext(args.gpx_file)

    gpx_points = None
    if fext.lower() == ".fit":
        #
        # get points with FIT Parser
        print("Using Garmin FIT file format")
        gpx_points = hrmmanager.GetTimeRangeFIT(args.gpx_file, creation_date + timedelta(seconds=int(args.offset)), duration_m.total_seconds()-int(args.offset), fake_time=args.fake)

    if fext.lower() == ".gpx":
        print ("Using Garmin GPX file format")
        gpx_points = hrmmanager.GetTimeRangeGPX(args.gpx_file, creation_date + timedelta(seconds=int(args.offset)), duration_m.total_seconds()-int(args.offset), fake_time=args.fake)

    if not gpx_points:
        print(("Error, can't guess type for %s. Can't parse it. Ensure is FIT or GPX file." % args.gpx_file))
        sys.exit(1)

    
    data_series = CreateSeries(gpx_points)
    data_series = Smooth(data_series, [ "slope", "speed" ] )
    
    
    if False:
        gpx_item = GPXItem(gpx_points)
        gpxtxt = gpx_item.CreateGPX11(gpx_points)
        f = open("salida.gpx", "w+")
        f.write(gpxtxt)
        f.close()

        print(data_series[0].header())
        for i in data_series:
            print(i)
        sys.exit(0)
        
    # init things

    engine = Engine((width, height), fps)
    pygame.init()
    pygame.font.init()
    #screen=pygame.display.set_mode([width,height]) #small screen
    #screen=pygame.display.set_mode([320,200]) #small screen
    screen = pygame.display.set_mode([width,height],pygame.SRCALPHA,32)

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


    fourcc = cv2.VideoWriter_fourcc(*'XVID') # DIVX, XVID, MJPG, X264, WMV1, WMV2
    ostream = cv2.VideoWriter(args.output_file,fourcc, fps, (width,height))

    #
    # POINT INFO:
    # BEGIN [ POINTS ] END
    # BEGIN and END points are inserted to do some nice calculations
    #

    gpx_index = 0
    gpx_point = gpx_points[gpx_index]
    gpx_point_prev = gpx_points[gpx_index]


    # Metadata DATETIME in LOCALTIME format.

    start_time = creation_date + timedelta(seconds=int(args.offset))

    # note that VIDEO_START = GPXPOINT_START
    # watch out FAKE TIME INFO.

    if args.fake: start_time = gpx_points[0].time

    # set the current_time

    current_time = start_time
    frame_counter = 0

    # if we want to create a matte (-l) for FCP.

    if args.layer:
        # match the openCV frame format
        background_surface_np = np.zeros( (height, width, 3), np.uint8 )


    # begin calculate things #################################################

    osmmaps = engine.GetItemsByName("osmmap")
    for i in osmmaps:
        i.set_points(gpx_points)
        i.CreateMap()

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

        # get the frame delta interval

        delta = stream.get(cv2.CAP_PROP_POS_MSEC)           # from the start
        tdelta = datetime.timedelta(milliseconds=delta)
        current_time = start_time + tdelta
        
        frame_time = (frame_counter % fps) * 1.0/fps  #between 0.x and 0 (when frame change happens)
        
        # print("Current Time:%s , UTC: %s" % (current_time, gpxtoolbox.utc_to_local(gpx_point.time) ))
        if current_time > gpxtoolbox.utc_to_local(gpx_point.time):
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

        if True:
            # prepare overlay to be written
            engine.Draw(sf)

            # move to window
            frame = pygame_to_cvimage(sf)

            # write the data output
            ostream.write(frame)

            # show the frame to our screen and increment the frame counter

            if args.show:
                cv2.imshow("Frame", frame)
            key = cv2.waitKey(50) & 0xFF

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
            
            if frame_counter % fps == 0 and frame_counter >0:
                print(("FPS: %s %08d %3.2f %3.2f %3.2f %3.2f" % (current_time, frame_counter, metrics.distance, metrics.elevation, metrics.speed, metrics.slope)))

        frame_counter += 1
        ### end while

    # cleanup the camera and close any open windows
    ostream.release()
    stream.release()
    cv2.destroyAllWindows()
    pygame.quit()

    # create and restore the file
    encoder = FFMPEGAdapter()
    encoder.CopyAudioStream(args.video_file, args.output_file)


