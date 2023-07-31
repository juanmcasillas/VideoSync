#!/usr/bin/env python
#
# Juan M. Casillas
# PolarGPX
#
# Integrate altitude data inside the files generated with RCX5
#
#
# RCX5 files generate 2 files
#
# VIA WEBSYNC:        Upload exercise data to PolarPersonalTrainer (without altitude)
#                    after export data, a GPX11 compliant file is generated, with
#                    altitude data extracted from GoogleMaps.
#
#                    GPX:
#                    -1.1 format
#                    -various segments, 1 track. Join them first
#    - GPX11_IN
#
# VIA LOCALSYNC:    Generates two files. A GPX 1.0 compliant file without altitude
#                    and a HRM file with some funky parameters that need to be tuned
#
#                    GPX:
#                    -Add the Elevation data from GPX11_IN
#                    -The number of points is the same of the HRData Items in HRM file
#                    -Time is UTC
#                    -Format it for GPX 1.0
#                    -The number of points in GPX11_IN != number of points in GPX10_IN
#                    -one segment, one track
#
#                    HRM:
#    - GPX10_IN
#    - HRM_IN
#
#def usage():
#    print "%s: [-a] [-f] GPX11IN GPX10IN HRMIN" % sys.argv[0]
#    print "where:"
#    print " -f --force: overwrite output files (GPX10IN and HRMIN)"
#    print " GPX11IN is the GPX 1.1 file exported from PolarPersonalTrainer (e.g. 14053001.gpxe)"
#    print " GPX10IN    is the GPX 1.0 file generated from WebSync (Local) (e.g. 14053001.gpx)"
#    print " HRMIN    is the HRM file generated from WebSync (Local) (e.g. 14053001.hrm)"
#    print ""
#    print "    14053001 = yymmddee (yy year=(20)14, mm month=05 dd day=30 ee exercise=01"
#    print ""
#    print " if not -f specified, generates two files: GPX10IN_ele and HRMIN_ele (e.g. 14053001_ele.gpx and 14053001_ele.hrm)"
#    print ""
#
#     RCX5 is mapped to monitor 1 (Polar Sport Tester)
#





import sys
import argparse
import os
import os.path
import random
import time
import datetime as dt
from datetime import datetime, timezone
import calendar
import math
import xml.dom.minidom as xmlp
from gpxtoolbox import *

# use Python3 Version
#from . import fitparse
import fitparse
from gpxpy.gpx import GPXTrackPoint

class EmptyClass(object): pass

class HRMManager():
    def __init__(self, verbose=0, overwrite=False, generate_cadence=False, generate_power=False,  no_elevation=False, roller=False):
        self.overwrite = overwrite
        self.generate_cadence = generate_cadence
        self.generate_power = generate_power
        self.no_elevation = no_elevation
        self.roller = roller
        self.verbose = False

    def add_ele_extension(self, filen):
        "c:\\gpx10file.gpx -> C:\\gpx10file_ele.gpx"

        abspath = os.path.abspath(filen)

        fn = os.path.basename(os.path.splitext(abspath)[0])
        ex = os.path.splitext(abspath)[1]

        fn = "%s%s%s_ele%s" % (os.path.dirname(abspath), os.sep, fn, ex)
        return fn

    def replace_or_overwrite(self, fn, data):
        fnl = fn
        if not self.overwrite:
            # add the ele extension to the file name.
            fnl = self.add_ele_extension(fn)

        outf = file(fnl,"wb")
        outf.write(data)
        outf.close()

        if self.verbose >= 1:
            print(self.LOG("Data written to '%s'" % fnl))


    def create_or_overwrite(self, fn, data):
        fnl = fn
        if not self.overwrite and os.path.exists(os.path.abspath(fnl)):
            # add the ele extension to the file name.
            fnl = self.add_ele_extension(fn)

        # support unicode.
        
        if isinstance(data,str):
            outf = codecs.open(fnl, "wb", 'utf-8')
        else:
            outf = file(fnl,"wb")
        outf.write(data)
        outf.close()

        if self.verbose >= 1:
            print(self.LOG("Data written to '%s'" % fnl))

    def LOG(self, msg):
        dt = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime())
        return "[%s] %s" % (dt, msg)



    #
    # AddPower(hrm)
    # add power data (fake) in order to prepare HRM files to support the Stages data
    #

    def AddPower(self, hrm_file):
        """
        Add power data (fake) in order to prepare HRM files to support the Stages data
        """

        #1 read the HRM file, extract params and show data

        if self.verbose >= 1:
            print(self.LOG("START '%s'" % (hrm_file)))

        hrmfile = HRMParser()
        try:
            hrmfile.ParseFromFile(hrm_file)
        except Exception as e:
            raise Exception("Error parsing HRM %s: %s" % (hrm_file, e))

        if self.verbose >= 1:
            print(self.LOG("Parsed HRMFile '%s'" % hrm_file))

        #
        # last, but not least, mangle the HRData section
        #
        # 1) the number of points is the Same than in the gpx10 file
        # 2) points are ordered
        # 3) if not speed activated, calculate the speed for each HRData (todo)
        #

        # if fake cadence, add a debug serie
  # just add it if not cadence found.

        if self.generate_cadence and hrmfile.sections['Params'].mode.cadence == False:

            hrmfile.sections['Params'].set_cadence(True)
            random.seed()
            cadence_values = []
            for i in range(len(hrmfile.sections['HRData'].items)):
                cad_r = 80 + random.randrange(-20,20)
                cadence_values.append(cad_r)

            hrmfile.sections['HRData'].set_cadence(cadence_values)

            if self.verbose >= 1:
                print(self.LOG("Added DEBUG_CADENCE to HRM file '%s' (%d points)" % (hrm_file, len(cadence_values))))

        # if fake power, add a debug serie

        if self.generate_power:
            hrmfile.sections['Params'].set_power(True)
            random.seed()
            power_values = []
            for i in range(len(hrmfile.sections['HRData'].items)):
                power_v = 200 + random.randrange(-100,200)
                pbpi_v = (100*256)+50
                #power_v = 888
                #pbpi_v =  999
                power_values.append( (power_v, pbpi_v) )

            hrmfile.sections['HRData'].set_power(power_values)

            if self.verbose >= 1:
                print(self.LOG("Added DEBUG_POWER to HRM file '%s' (%d points)" % (hrm_file, len(power_values))))


        #
        # export all the data and store it
        #

        self.replace_or_overwrite(hrm_file, hrmfile.Export())

        if self.verbose >= 2:
            hrmfile.DebugSections(self.verbose)

        if self.verbose >= 1:
            print(self.LOG("END '%s'" % (hrm_file)))
        return True



    ###

    def Process(self, gpx11_file, gpx10_file, hrm_file):
        """
        This function takes the files GPX11 and builds the GPX10 with elevations
        then, fixes the HRM_FILE adding the right parameters (and sections) and
        putting the elevation data inside
        """

        #1 read the HRM file, extract params and show data

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s' '%s'" % (gpx11_file, gpx10_file, hrm_file)))


        hrmfile = HRMParser()
        try:
            hrmfile.ParseFromFile(hrm_file)
        except Exception as e:
            raise Exception("Error parsing HRM %s: %s" % (hrm_file, e))

        if self.verbose >= 1:
            print(self.LOG("Parsed HRMFile '%s'" % hrm_file))

        #If no trip section (brand new file) add it, and set the mode propertly
        #RCX5 monitor flags with '0' (no monitor)  by default, PolarProTrainer adds a '1'
        #Polar Sport Tester / Vantage XL. Maybe it's better to put here the value
        #'22':    'Polar S625X / S725X' for more capable item.

        if not 'Trip' in list(hrmfile.sections.keys()):
            hrmfile.sections['Trip'] = TripSection()
            hrmfile.sections['Trip'].setdefault()
            if self.verbose >= 1:
                print(self.LOG("Added TRIP section to hrmfile"))

        hrmfile.sections['Params'].CheckMonitor('22')

        #2 read the GPX Files and show some data about them


        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11_file, gpx10_file)
        except Exception as e:
            raise Exception("Error while parsing %s and %s: %s" % (gpx11_file, gpx10_file, e))


        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX11 '%s' (%d points) and GPX10 '%s' (%d points)" % \
                (gpx11_file, gpxmanager.get_gpx11_points_no(), gpx10_file, gpxmanager.get_gpx10_points_no())))

        #3 FIX the GPX1.0 to GPX.1.1 info, and save it. If overwrite is on
        #save the data in the same file, else, create another one with ele
        #extension.

        xml = ""
        try:
            xml = gpxmanager.ConvertLoadedFiles()
        except Exception as e:
            raise Exception("Error while adding ALTITUDE from %s into %s: %s" % (gpx11_file, gpx10_file, e))

        if self.verbose >= 1:
                debug_time = time.time() - debug_time
                elapsed = time.gmtime(debug_time)
                elapsed = time.strftime("%H:%M:%S",elapsed)
                print(self.LOG("ALTITUDE succesfully added (elapsed time %s)" % elapsed))

        # save the GPX10 file

        self.replace_or_overwrite(gpx10_file, xml)

        #
        # 4 HARDCORE STEP. ADD Info to the HRM File. In order to do that, we have some considerations to archieve
        #

        # First, tweak the params section and add the Altitude switch to Mode

        hrmfile.sections['Params'].set_altitude(True)

        # then, calculate and fill the Trip Area

        hrmfile.sections['Trip'].set_distance        ( gpxmanager.get_distance() )
        hrmfile.sections['Trip'].set_ascent            ( gpxmanager.get_ascent() )
        hrmfile.sections['Trip'].set_totaltime        ( gpxmanager.get_totaltime() )
        hrmfile.sections['Trip'].set_average_alt    ( gpxmanager.get_average_altitude() )
        hrmfile.sections['Trip'].set_max_alt        ( gpxmanager.get_max_alt() )
        hrmfile.sections['Trip'].set_average_speed    ( gpxmanager.get_average_speed()[1] )
        hrmfile.sections['Trip'].set_max_speed        ( gpxmanager.get_max_speed() )
        hrmfile.sections['Trip'].set_odometer        ( gpxmanager.get_distance() )

        if self.verbose >= 1:
                print(self.LOG("Data added to TRIP section"))

        #
        # Now, process the LapTimes and add the Momentary Altitude and Lap Ascend
        # Lap  Times are stored relative to the start of the exercise. So convert
        # everything to seconds, in order to access to the data stored in the file
        #

        start_date = hrmfile.sections['Params'].date
        start_time = hrmfile.sections['Params'].starttime

        sd = [ start_date[0], start_date[1], start_date[2],
               start_time[0], start_time[1], start_time[2],
               0            , 0            , -1             ]

        sd = list(map (int, sd))

        # pass the start_date to gmt,

        sd = time.mktime(sd)

        #sd_gmt = time.gmtime(sd)
        sd_gmt = time.localtime(sd)


        for l in range(hrmfile.sections['IntTimes'].NumberOfLaps()):
            lap_time =     hrmfile.sections['IntTimes'].LapTime(l)
            #
            # convert to seconds
            #
            lap_time_seconds = (lap_time[0]*3600) +(lap_time[1] * 60) + (lap_time[2]) + math.ceil( lap_time[3]/10 )
            target = time.mktime(sd_gmt) + lap_time_seconds
            target_s = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(target))

            point = gpxmanager.get_location_at( target )

            hrmfile.sections['IntTimes'].set_momentary_altitude(l, point.elevation)
            hrmfile.sections['IntTimes'].set_asc(l, point.elevation)

            #print "%s %s (%s)" % (point.time , point.elevation, target_s)
            if self.verbose >= 1:
                print(self.LOG("Added ELEVATION data to lap #%d" % (l)))

        #
        # last, but not least, mangle the HRData section
        #
        # 1) the number of points is the Same than in the gpx10 file
        # 2) points are ordered
        # 3) if not speed activated, calculate the speed for each HRData (todo)
        #

        if not hrmfile.sections['Params'].mode.speed:

            speed_values = gpxmanager.get_speed_for_all_points()
            #print "GPX# %d" % gpxmanager.gpx10.tracks[0].get_points_no()
            #print "HRData %d" % len(hrmfile.sections['HRData'].items)
            #print "Speed %d" % len(speed_values)

            hrmfile.sections['Params'].set_speed(True)
            hrmfile.sections['HRData'].set_speed(speed_values)

            if self.verbose >= 1:
                print(self.LOG("Added SPEED data to HRM file '%s' (%d points)" % (hrm_file, len(speed_values))))

        # if fake cadence, add a debug serie

        if self.generate_cadence:
            hrmfile.sections['Params'].set_cadence(True)
            random.seed()
            cadence_values = []
            for i in range(len(hrmfile.sections['HRData'].items)):
                cad_r = 80 + random.randrange(-20,20)
                cadence_values.append(cad_r)

            hrmfile.sections['HRData'].set_cadence(cadence_values)

            if self.verbose >= 1:
                print(self.LOG("Added DEBUG_CADENCE to HRM file '%s' (%d points)" % (hrm_file, len(cadence_values))))


        #
        # compute altitude and store it in the HRData
        #

        altitude_values = gpxmanager.get_elevation_for_all_points()
        #print "HRData %d" % len(hrmfile.sections['HRData'].items)
        #print "altitude %d" % len(altitude_values)

        hrmfile.sections['HRData'].set_altitude(altitude_values)

        if self.verbose >= 1:
            print(self.LOG("Added ALTITUDE to HRM file '%s' (%d points)" % (hrm_file, len(altitude_values))))

        #
        # export all the data and store it
        #

        self.replace_or_overwrite(hrm_file, hrmfile.Export())

        if self.verbose >= 2:
            hrmfile.DebugSections(self.verbose)
            gpxmanager.DebugFiles()


        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s' '%s'" % (gpx11_file, gpx10_file, hrm_file)))
        return True


    #
    # Fixer: Some useful function to fix times, create sample HRM data from scratch,
    # etc. Seldom used. Get the gpx11 file, generate a some called _fixed file with
    # the interpolated data, etc. Use it for development pourposes only
    #

    def Fixer(self, gpx11_file):

        tgt_file = gpx11_file + ".fixed"

        if self.verbose >= 1:
          print(self.LOG("START '%s'" % gpx11_file))

        try:
          gpxmanager = GPXToolBox()
          gpxmanager.LoadFiles(gpx11=gpx11_file)
        except Exception as e:
          raise Exception("Error while parsing %s: %s" % (gpx11_file, e))

        if self.verbose >= 1:
          debug_time = time.time()
          print(self.LOG("Loaded GPX1 '%s' (%d points)" % (gpx11_file, gpxmanager.get_gpx11_points_no())))


        gpxmanager.gpx11.MergeAll()

        gpx = gpxmanager.gpx11
        points = gpx.Segment().points

        #
        # now, iterate points, extract date, calculate the time (+5/+4) and create the HR values
        # also calculate the HR value. For that, interpolate the following:
        #
        # base HR: 75
        # if next point elev > +1 till 140
        # if next point elev < -1 until 60

        base_hr = 75
        max_hr = 140

        target_time = datetime.strptime("2014-12-08 14:38:45","%Y-%m-%d %H:%M:%S")
        hr = base_hr

        for i in range(len(points)):
          p = points[i]

          if i+1 < len(points):
            n = points[i+1]
            if n.elevation > p.elevation:
              if hr+1 <= max_hr:
                hr += random.randint(0,2)
            if n.elevation < p.elevation:
              if hr-1 >= base_hr:
                hr -= random.randint(0,2)

            p.extensions = { 'hr': hr, 'cad': 0 }
          else:
            hr = points[i-1].extensions['hr']
            p.extensions = { 'hr': hr, 'cad': 0 }


          if p.time == target_time:
            delta = random.randint(4,5)
            p.time = points[i-1].time + timedelta(seconds=delta)
          else:
            p.time = p.time + timedelta(hours=672)
            p.time = p.time - timedelta(hours=1)



        xml = gpx.CreateGPX11(points)

        self.replace_or_overwrite(tgt_file, xml)

        if self.verbose >= 2:
          gpxmanager.DebugFiles()

        if self.verbose >= 1:
          print(self.LOG("END '%s'" % gpx11_file))
        return True


        #
        # extract the creation date (date for first gpx entry) and build a HRM
        # name in the format YYMMDD01.hrm
        #
    def GuessHRMFileName(self, gpx11_file):

        if self.verbose >= 1:
            print(self.LOG("START '%s'" % (gpx11_file)))

        gpxmanager = GPXToolBox()
        gpxmanager.LoadFiles(gpx11=gpx11_file)
        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11=gpx11_file)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx11_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX1 '%s' (%d points)" % (gpx11_file, gpxmanager.get_gpx11_points_no())))

        gpxmanager.gpx11.MergeAll()
        gpx = gpxmanager.gpx11
        points = gpx.Segment().points

        gpx_date =  self.UTC2Localtime(points[0].time)#.strftime('%Y%m%d')
        fname = gpx_date.strftime("%y%m%d01.hrm")

        if self.verbose >= 1:
            print(self.LOG("END '%s' -> '%s'" % (gpx11_file,fname)))

        return fname



    #
    # Get and GPX11 file from Garmin (with extensions) and build and HRM
    # compilant file
    #

    def GPX2HRM(self, gpx11in, hrm_file):

        fmode = True
        gpx11_file = gpx11in
        if not isinstance(gpx11in, str):
            fmode = False
            gpx11_file = '-'


        #1 read the GPX file, and look for HRM data. If not found, bail out...

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s'" % (gpx11_file, hrm_file)))

        try:
            gpxmanager = GPXToolBox()
            if fmode:
                gpxmanager.LoadFiles(gpx11=gpx11_file)
            else:
                gpxmanager.set_gpx11(gpx11in)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx11_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX1 '%s' (%d points)" % (gpx11_file, gpxmanager.get_gpx11_points_no())))


        gpxmanager.gpx11.MergeAll()

        #2 check for HRM extensions...

        #
        #  <extensions>
        #  <gpxtpx:TrackPointExtension>
        #    <gpxtpx:hr>60</gpxtpx:hr>
        #  </gpxtpx:TrackPointExtension>
        #  <gpxx:TrackPointExtension/>
        # </extensions>
        #

        gpx = gpxmanager.gpx11
        points = gpx.Segment().points

        if not gpx.HasExtensions('hr'):
            return False

        # check if we have speed info and no gps data... in this case, this
        # fucking shit is a  Roller ouput (rodillo garmin EDGE)
        roller_mode = False
        roller_max_speed = 0
        roller_avg_speed = 0


        #print gpx.get_distance_2d()
        #print gpx.get_antplus_distance()

        if gpx.get_distance_2d() == 0 and gpx.get_antplus_distance() > 0.0:
            # roller / rodillo work
            roller_mode = True

        #
        # Ok, we have the HR from Garmin GPX. Now we have to build all the HRM
        # file
        #

        hrmfile = HRMParser()
        hrmfile.CreateEmpty()

        #
        # fill data.
        #
        hrmfile.sections['Params'].set_altitude(1)
        hrmfile.sections['Params'].set_speed(1)


        if gpx.HasExtensions('cad'):
            hrmfile.sections['Params'].set_cadence(1)

        total_time_s = gpx.get_totaltime()
        gpx_date =  self.UTC2Localtime(points[0].time)#.strftime('%Y%m%d')
        gpx_starttime =self.UTC2Localtime(points[0].time)#.strftime('%H:%M:%S.0')
        gpx_length =  datetime.utcfromtimestamp(total_time_s)#.strftime('%H:%M:%S.0')

        #Params
        #Notes
        #IntTimes
        #ExtraData
        #Summary-123
        #Summary-TH
        #HRZones
        #SwapTimes
        #Trip
        #HRData


        hrmfile.sections['Params'].set_date(gpx_date)
        hrmfile.sections['Params'].set_starttime(gpx_starttime)
        hrmfile.sections['Params'].set_length(gpx_length)

        hrmfile.sections['Params'].set_altitude(True)

        hrmfile.sections['Summary-123'].set_time(total_time_s)
        hrmfile.sections['Summary-TH'].set_time(total_time_s)

        # then, calculate and fill the Trip Area

        hrmfile.sections['Trip'].set_distance       ( gpx.get_distance() )


        hrmfile.sections['Trip'].set_ascent         ( gpx.get_ascent() )
        hrmfile.sections['Trip'].set_totaltime      ( gpx.get_totaltime() )
        hrmfile.sections['Trip'].set_average_alt    ( gpx.get_average_altitude() )
        hrmfile.sections['Trip'].set_max_alt        ( gpx.get_max_alt() )
        hrmfile.sections['Trip'].set_average_speed  ( gpx.get_average_speed()[1] )
        hrmfile.sections['Trip'].set_max_speed      ( gpx.get_max_speed() )
        hrmfile.sections['Trip'].set_odometer       ( gpx.get_distance() )





        # and now, generate the HRData !
        # get first point, add 5 seconds, and get data, until npoints
        # reached.

        npoints = int(math.ceil(total_time_s / float(hrmfile.sections['Params'].interval))) + 1

        hdata = []
        power_values = []

        #
        # GetLocationAt is looking for stamps in LocalTime instead
        # UTC... so the call is wrong. Use the get_location_at_utc instead
        #

        start_date = calendar.timegm(points[0].time.timetuple())

        prev_point = None
        for i in range(0, npoints):

            delta = i*hrmfile.sections['Params'].interval
            gpx_point = gpx.get_location_at_utc( start_date + delta )

            if not hasattr(gpx_point, 'extensions'):
                gpx_point.extensions = prev_point.extensions

            if gpx_point.extensions == None:
                gpx_point.extensions = { 'hr': 0, 'cad': 0, 'power': 0, 'left_torque_effectiveness': 0, 'left_pedal_smoothness': 0, 'speed': 0}

            hr = gpx_point.extensions['hr']
            cad = gpx_point.extensions['cad']
            power = gpx_point.extensions['power']
            left_pedal_smoothness = gpx_point.extensions['left_pedal_smoothness']
            left_torque_effectiveness = gpx_point.extensions['left_torque_effectiveness']

            pbpi_v = 0.0
            if left_pedal_smoothness != None and left_torque_effectiveness != None:
                pbpi_v = (left_pedal_smoothness*256)+left_torque_effectiveness


            if prev_point:
                speed = gpx_point.speed_between(prev_point)
                time_delta = gpx_point.time_difference(prev_point)
                distance_delta = gpx_point.distance_3d(prev_point)

                # fix out of bounds speeds (for example, when sampling > 1 sec)


                if (time_delta > 0 and speed > distance_delta / time_delta):
                    speed = distance_delta / time_delta

                if not speed:
                    speed = 0

                # converted later
                #speed = speed * 3.6 * 10 # (km/h)

            else:
                speed = 0
                time_delta = 0
                distance_delta = 0


            if not cad:
                    cad = 0

            if roller_mode:
                speed = gpx_point.extensions['speed']


                roller_avg_speed += speed
                if speed > roller_max_speed:
                    roller_max_speed = speed



            hitem = [ int(hr), int(speed*3.6*10) ]
            power_values.append( (power, int(math.floor(pbpi_v))) )

            #jmc
            ##print speed, time_delta, distance_delta, "//",  roller_mode, hitem

            if gpx.HasExtensions('cad'): hitem.append(int(cad))

            hitem.append(int(gpx_point.elevation))
            hdata.append(hitem)

            # advance!
            prev_point = gpx_point



        if roller_mode:

            roller_avg_speed = roller_avg_speed/len(hdata)
            hrmfile.sections['Trip'].set_distance       ( gpx.get_antplus_distance() )
            hrmfile.sections['Trip'].set_average_speed  ( roller_avg_speed )
            hrmfile.sections['Trip'].set_max_speed      ( roller_max_speed )



        #
        # everything is done.
        # Equalize All the values and set it into the HRM file.
        #


        hrmfile.sections['HRData'].set_all( self.EqualizeData(hdata) )

        # add power data, if found in gpx.exceptions
        if gpx.has_power_data():

            hrmfile.sections['Params'].set_power(True)
            hrmfile.sections['HRData'].set_power(power_values)


        self.replace_or_overwrite(hrm_file, hrmfile.Export())

        if self.verbose >= 2:
            hrmfile.DebugSections(self.verbose)
            gpxmanager.DebugFiles()

        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s'" % (gpx11_file, hrm_file)))
        return True



    def EqualizeData(self, data):

        j=0
        k=0
        l=0
        for k in range(1, len(data)-1):

            l=k+1
            #
            #
            # iterate all the elements in the container
            # create a refined version so no 0s in the speed
            # to calculate a more averaged distance
            #
            for i in range(len(data[k])):

             if data[j][i] == 0:
                      continue

                      if data[k][i] == 0:
                       e = l
                       while e < len(data)-1 and data[e][i] == 0:
                           e += 1

                       # from k to e all are 0s, so put the last element inside.

                       v = int((data[j][i] + data[e][i]) / 2.0)
                       for w in range(k,e):
                           data[w][i] = v


                    #if data[j][i] > 0 and data[k][i] == 0 and data[l][i] > 0:
                        #
                        # a value in the middle is 0, so calculate
                        # the median
                    #    v = int((data[l][i] + data[j][i]) / 2.0)
                    #    data[k][i] = v

                #
             j=k


            return data



    def UTC2Localtime(self, tobject):
        # changed to put the right hour in the HRM files
        # 19_11_2015

        # return a datetimeobject converted to current localtime
        #return datetime.fromtimestamp( calendar.timegm(tobject.timetuple()) )
        return datetime.fromtimestamp( time.mktime(tobject.timetuple()) )


    #
    # Get a GPX11 file (from another system, e.g. GARMIN)
    # and create a GPX10 compliant file (with elevations, as optional) in order to
    # match the HR data with the altitude. Useful if you train with a 625sx and carries
    # a external gps (e.g GARMIN Etrex)
    #
    # The algorithm to match the files is using the LOCALTIME of HRM, asking to the
    # GPX (in UTC) for the points at given time
    #


    def BuildGPX10fromGPX(self, gpxin, hrm_file, output_file):

        fmode = True
        gpx_file = gpxin
        if not isinstance(gpxin, str):
            fmode = False
            gpx_file = '-'

        #1 read the HRM file, extract params and show data

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))

        hrmfile = HRMParser()
        try:
            hrmfile.ParseFromFile(hrm_file)
        except Exception as e:
            raise Exception("Error parsing HRM %s: %s" % (hrm_file, e))

        if self.verbose >= 1:
            print(self.LOG("Parsed HRMFile '%s'" % hrm_file))


        #2 read the GPX Files and show some data about them

        try:
            gpxmanager = GPXToolBox()
            if fmode == True:
                gpxmanager.LoadFiles(gpx11=gpx_file)
            else:
                gpxmanager.set_gpx11(gpxin)

        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX1 '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))

        #3 FIX the GPX1.0 to GPX.1.1 info, and save it. If overwrite is on
        #save the data in the same file, else, create another one with ele
        #extension.

        xml = ""

        start_date = hrmfile.sections['Params'].date
        start_time = hrmfile.sections['Params'].starttime

        interval   = hrmfile.sections['Params'].interval
        points     = hrmfile.sections['HRData'].len()

        sd = [ start_date[0], start_date[1], start_date[2],
               start_time[0], start_time[1], start_time[2],
               0            , 0            , -1             ]

        sd = list(map (int, sd))

        # pass the start_date to gmt,

        sd = time.mktime(sd)

        #start_time_gmt = time.gmtime(sd)
        start_time = time.localtime(sd)

        try:
            xml = gpxmanager.CreateGPX10FromGPX(start_time, interval, points)
        except Exception as e:
            raise Exception("Error while Converting %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time() - debug_time
                elapsed = time.gmtime(debug_time)
                elapsed = time.strftime("%H:%M:%S",elapsed)
                print(self.LOG("Conversion succesfully added (elapsed time %s)" % elapsed))

        # save the GPX10 file

        self.create_or_overwrite(output_file, xml)

        if self.verbose >= 2:
            hrmfile.DebugSections(self.verbose)
            gpxmanager.DebugFiles()


        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))
        return True

    # buildTCX --- new version

    #
    # Get a valid GPX 1.1 File, and a HRM file, and build
    # the TCX file. For Strava, for example. This function
    # deprecates the old buildTCX data.
    #

    def BuildTCX(self, gpx_file, hrm_file, output_file, activity='biking'):

        #1 read the HRM file, extract params and show data


        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))

        hrmfile = HRMParser()
        try:
            hrmfile.ParseFromFile(hrm_file)
        except Exception as e:
            raise Exception("Error parsing HRM %s: %s" % (hrm_file, e))

        if self.verbose >= 1:
            print(self.LOG("Parsed HRMFile '%s'" % hrm_file))


        #2 read the GPX Files and show some data about them

        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11=gpx_file)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX File '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))

        #3 Build the Preamble and the prologue of the file.


        start_date = hrmfile.sections['Params'].date
        start_time = hrmfile.sections['Params'].starttime

        interval   = hrmfile.sections['Params'].interval

        sd = [ start_date[0], start_date[1], start_date[2],
               start_time[0], start_time[1], start_time[2],
               0            , 0            , -1             ]

        sd = list(map (int, sd))

        # pass the start_date to gmt,

        sd = time.mktime(sd)
        start_time = time.localtime(sd)


        points = []

        for i in range(len(hrmfile.sections['HRData'].items)):
            point = hrmfile.sections['HRData'].items[i]

            speed = 0
            cadence = 0
            hrm = point[0]
            mode = hrmfile.sections['Params'].mode

            if  mode.speed:
                speed = point[1]

            if  mode.cadence:
                if mode.speed:
                   cadence = point[2]
                else:
                   cadence = point[1]

            timepoint = time.mktime(start_time) + (interval*i)
            t_stamp = datetime.utcfromtimestamp(timepoint)

            gps_point = gpxmanager.gpx11.get_location_at(timepoint)
            gps_point.hr = hrm
            gps_point.cadence = cadence

            points.append(gps_point)


        builder = TCXBuilder()
        xml = builder.BuildTCX( os.path.basename(gpx_file), GPXItem(points), activity )

        # save the TCX file

        self.create_or_overwrite(output_file, xml)

        #if self.verbose >= 2:
        #    hrmfile.DebugSections(self.verbose)
        #    gpxmanager.DebugFiles()

        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))
        return True


    #########################################################################
    #
    # CalculateTimeRange Compute the POINT Range fOR HUD
    # calculations. This code is called from GPX and FIT
    # interfaces. Need to write the TCX one (for compatibility)
    # this code can be elsewhere. SKIP same points.
    #
    #########################################################################

    def CalculateTimeRange(self, points, instamp=0, deltat=0, fake_time=False):

        # NOT INSERT BEFORE AND AFTER POINTS (08/07/2016)
        r = []

        if instamp == 0 and deltat == -1 and fake_time== True:
            # get all the points for metrics
            print("Getting al the points")
            for p in points: r.append(p)
            return r


        start_time = instamp
        
        if fake_time:
            start_time = (points[0].time) + timedelta(seconds=instamp)

        end_time = start_time + timedelta(seconds=deltat)

        
        # now, iterate from instamp to deltat.
 
        NoneInserted = True
        for i in range(len(points)):
            p = points[i]

            #putct = (p.time - datetime(1970, 1, 1)).total_seconds()
            #tutc = (start_time - datetime(1970, 1, 1)).total_seconds()
            #print putct, tutc, tutc + deltat
            #if putct >= tutc and putct <= tutc + deltat:

            #if (utc_to_local(points[i+1].time) >= start_time and NoneInserted):
                # insert the previous point to segment
            #    NoneInserted = False
                ##r.append(p)

            # print("--")
            # print(type(p.time))
            # print(p.time)
            # print(type(start_time))
            # print(start_time)
            # print("==")
            if p.time >= start_time and p.time <= end_time:
                if len(r) == 0:
                    r.append(p)
                elif r[-1].latitude != p.latitude or r[-1].longitude != p.longitude or r[-1].time != p.time:
                    r.append(p)
                else:
                    print("Duplicated Point: ", p, r[-1])
                    #r.append(p)

            # hack ... not to run all the points
            if p.time > end_time:
                # insert the current point (last) and go out
                ##r.append(p)
                break

        # debug things

  
        #print("CalculatedTimeRange: START: %s - END: %s (%s) #Points: %d" % \
        #      (start_time, end_time, timedelta(seconds=deltat),len(r)))

        return r,start_time,end_time


        #         print "Get: %d points (%d secs)" % (len(r), deltat)
        #         for i in range(len(r)):
        #             p = r[i]
        #             if i == 0:
        #                 d = 0.0
        #                 ed = 0.0
        #                 g = 0
        #             else:
        #                 A = r[i-1]
        #                 B = p
        #                 ed = p.elevation - r[i-1].elevation
        #                 d = gpxpy.geo.distance( A.latitude, A.longitude, A.elevation,B.latitude, B.longitude, B.elevation, haversine=True)
        #                 #g = 100 * (ed / float(d))
        #                 #g = math.degrees(math.asin(100/141.42)) a perfect 45 degrees (100 ascent, 100 travelled)
        #                 g = math.degrees(math.asin(ed/d))
        #
        #             #print "[POINT] %s -> %s <- %s || %3.2f || %3.2f || %3.2f || %3.2f" % (start_time, utc_to_local(p.time), end_time, p.elevation, d, ed, g)
        #             print p.time, p.elevation, d, ed, p.extensions["hr"], p.extensions["cad"], p.extensions["power"]
        #         return r


    
    #########################################################################
    #
    # GetTimeRange (Create a segment for a given time range, and return it
    # VIDEO HUD project
    # WIP.
    #
    #########################################################################

    def GetTimeRange(self, mode, data_file, instamp, deltat, beginstamp, fake_time=False):
        """
        data_file: the name of the file to be loaded (Garmin FIT)
        instamp: stamp time when the segments start
        deltat: stamp + seconds to end
        """



        if self.verbose >= 1:
            print(self.LOG("START %s '%s' '%s' '%s'" % (mode, data_file, instamp, deltat)))

        #1 read the GPX Files and show some data about them

        if mode == 'fit':
            points = self.FIT2TCX(data_file, None, saveFile=False)
        elif mode == 'gpx':
            try:
                gpxmanager = GPXToolBox()
                gpxmanager.LoadFiles(gpx11=data_file)

            except Exception as e:
                raise Exception("Error while parsing %s: %s" % (data_file, e))
            gpx = gpxmanager.gpx11
            points = gpx.Segment().points

        else:
             raise Exception("Unknown mode: %s", mode)

        # first, get all the points for the BB (maps) for full video
        # then get only working points to process them

        map_r,_,_ = self.CalculateTimeRange(points, beginstamp, deltat)
        r,start_time,end_time = self.CalculateTimeRange(points, instamp, deltat, fake_time)

        
        
        if self.verbose >= 1:
            print(self.LOG("END %s '%s' '%s' '%s'" % (mode, data_file, instamp, deltat)))

        info = EmptyClass()
        info.start_time = start_time
        info.end_time = end_time
        info.points_len = len(r)
        info.points_all = len(points)
        info.gpx_file = data_file
        info.gpx_mode = mode
        
        t_f = lambda x: x

        if mode == "fit":
            # time is in UTC, so change it.
            t_f = lambda x: x

        info.start_time_all = t_f(points[0].time)
        info.end_time_all = t_f(points[-1].time)
        return r,info,map_r


    

    #########################################################################
    #
    # BuildTCXFromGPX ... the real new compliant function
    #
    #########################################################################

    def BuildTCXFromGPX(self, gpx_file, output_file, activity='biking'):

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s'" % (gpx_file, output_file)))

        #1 read the GPX Files and show some data about them

        try:
            
            gpxmanager.LoadFiles(gpx11=gpx_file)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX File '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))

        gpx = gpxmanager.gpx11
        points = gpx.Segment().points

        builder = TCXBuilder()
        xml = builder.BuildTCX( os.path.basename(gpx_file), GPXItem(points), activity )

        # save the TCX file
        self.create_or_overwrite(output_file, xml)


        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s'" % (gpx_file, output_file)))
        return True


    ## until here --



    #
    # Get a valid GPX 1.1 File, with HR and CAD extensions, and do the work
    # deprecated function. Use the previous one instead.
    #


    def AdjustTime(self, gpx_file, hrm_file, output_file):

        #1 read the HRM file, extract params and show data

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))

        hrmfile = HRMParser()
        try:
            hrmfile.ParseFromFile(hrm_file)
        except Exception as e:
            raise Exception("Error parsing HRM %s: %s" % (hrm_file, e))

        if self.verbose >= 1:
            print(self.LOG("Parsed HRMFile '%s'" % hrm_file))


        #2 read the GPX Files and show some data about them

        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11=gpx_file)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX1 '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))

        #3 FIX the GPX1.0 to GPX.1.1 info, and save it. If overwrite is on
        #save the data in the same file, else, create another one with ele
        #extension.

        xml = ""

        start_date = hrmfile.sections['Params'].date
        start_time = hrmfile.sections['Params'].starttime

        interval   = hrmfile.sections['Params'].interval
        points     = hrmfile.sections['HRData'].len()

        sd = [ start_date[0], start_date[1], start_date[2],
               start_time[0], start_time[1], start_time[2],
               0            , 0            , -1             ]

        sd = list(map (int, sd))

        # pass the start_date to gmt,

        sd = time.mktime(sd)

        #start_time_gmt = time.gmtime(sd)
        start_time = time.localtime(sd)

        length = hrmfile.sections['Params'].length
        duration = (length[0] * 3600) + (length[1] * 60) + (length[2])

        # calculate the interval as follows: starttime + length / points.

        interval_median = int(duration / points)

        try:
            xml = gpxmanager.AdjustTime(start_time, interval_median, points)
        except Exception as e:
            raise Exception("Error while Converting %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time() - debug_time
                elapsed = time.gmtime(debug_time)
                elapsed = time.strftime("%H:%M:%S",elapsed)
                print(self.LOG("Conversion succesfully added (elapsed time %s)" % elapsed))

        # save the GPX10 file

        self.create_or_overwrite(output_file, xml)

        if self.verbose >= 2:
            hrmfile.DebugSections(self.verbose)
            gpxmanager.DebugFiles()


        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))
        return True


    #
    # Show info about GPX file
    #


    def GPXInfo(self, gpx_file):

        if self.verbose >= 1:
            print(self.LOG("START '%s'" % (gpx_file)))

        #1 read the GPX Files and show some data about them

        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11=gpx_file)

        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX1 '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))

        if self.verbose >= 1:
                debug_time = time.time() - debug_time
                elapsed = time.gmtime(debug_time)
                elapsed = time.strftime("%H:%M:%S",elapsed)
                print(self.LOG("Conversion succesfully added (elapsed time %s)" % elapsed))


        gpxmanager.DebugFiles()

        if self.verbose >= 1:
            print(self.LOG("END '%s" % (gpx_file)))

        return True


        #
        #
        # debug info. The altitude should be smoothed 2 times, in order to
        # fix the data for GARMIN and STRAVA
        # NOT REACHED
        #

        uph = 0.0
        doh = 0.0
        max = 0
        min = 9999999999999.0

        gpxmanager.gpx11.MergeAll()
        gpxmanager.gpx11.gpx.tracks[0].smooth()
        gpxmanager.gpx11.gpx.tracks[0].smooth()

        points = gpxmanager.gpx11.Segment().points
        for i in range(len(points)-1):
            j = points[i]
            k = points[i+1]
            #k.elevation = math.floor(k.elevation)
            #j.elevation = math.floor(j.elevation)

            if k.elevation >0 and j.elevation>0:
                if k.elevation > j.elevation:
                    uph += (k.elevation-j.elevation)

                if k.elevation < j.elevation:
                    doh += (j.elevation-k.elevation)

                if j.elevation > max: max = j.elevation
                if j.elevation < min: min = j.elevation

        j = points[-1]
        if j.elevation > max: max = j.elevation
        if j.elevation < min: min = j.elevation

        print(uph, doh, max, min)
        return

    # #####################################################################################
    #
    # Parse FitLog file format from GC.
    # Golden Cheetah Roller stores the info in this awkward format. Also
    # let room to add a GPX track of the course, to fake time (in order to
    # create the proper speed and so on).
    #
    # #####################################################################################

    def _fitlog_xml_gData(self, dom, nodename):
        node = dom.getElementsByTagName(nodename)

        if not node:
            return None

        node = node[0]

        return self._fitlog_xml_gTEXT(node)


    def _fitlog_xml_gTEXT(self,nodelist):
        rc = []
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def _fitlog_xml_gAttr(self,node, attrnames):

        rc = []
        return node.getAttribute(attrnames)

    def _fitlog_xml_gChild(self,node, child):

        return node.getElementsByTagName(child)


    def FITLog2GPX(self, fitfile, outputfile):
        """
        BASED ON Speed, Time, Distance, Calculate the FAKE GPX Points?


        <?xml version="1.0"?>
        <FitnessWorkbook xmlns="http://www.zonefivesoftware.com/xmlschemas/FitnessLogbook/v2" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <AthleteLog>
        <Athlete athlete="juanmcasillas"/>
        <Activity StartTime="2015-11-18T20:23:16Z" Id="">
            <Metadata Source="GoldenCheetah"/>
            <Duration TotalSeconds="2400"/>
            <Distance TotalMeters="15474.6"/>
            <Elevation AscendMeters="0"/>
            <HeartRate MaximumBPM="167" AverageBPM="146.907"/>
            <Cadence AverageRPM="82.2657" MaximumRPM="157"/>
            <Power AverageWatts="203.312" MaximumWatts="252"/>
            <Calories TotalCal="487.95"/>
            <Track StartTime="2015-11-18T20:23:16Z">
                <pt hr="0" cadence="0" power="0" ele="0" tm="0" dist="0"/>
                <pt hr="73" cadence="0" power="0" ele="0" tm="1" dist="0"/>
                <pt hr="74" cadence="0" power="0" ele="0" tm="2" dist="0"/>
                <pt hr="75" cadence="41" power="0" ele="0" tm="3" dist="0"/>
                <pt hr="76" cadence="41" power="0" ele="0" tm="4" dist="7.93285"/>
                [...]
            </Track>
            </Activity>
            </AthleteLog>
        </FitnessWorkbook>

        <?xml version="1.0" encoding="UTF-8"?>
        <gpx creator="StravaGPX" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
         <metadata>
          <time>2015-11-18T18:50:31Z</time>
         </metadata>
         <trk>
          <name>Zwift - Richey intervals</name>
          <trkseg>
           <trkpt lat="-11.6397580" lon="166.9478080">
            <ele>7.8</ele>
            <time>2015-11-18T18:50:31Z</time>
            <extensions>
             <gpxtpx:TrackPointExtension>
              <gpxtpx:hr>70</gpxtpx:hr>
              <gpxtpx:cad>52</gpxtpx:cad>
             </gpxtpx:TrackPointExtension>
            </extensions>
           </trkpt>
          </trkseg>
          </trk>
        </gpx>
        """

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s'" % (fitfile, outputfile)))

        try:
            dom = xmlp.parse(fitfile)

        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (fitfile, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded FIT File '%s'" % (fitfile)))


        activity = dom.getElementsByTagName("Activity")[0]
        #starttime = activity.getAttribute("StartTime")
        duration = activity.getElementsByTagName("Duration")[0].getAttribute("TotalSeconds")
        # get other things here if needed...

        track = dom.getElementsByTagName("Track")[0]
        starttime = track.getAttribute("StartTime")

        attrmap = {
                   'hr'     : 'hr',
                   'cadence': 'cad',
                   'power'  : 'power',
                   'ele'    : 'elevation',
                   'tm'     : 'seconds',
                   'dist'   : 'distance',
                   'lat'    : 'latitude',
                   'lon'    : 'longitude'
                   }

        points = []
        for point in track.getElementsByTagName("pt"):

            #p =   GPXTrackPoint(latitude, longitude, altitude, timestamp, extensions={})
            p =   GPXTrackPoint(0, 0, 0, 0, extensions={})

            for a in list(attrmap.keys()):

                p.extensions[attrmap[a]] = point.getAttribute(a)

                #p.extensions['hr'] = heart_rate
                #p.extensions['cad'] = cadence
                # non compliant extensions
                #p.extensions['speed'] = speed
                #p.extensions['temperature'] = temperature
                #p.extensions['power'] = power
                #p.extensions['distance'] = distance
                #p.extensions['left_pedal_smoothness'] = left_pedal_smoothness
                #p.extensions['left_torque_effectiveness'] = left_torque_effectiveness

            #2015-11-18T20:23:16Z

            st = time.strptime(starttime.encode("ascii","ignore"),'%Y-%m-%dT%H:%M:%SZ')
            mk = time.mktime(st)
            mk = mk + int(p.extensions['seconds'])
            p_timestamp = datetime.fromtimestamp(mk)

            distance = p.extensions['distance'] or 0.0
            seconds = p.extensions['seconds'] or 0
            speed = 0.0

            if float(seconds) > 0:
                speed = float(distance) / float(seconds)

            p.extensions['speed'] = speed

            p.latitude  = p.extensions['latitude'] or 0.0
            p.longitude = p.extensions['longitude'] or 0.0
            p.elevation = float(p.extensions['elevation']) or 0.0
            p.time      = p_timestamp


            points.append(p)
            #print p.extensions['hr'], p.extensions['cad'], p.extensions['elevation']


        gpx = GPXItem()
        gpx11_xml = gpx.CreateGPX11(points, trk_name=os.path.basename(outputfile))
        self.create_or_overwrite(outputfile, gpx11_xml)
        if self.verbose >= 1:
            print(self.LOG("Storing '%s' '%s'" % (fitfile, outputfile)))

        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s'" % (fitfile, outputfile)))

        #for element in self.xml2attr.keys():
        #    data = self._xml_gData(dom,element)
        #
        #    CatastroInfo.__dict__[self.xml2attr[element]] = data

    # #####################################################################################
    #
    # some kind of experiment.
    # Map The Lat,Long Elevation from data_file into base_file
    #
    # #####################################################################################

    def accDistance(self, point, distance, track):


        (loc, si, pi) = track.get_nearest_location(point)

        if not point or not loc:
            return (None, None)


        d = gpxpy.geo.length_2d([point, loc])

        while d < distance:
            track.segments[0].points = track.segments[0].points[1:]
            (loc, si, pi) = track.get_nearest_location(loc)
            if not loc:
                return (None, None)
            d += gpxpy.geo.length_2d([point, loc])


        return (track.segments[si].points[pi], track.segments[0].points)






    def MapLatLong(self, basefile, gpxfile, outputfile):

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s' '%s'" % (basefile,gpxfile, outputfile)))

        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(basefile, gpxfile) # 11->base, 10->data
        except Exception as e:
            raise Exception("Error while parsing %s and %s: %s" % (gpx11_file, gpx10_file, e))

        # create a list based on distance, instead of lat,lon



        base_points = gpxmanager.gpx11.gpx.tracks[0].segments[0].points
        data_points = gpxmanager.gpx10.gpx.tracks[0].segments[0].points

        orig_distance = base_points[-1].extensions['distance']

        dlist = [ (0, data_points[0]) ]
        data_distance = 0
        for i in range(0,len(data_points)-1):
            dd = gpxpy.geo.length_3d( [data_points[i], data_points[i+1]] )
            data_distance += dd
            dlist.append ( (data_distance, data_points[i+1]))
            #print data_distance, data_points[i+1]

        if orig_distance > data_distance:
            raise Exception("GPX Should be greater for mapping Lat,Lon (get %3.3fm, expected %3.3f)" % (data_distance, orig_distance))

        # for each point, get the point nearest based on distance.

        base_points[0].latitude = dlist[0][1].latitude
        base_points[0].longitude = dlist[0][1].longitude
        base_points[0].elevation = dlist[0][1].elevation

        k = 0
        for i in range(1,len(base_points)):
            for j in range(k,len(dlist)):
                if dlist[j][0] >= base_points[i].extensions['distance']:
                    base_points[i].latitude = dlist[j][1].latitude
                    base_points[i].longitude = dlist[j][1].longitude
                    base_points[i].elevation = dlist[j][1].elevation
                    k = j # use all the items (uncommented: optimized)
                    break

        gpx11_xml = gpxmanager.gpx11.CreateGPX11(base_points, trk_name=os.path.basename(outputfile))
        self.create_or_overwrite(outputfile, gpx11_xml)
        if self.verbose >= 1:
            print(self.LOG("Storing '%s' '%s'" % (basefile, outputfile)))

        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s' '%s'" % (basefile,gpxfile, outputfile)))

    # #####################################################################################
    #
    # some kind of experiment.
    # FIT2TCX
    # try to read a FIT file and build a GPX 1.1 with POWER,SPEED,CADENCE,TEMPERATURE...
    # extensions, and try to work with. The most accurate aprox should be generate a
    # TCX file, but parsing it is too hard.
    #
    # #####################################################################################

    def FIT_getvalue(self, message, valkey, default=0):
        # adjust the value of value per units, using the default default.

        unitmap = { 'km':     1000,           # to meters
                    'km/h':   0.277777778,    # to m/s
                    'deg':    1,              # keep them
                    'm':      1,
                    'C':      1,
                    'bpm':    1,
                    'rpm':    1,
                    'watts':  1,
                    'percent':1
                 }

        value = message.get(valkey)

        if not value: return default

        value = value.value

        units = message.get(valkey).units


        if value == None: return default
        if not units in list(unitmap.keys()) and units != None: raise Exception("Bad Units %s" % units)

        if units:
            return value * unitmap[units]
        return value

    def FIT2TCX(self, fit_file, output_file, saveFile=True):

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s'" % (fit_file, output_file)))

        try:
            gpxmanager = GPXToolBox()
            fitfile = fitparse.FitFile(fit_file,data_processor=fitparse.StandardUnitsDataProcessor())
            messages = fitfile.get_messages(with_definitions=False, as_dict=False)

        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (fit_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded FIT File '%s'" % (fit_file)))

        #
        # get everything between event type "start" and "stop" useful only records.
        #

        state=0
        points = []
        activity = 'biking'

        for n, message in enumerate(messages, 1):

            if state==0 and message.name == "event" and message.get("event_type").value == "start":
                state = 1
                if self.verbose >= 1:
                    print(self.LOG("* event start found at pos #%d" % (n)))
                continue

            if state==1 and message.name == "event" and message.get("event_type").value == "stop_disable_all":
                state = 2
                if self.verbose >= 1:
                    print(self.LOG("* event stop_disable_all found at pos #%d" % (n)))
                continue

            if state==2 and message.name == "session":
                values = message.get_values()
                activity = self.FIT_getvalue(message, "sport")
                if activity == 'cycling':
                    activity = 'biking'
                break # last message.


            if state==1 and message.name == "record":

                # JMC FIX. Default values for INVALID metrics should be NONE

                distance = self.FIT_getvalue(message, "distance")
                latitude = self.FIT_getvalue(message, "position_lat")
                longitude = self.FIT_getvalue(message, "position_long")
                speed = self.FIT_getvalue(message, "speed")
                altitude = self.FIT_getvalue(message, "altitude")
                heart_rate = self.FIT_getvalue(message, "heart_rate")
                temperature = self.FIT_getvalue(message, "temperature", 0)
                cadence = self.FIT_getvalue(message, "cadence", 0)
                power = self.FIT_getvalue(message, "power", 0)
                left_pedal_smoothness = self.FIT_getvalue(message, "left_pedal_smoothness", 0.0)
                left_torque_effectiveness = self.FIT_getvalue(message, "left_torque_effectiveness", 0.0)
                timestamp = message.get('timestamp').value
                
                #def utc_to_local(utc_dt):
                #    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
                # convert to localtime fit files
                #timestamp = timestamp.replace(tzinfo=timezone.utc).astimezone(tz=None)

                
                p = GPXTrackPoint(latitude, longitude, altitude, timestamp, extensions={})
                p.extensions['hr'] = heart_rate
                p.extensions['cad'] = cadence
                p.extensions['cadence'] = cadence
                # non compliant extensions
                p.extensions['speed'] = speed
                p.extensions['temperature'] = temperature
                p.extensions['atemp'] = temperature
                p.extensions['power'] = power
                p.extensions['distance'] = distance
                p.extensions['left_pedal_smoothness'] = left_pedal_smoothness
                p.extensions['left_torque_effectiveness'] = left_torque_effectiveness

                points.append(p)

                #s = ""
                #print message.name
                #for field_data in message:
                #    s += ' * %s: %s' % (field_data.name, field_data.value)
                #    if field_data.units:
                #        s += ' [%s]' % field_data.units
                #    s += '\n'
                #print s

        # points have the list... so go for it
        #xml = gpxmanager.gpx11.CreateGPX11(points)

        if saveFile:
            builder = TCXBuilder()
            xml = builder.BuildTCX( os.path.basename(fit_file) , GPXItem(points), activity )


            # save the GPX file

            self.create_or_overwrite(output_file, xml)

            if self.verbose >= 1:
                print(self.LOG("END '%s' '%s'" % (fit_file, output_file)))

        return points




    def GuessFITFileName(self, fit_file, pos_index="01"):
        """
        get the first record, use the date to create the name
        """

        if self.verbose >= 1:
            print(self.LOG("START '%s'" % (fit_file)))

        try:
            fitfile = fitparse.FitFile(fit_file,data_processor=fitparse.StandardUnitsDataProcessor())
            messages = fitfile.get_messages(with_definitions=False, as_dict=False)

        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (fit_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded FIT File '%s'" % (fit_file)))

        #
        # get everything between event type "start" and "stop" useful only records.
        #

        state=0
        points = []
        activity = 'biking'

        for n, message in enumerate(messages, 1):

            if state==0 and message.name == "sport":
                 print(self.LOG("* tacx start found at pos #%d" % (n)))
                 state = 10
                 continue
          
            if state==0 and message.name == "event" and message.get("event_type").value == "start":
                state = 1
                print(self.LOG("* event start found at pos #%d" % (n)))
                continue

            if state==1 and message.name == "event" and message.get("event_type").value == "stop_disable_all":
                state = 2
                print(self.LOG("* event stop_disable_all found at pos #%d" % (n)))
                continue

            if state==2 and message.name == "session":
                values = message.get_values()
                activity = self.FIT_getvalue(message, "sport")
                if activity == 'cycling':
                    activity = 'biking'
                break # last message.

            if state==1 and message.name == "record":

                distance = self.FIT_getvalue(message, "distance")
                latitude = self.FIT_getvalue(message, "position_lat")
                longitude = self.FIT_getvalue(message, "position_long")
                speed = self.FIT_getvalue(message, "speed")
                altitude = self.FIT_getvalue(message, "altitude")
                heart_rate = self.FIT_getvalue(message, "heart_rate")
                temperature = self.FIT_getvalue(message, "temperature", 0)
                cadence = self.FIT_getvalue(message, "cadence", 0)
                power = self.FIT_getvalue(message, "power", 0)
                left_pedal_smoothness = self.FIT_getvalue(message, "left_pedal_smoothness", 0.0)
                left_torque_effectiveness = self.FIT_getvalue(message, "left_torque_effectiveness", 0.0)
                timestamp = message.get('timestamp').value

                p =   GPXTrackPoint(latitude, longitude, altitude, timestamp, extensions={})
                p.extensions['hr'] = heart_rate
                p.extensions['cad'] = cadence
                p.extensions['cadence'] = cadence
                # non compliant extensions
                p.extensions['speed'] = speed
                p.extensions['temperature'] = temperature
                p.extensions['atemp'] = temperature
                p.extensions['power'] = power
                p.extensions['distance'] = distance
                p.extensions['left_pedal_smoothness'] = left_pedal_smoothness
                p.extensions['left_torque_effectiveness'] = left_torque_effectiveness

                points.append(p)
                break # get the first one

            if state==10 and message.name == "record":
                distance = self.FIT_getvalue(message, "distance")
                latitude = self.FIT_getvalue(message, "position_lat")
                longitude = self.FIT_getvalue(message, "position_long")
                speed = self.FIT_getvalue(message, "speed")
                altitude = self.FIT_getvalue(message, "altitude")
                heart_rate = self.FIT_getvalue(message, "heart_rate")
                temperature = self.FIT_getvalue(message, "temperature", 0)
                cadence = self.FIT_getvalue(message, "cadence", 0)
                power = self.FIT_getvalue(message, "power", 0)
                left_pedal_smoothness = self.FIT_getvalue(message, "left_pedal_smoothness", 0.0)
                left_torque_effectiveness = self.FIT_getvalue(message, "left_torque_effectiveness", 0.0)
                timestamp = message.get('timestamp').value

                p =   GPXTrackPoint(latitude, longitude, altitude, timestamp, extensions={})
                p.extensions['hr'] = heart_rate
                p.extensions['cad'] = cadence
                p.extensions['cadence'] = cadence
                # non compliant extensions
                p.extensions['speed'] = speed
                p.extensions['temperature'] = temperature
                p.extensions['atemp'] = temperature
                p.extensions['power'] = power
                p.extensions['distance'] = distance
                p.extensions['left_pedal_smoothness'] = left_pedal_smoothness
                p.extensions['left_torque_effectiveness'] = left_torque_effectiveness

                points.append(p)
                # tacx      

       
        gpx_date =  self.UTC2Localtime(points[0].time)#.strftime('%Y%m%d')
        fname = gpx_date.strftime("%y%m%d__POS__")
        fname = fname.replace("__POS__", pos_index)

        if self.verbose >= 1:
            print(self.LOG("END '%s' -> '%s'" % (fit_file,fname)))

        return fname

  #
  # wrapper to generate everything needed to create the tcx, the hrm, the slim gpx11 and the slim
  # gpx10, and tcx
  #

    def FIT2All(self, fit_file, output_dir, tcxfile=True, hrmfile=True):
        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s'" % (fit_file, output_dir)))

        try:
            fitfile = fitparse.FitFile(fit_file,data_processor=fitparse.StandardUnitsDataProcessor())
            messages = fitfile.get_messages(with_definitions=False, as_dict=False)
            m2 = fitfile.get_messages(with_definitions=True, as_dict=True)
            #for m in m2:
                #print m, m.name


        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (fit_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded FIT File '%s'" % (fit_file)))

        #
        # get everything between event type "start" and "stop" useful only records.
        #

        state=0
        points = []
        activity = 'biking'

        for n, message in enumerate(messages, 1):

            if state==0 and message.name == "sport":
                 print(self.LOG("* tacx start found at pos #%d" % (n)))
                 state = 1
                 continue

            if state==0 and message.name == "event" and message.get("event_type").value == "start":
                state = 1
                if self.verbose >= 1:
                    print(self.LOG("* event start found at pos #%d" % (n)))
                continue

            if state==1 and message.name == "event" and message.get("event_type").value == "stop_disable_all":
                state = 2
                if self.verbose >= 1:
                    print(self.LOG("* event stop_disable_all found at pos #%d" % (n)))
                continue

            if state==2 and message.name == "session":
                values = message.get_values()
                activity = self.FIT_getvalue(message, "sport")
                if activity == 'cycling':
                    activity = 'biking'
                break # last message.


            if state==1 and message.name == "record":

                distance = self.FIT_getvalue(message, "distance")
                latitude = self.FIT_getvalue(message, "position_lat")
                longitude = self.FIT_getvalue(message, "position_long")
                speed = self.FIT_getvalue(message, "speed")
                altitude = self.FIT_getvalue(message, "altitude")
                heart_rate = self.FIT_getvalue(message, "heart_rate")
                temperature = self.FIT_getvalue(message, "temperature", 0)
                cadence = self.FIT_getvalue(message, "cadence", 0)
                power = self.FIT_getvalue(message, "power", 0)
                timestamp = message.get('timestamp').value
                left_pedal_smoothness = self.FIT_getvalue(message, "left_pedal_smoothness", 0.0)
                left_torque_effectiveness = self.FIT_getvalue(message, "left_torque_effectiveness", 0.0)

                if self.roller:
                    latitude = 0
                    longitude = 0

                p =   GPXTrackPoint(latitude, longitude, altitude, timestamp, extensions={})
                p.extensions['hr'] = heart_rate
                p.extensions['cad'] = cadence
                p.extensions['cadence'] = cadence
                # non compliant extensions
                p.extensions['speed'] = speed
                p.extensions['temperature'] = temperature
                p.extensions['atemp'] = temperature
                p.extensions['power'] = power
                p.extensions['distance'] = distance
                p.extensions['left_pedal_smoothness'] = left_pedal_smoothness
                p.extensions['left_torque_effectiveness'] = left_torque_effectiveness

                points.append(p)


        # create a gpx container to do all the work.

        gpx = GPXItem(points)

        woutput_dir, wext = os.path.splitext(output_dir)

        # save the GPX11 file (strict)
        # use our custom storer to add hr and cad

        gpx11_out = woutput_dir + ".gpx"
        gpx11_xml = gpx.CreateGPX11(points, trk_name=os.path.basename(woutput_dir))
        self.create_or_overwrite(gpx11_out, gpx11_xml)
        if self.verbose >= 1:
            print(self.LOG("Storing '%s' '%s'" % (fit_file, gpx11_out)))


        if tcxfile:
            builder = TCXBuilder()
            tcx_xml = builder.BuildTCX( os.path.basename(fit_file), gpx , activity)
            tcx_out = output_dir + ".tcx"

            # save the TCX file

            self.create_or_overwrite(tcx_out, tcx_xml)
            if self.verbose >= 1:
                print(self.LOG("Storing '%s' '%s'" % (fit_file, tcx_out)))

        if hrmfile:
            # save the HRM file - Note that the GPX11 is overwritten.
            hrm_out = output_dir + ".hrm"

            self.GPX2HRM(gpx, hrm_out)
            if self.verbose >= 1:
                print(self.LOG("Storing '%s' '%s'" % (fit_file, hrm_out)))

            # save the Polar GPX10 file
            gpx10_out = output_dir + ".gpx"
            self.BuildGPX10fromGPX(gpx,hrm_out,gpx10_out)
            if self.verbose >= 1:
                print(self.LOG("Storing '%s' '%s'" % (fit_file, gpx10_out)))


        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s'" % (fit_file, output_dir)))

        return True


































    # #####################################################################################
    #
    # DEPRECATED STUFF -- don't delete ... for now
    #
    # #####################################################################################

    def BuildTCXFromGPX_OLD(self, gpx_file, output_file):

        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s'" % (gpx_file, output_file)))

        #1 read the GPX Files and show some data about them

        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11=gpx_file)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX File '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))


        gpx = gpxmanager.gpx11
        points = gpx.Segment().points

        xml = gpx.CreateGPX11(points)

        # save the TCX file

        self.create_or_overwrite(output_file, xml)


        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s'" % (gpx_file, output_file)))
        return True


    #
    # Get a valid GPX 1.1 File, and a HRM file, and build
    # the TCX file. For Strava, for example. Deprecated function
    # new one creates a real TCX file with power, speed and so
    # on. Don't use this one.
    #

    def BuildTCX_OLD(self, gpx_file, hrm_file, output_file):

        #1 read the HRM file, extract params and show data


        if self.verbose >= 1:
            print(self.LOG("START '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))

        hrmfile = HRMParser()
        try:
            hrmfile.ParseFromFile(hrm_file)
        except Exception as e:
            raise Exception("Error parsing HRM %s: %s" % (hrm_file, e))

        if self.verbose >= 1:
            print(self.LOG("Parsed HRMFile '%s'" % hrm_file))


        #2 read the GPX Files and show some data about them

        try:
            gpxmanager = GPXToolBox()
            gpxmanager.LoadFiles(gpx11=gpx_file)
        except Exception as e:
            raise Exception("Error while parsing %s: %s" % (gpx_file, e))

        if self.verbose >= 1:
                debug_time = time.time()
                print(self.LOG("Loaded GPX File '%s' (%d points)" % (gpx_file, gpxmanager.get_gpx11_points_no())))

        #3 Build the Preamble and the prologue of the file.


        start_date = hrmfile.sections['Params'].date
        start_time = hrmfile.sections['Params'].starttime

        interval   = hrmfile.sections['Params'].interval

        sd = [ start_date[0], start_date[1], start_date[2],
               start_time[0], start_time[1], start_time[2],
               0            , 0            , -1             ]

        sd = list(map (int, sd))

        # pass the start_date to gmt,

        sd = time.mktime(sd)
        start_time = time.localtime(sd)


        points = []

        for i in range(len(hrmfile.sections['HRData'].items)):
            point = hrmfile.sections['HRData'].items[i]

            speed = 0
            cadence = 0
            hrm = point[0]
            mode = hrmfile.sections['Params'].mode

            if  mode.speed:
                speed = point[1]

            if  mode.cadence:
                if mode.speed:
                   cadence = point[2]
                else:
                   cadence = point[1]

            timepoint = time.mktime(start_time) + (interval*i)
            t_stamp = datetime.utcfromtimestamp(timepoint)

            gps_point = gpxmanager.gpx11.get_location_at(timepoint)
            gps_point.hr = hrm
            gps_point.cadence = cadence

            points.append(gps_point)

        xml = gpxmanager.gpx11.CreateGPX11(points)


        # save the TCX file

        self.create_or_overwrite(output_file, xml)

        #if self.verbose >= 2:
        #    hrmfile.DebugSections(self.verbose)
        #    gpxmanager.DebugFiles()

        if self.verbose >= 1:
            print(self.LOG("END '%s' '%s' '%s'" % (gpx_file, hrm_file, output_file)))
        return True

