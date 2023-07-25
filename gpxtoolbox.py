#!/usr/bin/env python
#
# gpx to gpx-polar file format. Add the Elevation data and make it compliant
# with the PolarProtrainer format
#
# http://www.topografix.com/gpx_manual.asp (version 1.0)
#
#
#GPX extracted from PolarPersonalTrainer (GPX 1.1)
#
#<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
#
#<gpx xmlns="http://www.topografix.com/GPX/1/1"
#	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#	creator="http://www.polarpersonaltrainer.com"
#	version="1.1"
#	xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
#
#    <metadata>
#        <name>Running</name>
#        <author>
#            <name>Juan M. Casillas</name>
#        </author>
#        <time>2014-05-31T11:21:34.648Z</time>
#        <bounds maxlon="-3.746017" maxlat="40.384592" minlon="-3.784258" minlat="40.332592"/>
#    </metadata>
#
#    <trk>
#        <trkseg>
#            <trkpt lon="-3.746017" lat="40.332592">
#                <ele>635.84</ele>
#                <time>2014-05-30T18:11:13.000Z</time>
#                <sat>4</sat>
#            </trkpt>
#
#
#GPX generated from RCX5 to the directory (GPX 1.0)
#
#<?xml version="1.0" encoding="UTF-8"?>
#<gpx
#	  xmlns="http://www.topografix.com/GPX/1/0"
#	  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#	  creator="Polar WebSync 2.4 - www.polar.fi"
#	  version="1.0"
#     xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
#
#  <time>2014-05-30T20:11:17Z</time>
#  <trk>
#    <name>exercise</name>
#    <trkseg>
#      <trkpt lat="40.332591667" lon="-3.746016667">
#        <time>2014-05-30T20:11:17Z</time>
#        <fix>2d</fix>
#        <sat>4</sat>
#      </trkpt>
#
# TODO
# add time from HRM file (DATETHOURZ) format UTC
# remove metadata info
# Add the ele element (elevation)
#

import time
from datetime import datetime
from datetime import timedelta
import copy
import sys
import math
import random

import gpxpy
import gpxpy.gpx
import gpxpy.geo
import calendar

class GPXItem:
  def __init__(self, points=None):
    self.gpx = None
    self.gpx_fname = None

    if points:
      self.LoadFromPoints(points)


  def Load(self, fname):

    self.gpx_fname = fname
    gpx_f = open(self.gpx_fname, 'r')
    self.gpx = gpxpy.parse(gpx_f)
    gpx_f.close()

  def LoadFromString(self, data):

    self.gpx_fname = "-"
    self.gpx = gpxpy.parse(data)


  def LoadFromPoints(self, points, version="1.1"):
    self.gpx_fname = "-"
    self.gpx = gpxpy.gpx.GPX()
    self.gpx.tracks.append(gpxpy.gpx.GPXTrack())
    self.gpx.tracks[0].segments.append(gpxpy.gpx.GPXTrackSegment())
    self.gpx.tracks[0].segments[0].points = points
    self.gpx.version = version

  def HasExtensions(self, extname=None):
    return self.gpx.tracks[0].HasExtensions(extname)

  def Version(self):
    return self.gpx.version

  def MergeAll(self):
      
    while len(self.gpx.tracks)>0 and len(self.gpx.tracks[0].segments) > 1:
      self.gpx.tracks[0].join(0,1)

  def Bounds(self):
    return self.gpx.get_bounds()

  def Center(self):
    return self.gpx.tracks[0].get_center()


  def Track(self):
    return self.gpx.tracks[0]

  def Segment(self):
    return self.gpx.tracks[0].segments[0]

  def Smooth(self):
    #smooth(self, vertical=True, horizontal=False, remove_extremes=False)
    self.gpx.tracks[0].smooth()


  def UTCTime(self, timedata):
    #
    # time comes: 2014-05-30 20:11:27
    # should be formatted to 2014-05-30T20:11:17Z
    #
    
    return timedata.strftime("%Y-%m-%dT%H:%M:%SZ")

  def UTC2Local(self, utc_datetime):
    # GPX 1.1 comes with dates in UTC
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)

    if not utc_datetime:
        # if not data, create the data from today (dummy)
        # jmc fix 14/09/2016
        return datetime.today() + offset

    return utc_datetime + offset

  def GMT2Local(self, gmt):
    return gmt

  def to_xml(self):
    return self.gpx.to_xml()


  def CreateGPX11(self, points, trk_name="exercise", trk_satellite=4, trk_fix='2d'):

    """
    Creates a GPX in 1.1 Format
    """

    xml  = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
    gpx_attr = [
                'xmlns="http://www.topografix.com/GPX/1/1"' ,
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' ,
                'xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1"' ,
                'xmlns:gpxtrx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"' ,
                'xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v2"' ,
                'xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"' ,
                'xmlns:trp="http://www.garmin.com/xmlschemas/TripExtensions/v1"' ,
                'xmlns:adv="http://www.garmin.com/xmlschemas/AdventuresExtensions/v1"' ,
                'xmlns:prs="http://www.garmin.com/xmlschemas/PressureExtension/v1"' ,
                'xmlns:tmd="http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1"' ,
                'xmlns:vptm="http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1"' ,
                'xmlns:ctx="http://www.garmin.com/xmlschemas/CreationTimeExtension/v1"' ,
                'xmlns:gpxacc="http://www.garmin.com/xmlschemas/AccelerationExtension/v1"',
        'xmlns:gpxpx="http://www.garmin.com/xmlschemas/PowerExtension/v1"',
        'xmlns:vidx1="http://www.garmin.com/xmlschemas/VideoExtension/v1"',

                'creator="Garmin Desktop App"' ,
                'version="1.1"' ,
                'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v2 http://www.garmin.com/xmlschemas/TrackPointExtensionv2.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v1 http://www8.garmin.com/xmlschemas/ActivityExtensionv1.xsd http://www.garmin.com/xmlschemas/AdventuresExtensions/v1 http://www8.garmin.com/xmlschemas/AdventuresExtensionv1.xsd http://www.garmin.com/xmlschemas/PressureExtension/v1 http://www.garmin.com/xmlschemas/PressureExtensionv1.xsd http://www.garmin.com/xmlschemas/TripExtensions/v1 http://www.garmin.com/xmlschemas/TripExtensionsv1.xsd http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1 http://www.garmin.com/xmlschemas/TripMetaDataExtensionsv1.xsd http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1 http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensionsv1.xsd http://www.garmin.com/xmlschemas/CreationTimeExtension/v1 http://www.garmin.com/xmlschemas/CreationTimeExtensionsv1.xsd http://www.garmin.com/xmlschemas/AccelerationExtension/v1 http://www.garmin.com/xmlschemas/AccelerationExtensionv1.xsd http://www.garmin.com/xmlschemas/PowerExtension/v1 http://www.garmin.com/xmlschemas/PowerExtensionv1.xsd http://www.garmin.com/xmlschemas/VideoExtension/v1 http://www.garmin.com/xmlschemas/VideoExtensionv1.xsd"'
                ]

  	# BASECAMP:
  	# - doesn't support hr=0
  	# - doesn't support tags:
  	# <gpxtpx:speed>1.0</gpxtpx:speed>
    # <gpxtpx:distance>0</gpxtpx:distance>

    xml += "<gpx " + " ".join(gpx_attr) + ">\r\n"

  
    xml += "<metadata>\r\n"
    xml += "  <time>%s</time>\r\n" % self.UTCTime(points[0].time) # first point !
    xml += "</metadata>\r\n"
    xml += "<trk>\r\n"
    xml += "  <name>%s</name>\r\n" % trk_name
    xml += "<trkseg>\r\n"

    #
    # add the points
    #

    #  <trkpt lat="40.327363333" lon="-3.760243333">
    #    <time>2014-06-26T18:40:45Z</time>
    #    <fix>2d</fix>
    #    <sat>7</sat>
    #  </trkpt>

    for p in points:

      if hasattr(p,'extensions') and p.extensions != None:
          hr = p.extensions['hr']
          cadence = p.extensions['cad']
          speed = p.extensions['speed']
          distance = p.extensions['distance']
      else:
        if hasattr(p, 'hr'):
           hr = p.hr
        else:
           hr = 0
        if hasattr(p, 'cadence'):
           cadence = p.cadence
        else:
           cadence = 0
        speed = 0
        distance = 0

      pts  = '	<trkpt lat="%s" lon="%s">\r\n' % (p.latitude, p.longitude)
      pts += '		<ele>%s</ele>\r\n' % p.elevation
      pts += '		<time>%s</time>\r\n' % self.UTCTime(p.time)
      pts += '		<extensions>\r\n'
      pts += '		<gpxtpx:TrackPointExtension>\r\n'

#			if hr > 0:
      pts += '		    <gpxtpx:hr>%s</gpxtpx:hr>\r\n' % hr

      pts += '		    <gpxtpx:cad>%s</gpxtpx:cad>\r\n' % cadence
      # ## added ... compliant???
      pts += '		    <gpxtpx:speed>%s</gpxtpx:speed>\r\n' % speed
      pts += '		    <gpxtpx:distance>%s</gpxtpx:distance>\r\n' % distance
      pts += '		   </gpxtpx:TrackPointExtension>\r\n'
      pts += '		<gpxx:TrackPointExtension/>\r\n' ## new

#			pts += '        <power>200</power>\r\n' ##
#			pts += '        <temp>27</temp>\r\n'    ##
      pts += '		</extensions>\r\n'
      pts += '	</trkpt>\r\n'

      xml += pts

    xml += "</trkseg>\r\n"
    xml += "</trk>\r\n"
    xml += "</gpx>\r\n"

    return xml


  def CreatePolarXML(self, points, trk_name="exercise", trk_satellite=4, trk_fix='2d', extensions=False):
    """
    Creates a GPX in 1.0 Format, compliant with Polar ProTrainer Input
    """

    xml  = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
    gpx_attr = [
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        'version="1.0"',
        'xmlns="http://www.topografix.com/GPX/1/0"',
        'creator="Polar WebSync 2.4 - www.polar.fi"' ,
        'xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd"'
        ]


    xml += "<gpx " + " ".join(gpx_attr) + ">\r\n"

    xml += "<time>%s</time>\r\n" % self.UTCTime(points[0].time) # first point !
    xml += "<trk>\r\n"
    xml += "<name>%s</name>\r\n" % trk_name
    xml += "<trkseg>\r\n"

    #
    # add the points
    #

    #  <trkpt lat="40.327363333" lon="-3.760243333">
    #    <time>2014-06-26T18:40:45Z</time>
    #    <fix>2d</fix>
    #    <sat>7</sat>
    #  </trkpt>

    for p in points:
      pts  = '	<trkpt lat="%s" lon="%s">\r\n' % (p.latitude, p.longitude)
      pts += '		<time>%s</time>\r\n' % self.UTCTime(p.time)
      pts += '		<ele>%s</ele>\r\n' % p.elevation
      pts += '		<sat>%s</sat>\r\n' % trk_satellite
      pts += '		<fix>%s</fix>\r\n' % trk_fix

      if extensions:
        pts += '		<extensions>\r\n'
        pts += '		    <gpxdata:hr>%s</gpxdata:hr>\r\n' % p.hr
        pts += '		    <gpxdata:cadence>%s</gpxdata:cadence>\r\n' % p.cadence
        pts += '		</extensions>\r\n'



      pts += '	</trkpt>\r\n'

      xml += pts

    xml += "</trkseg>\r\n"
    xml += "</trk>\r\n"
    xml += "</gpx>\r\n"

    return xml




  def Print(self):

    r = ""

    # fn:	filename
    # fd:	gpx data
    # ff:	version "GPX 1.0"


    MangleTime = self.GMT2Local
    if self.Version() == "1.1":
        MangleTime = self.UTC2Local


    r += "GPX {}: {}\r\n".format( self.Version(), self.gpx_fname )
    r += "=" * 80 + "\r\n"
    r += "{:<20} {:>59}\r\n".format( "Number of Points",	self.gpx.tracks[0].get_points_no() )
    ts, te = self.gpx.tracks[0].get_time_bounds()
    r += "{:<20} {:>59}\r\n".format( "Time Bounds", 		"S:%s E:%s" % (MangleTime(ts).strftime("%H:%M:%S"), MangleTime(te).strftime("%H:%M:%S") ))
    r += "{:<20} {:>59}\r\n".format( "Start Date", 			"%s" % (MangleTime(self.gpx.tracks[0].segments[0].points[0].time).strftime("%Y/%m/%d")) )
    r += "{:<20} {:>59}\r\n".format( "Start Time", 			"%s" % (MangleTime(self.gpx.tracks[0].segments[0].points[0].time).strftime("%H:%M:%S")) )


    r += "-" * 80 + "\r\n"
    r += "{:<20} {:>59}\r\n".format( "Duration", 			"%s" % (time.strftime("%H:%M:%S",time.gmtime(self.gpx.tracks[0].get_duration()))) )

    moving_data = self.gpx.tracks[0].get_moving_data()
    average_speed, average_speed_m = self.gpx.tracks[0].get_average_speed()
    climb_info = self.gpx.tracks[0].get_uphill_downhill()
    altitudes = self.gpx.tracks[0].get_elevation_extremes()

    min_alt = 'N/A'
    max_alt = 'N/A'
    if altitudes.maximum != None:  max_alt = "%3.2fm" % altitudes.maximum
    if altitudes.minimum != None:  min_alt = "%3.2fm" % altitudes.minimum





    r += "{:<20} {:>59}\r\n".format( "Time (Moving)", 		"%s" % (time.strftime("%H:%M:%S",time.gmtime( moving_data.moving_time  ))) )
    if moving_data.stopped_time > 0:
        r += "{:<20} {:>59}\r\n".format( "Time (Stopped)", 		"%s" % (time.strftime("%H:%M:%S",time.gmtime(  ))) )
    else:
        r += "{:<20} {:>59}\r\n".format( "Time (Stopped)",         "%s" % ("00:00:00"))
    r += "{:<20} {:>59}\r\n".format( "3D Distance", "%3.2f m (%3.2f Km)" % (self.gpx.tracks[0].length_3d(),self.gpx.tracks[0].length_3d()/1000) )
    r += "{:<20} {:54.2f} km/h\r\n".format( "MaxSpeed (km/h)", 	 moving_data.max_speed * 3.6 )
    r += "{:<20} {:54.2f} km/h\r\n".format( "Average (km/h)", 	 average_speed * 3.6 )
    r += "{:<20} {:53.2f} km/h\r\n".format( "Average Moving (km/h)", 	 average_speed_m * 3.6 )
    r += "{:<20} {:>59}\r\n".format( "Max Altitude", max_alt   )
    r += "{:<20} {:>59}\r\n".format( "Min Altitude", min_alt   )
    r += "{:<20} {:58.2f}m\r\n".format( "Ascent", 		climb_info.uphill   )

    r += "-" * 80 + "\r\n"

    r += "{:<20} {:>59}\r\n".format( "Distance (Moving)",   "%3.2f m (%3.2f Km)" % (moving_data.moving_distance,moving_data.moving_distance/1000) )
    r += "{:<20} {:>59}\r\n".format( "Distance (Stopped)", 	 "%3.2f m (%3.2f Km)" % (moving_data.stopped_distance,moving_data.stopped_distance/1000) )

    r += "{:<20} {:>59}\r\n".format( "2D Distance", "%3.2f m (%3.2f Km)" % (self.gpx.tracks[0].length_2d(),self.gpx.tracks[0].length_2d()/1000) )
    r += "{:<20} {:58.2f}m\r\n".format( "Descent", 		climb_info.downhill )


    #ascend, descend = self.get_ascend_descend()
    #r += "{:<20} {:58.2f}m\r\n".format( "Ascent*", 		ascend   )
    #r += "{:<20} {:58.2f}m\r\n".format( "Descent*", 		descend )






    r += "\r\n"
    return r


  # getters to retrieve important data
  def has_power_data(self):
    return self.gpx.tracks[0].HasExtensions('power')

  def get_distance(self):
    return self.gpx.tracks[0].length_3d()				# return 3D data (counting altitude information)

  def get_distance_2d(self):
    return self.gpx.tracks[0].length_2d()				#

  def get_antplus_distance(self):
    return self.gpx.tracks[0].antplus_distance() # ant+ accumulated distance in meters (extension)

  def get_ascent(self):
    climb_info = self.gpx.tracks[0].get_uphill_downhill()
    return climb_info.uphill

  def get_totaltime(self):
    return self.gpx.tracks[0].get_duration() or 0

  def get_average_altitude(self):
    return self.gpx.tracks[0].get_average_altitude()

  def get_max_alt(self):
    altitudes = self.gpx.tracks[0].get_elevation_extremes()
    return altitudes.maximum

  def get_min_alt(self):
    altitudes = self.gpx.tracks[0].get_elevation_extremes()
    return altitudes.minimum

  def get_average_speed(self):
    return self.gpx.tracks[0].get_average_speed()

  def get_max_speed(self):
    moving_data = self.gpx.tracks[0].get_moving_data()
    return moving_data.max_speed

  def get_points_no(self):
    return self.gpx.tracks[0].get_points_no()

  def get_points(self):
    return self.gpx.tracks[0].segments[0].points
  # for inittimes

  def get_location_at(self, timepoint):

    d = datetime.fromtimestamp(timepoint)
    r = self.gpx.tracks[0].get_location_at(d)

    if len(r) == 0:
      #
      # last point reached (lap time is the last one)
      # return the last point info with altitude data
      #
      pindex = -1
      p = self.gpx.tracks[0].segments[0].points[pindex]
      while p.elevation == 0 and math.fabs(pindex) < self.gpx.tracks[0].get_points_no():
        p = self.gpx.tracks[0].segments[0].points[pindex]
        pindex -= 1
      return p

    return r[0]

  def get_location_at_utc(self, timepoint):

    d = datetime.utcfromtimestamp(timepoint)
    r = self.gpx.tracks[0].get_location_at(d)

    if len(r) == 0:
      #
      # last point reached (lap time is the last one)
      # return the last point info with altitude data
      #
      pindex = -1
      p = self.gpx.tracks[0].segments[0].points[pindex]
      while p.elevation == 0 and math.fabs(pindex) < self.gpx.tracks[0].get_points_no():
        p = self.gpx.tracks[0].segments[0].points[pindex]
        pindex -= 1
      return p

    return r[0]

  # for hrdata

  def get_speed_for_all_points(self):
    r = [ 0.0] # first point is 0 speed, of course :D

    for p in range(1,len(self.gpx.tracks[0].segments[0].points)):
      speed = self.gpx.tracks[0].segments[0].get_speed(p)
      r.append(speed)
    return r

  def get_elevation_for_all_points(self):
    r = [ ]
    for p in range(len(self.gpx.tracks[0].segments[0].points)):
      elevation = self.gpx.tracks[0].segments[0].points[p].elevation
      r.append(elevation)
    return r

  def get_ascend_descend(self):
    #
    # create a calculation about the ascend/descend information
    # returns a tuple (uphill, downhill) in m
    #

    ascend = 0.0
    descend = 0.0
    plen = len(self.gpx.tracks[0].segments[0].points)

    j = 0
    k = 1
    while  k < plen-1:

      jv = self.gpx.tracks[0].segments[0].points[j].elevation
      kv = self.gpx.tracks[0].segments[0].points[k].elevation

      # j -> previous point
      # k -> middle point
      #
      #  j ----- k
      #
      # climb_if: k>j
      # dive_if: j<j


      if kv > jv and kv > 0 and jv > 0:
          ascend += (kv-jv)
      if jv > kv and kv > 0 and jv > 0:
          descend += (jv-kv)

      j = k
      k += 1



    return (ascend, descend)







#############################






class GPXToolBox:
  def __init__(self):
    self.gpx10 = GPXItem()
    self.gpx11 = GPXItem()


  def LoadFiles(self, gpx11=None, gpx10=None):

    self.gpx11_src =  gpx11
    self.gpx10_src =  gpx10
    self.gpx11 	   =  GPXItem()
    self.gpx10	   =  GPXItem()

    if self.gpx11_src:
      self.gpx11.Load(self.gpx11_src)
      self.gpx11.MergeAll()
      self.gpx11.Smooth()

    if self.gpx10_src:
      self.gpx10.Load(self.gpx10_src)
      self.gpx10.MergeAll()
      self.gpx10.Smooth()

  def LoadFromPoints(self, gpx11=None, gpx10=None):

    self.gpx11_src =  gpx11
    self.gpx10_src =  gpx10
    self.gpx11 	   =  GPXItem()
    self.gpx10	   =  GPXItem()

    if self.gpx11_src:
      self.gpx11.LoadFromPoints(self.gpx11_src)
      self.gpx11.MergeAll()
      self.gpx11.Smooth()
      self.gpx11_src ="-"

    if self.gpx10_src:
      self.gpx10.LoadFromPoints(self.gpx10_src)
      self.gpx10.MergeAll()
      self.gpx10.Smooth()
      self.gpx10_src = "-"

  def set_gpx11(self, gpx):
      self.gpx11_src = "-"
      self.gpx11 = gpx
      self.gpx11.MergeAll()
      self.gpx11.Smooth()

  def set_gpx10(self, gpx):
      self.gpx10_src = "-"
      self.gpx10 = gpx
      self.gpx10.MergeAll()
      self.gpx10.Smooth()


  def GPX11toGPX10(self, gpx11_src, gpx10_src):

    self.LoadFiles(gpx11_src, gpx10_src)
    return self.ConvertLoadedFiles()


  def ConvertLoadedFiles(self):

    # merge all tracks, all segments

    self.gpx11.MergeAll()

    segment11 = self.gpx11.Segment()
    segment10 = self.gpx10.Segment()

    min_alt = self.gpx11.get_min_alt()


    for i in range(len(segment10.points)):
      (d,t_segment, t_point) = self.gpx11.Track().get_nearest_location(segment10.points[i])
      segment10.points[i].elevation = self.gpx11.Track().segments[t_segment].points[t_point].elevation

      # if elevation == 0, set the minimum altitude here.
      if segment10.points[i].elevation == 0:
        segment10.points[i].elevation = min_alt


    #
    # elevation fixed inside the track
    # now create the XML GPX 1.0 compliant (useful then to generate the HRM data)
    #

    xml_data = self.gpx10.CreatePolarXML(segment10.points)

    #for gpx10_point in segment10.points:
    #		print 'Point SRC at ({0},{1}) -> {2}'.format(gpx10_point.latitude, gpx10_point.longitude, gpx10_point.elevation)

    return xml_data





  def CreateGPX10FromGPX(self, start_time, interval, points):
    """
    get all the data in gpx11, and build a GPX10 file. Use the start_time as
    start point, then increment the date using interval (in seconds) and the
    number of times is the number of points

    start_time: datetime strcture in GMT time (UTC)
    interval:	seconds
    points:		number of points (interations)

    start_time + 0
    start_time + interval
    start_time + interval + interval
    ...
    points times.
    """

    self.gpx11.MergeAll()
    segment11 = self.gpx11.Segment()

    coords = []

    # date comes in localtime, so put it in GMT time.


    #print "First Point T: %s" % self.gpx11.UTCTime(segment11.points[0].time)
    #print "Last Point  T: %s" % self.gpx11.UTCTime(segment11.points[-1].time)
    #print "START       T: %s" % self.gpx11.UTCTime(datetime.utcfromtimestamp(time.mktime(start_time)))



    first_time = segment11.points[0].time
    last_time  = segment11.points[-1].time

    # first	<time>2014-06-30T17:51:59Z</time>
    # last  <time>2014-06-30T20:44:32Z</time>


    for i in range(points):
      timepoint = time.mktime(start_time) + (interval*i)
      t_stamp = datetime.utcfromtimestamp(timepoint)
      gps_points = self.gpx11.Track().get_location_at(t_stamp)

      #print "#%d %s+%d %s->" % (i,
      #						self.UTCTime(datetime.utcfromtimestamp(time.mktime(start_time))),
      #						(i*interval),
      #						self.UTCTime(t_stamp))

      if len(gps_points) == 0:
        # no point found at this time (maybe the track starts before).
        # so add the first point of the track, and continue.


        if t_stamp < first_time:
          #print "\tNot found, adding first time"
          gps_point = copy.copy(self.gpx11.Segment().points[0])

        if t_stamp > last_time:
          #print "\tNot found, adding last time"
          gps_point = copy.copy(self.gpx11.Segment().points[-1])

      else:
        gps_point = copy.copy(gps_points[0])

      gps_point.time = datetime.fromtimestamp(timepoint)
      coords.append(gps_point)

    return self.gpx10.CreatePolarXML( coords )

  def AdjustTime(self, start_time, interval, points):
    """
    In case of some problems (Etrex Vista Old) when the date is not stored
    right (when you save the track afte save a tracklog) you sould create the
    new GPX file based on the time and adding about 10 seconds more or less
    """

    self.gpx11.MergeAll()
    segment11 = self.gpx11.Segment()

    coords = []

    # date comes in localtime, so put it in GMT time.


    #print "First Point T: %s" % self.gpx11.UTCTime(segment11.points[0].time)
    #print "Last Point  T: %s" % self.gpx11.UTCTime(segment11.points[-1].time)
    #print "START       T: %s" % self.gpx11.UTCTime(datetime.utcfromtimestamp(time.mktime(start_time)))

    i=0
    for p in self.gpx11.Segment().points:
      timepoint = time.mktime(start_time) + (interval*i)
      t_stamp = datetime.utcfromtimestamp(timepoint)

      gps_point = copy.copy(p)
      gps_point.time = datetime.fromtimestamp(timepoint)
      coords.append(gps_point)
      i+=1

    return self.gpx10.CreatePolarXML( coords )

  def PrintSummary(self, gpxlist=[]):

    r = ""
    if self.gpx10.gpx: r += self.gpx10.Print()
    if self.gpx11.gpx: r += self.gpx11.Print()
    r += "\r\n"
    return r


  # getters to retrieve important data

  def get_distance(self): 		return self.gpx10.get_distance()
  def get_ascent(self): 			return self.gpx10.get_ascent()
  def get_totaltime(self):		return self.gpx10.get_totaltime()
  def get_average_altitude(self):	return self.gpx10.get_average_altitude()
  def get_max_alt(self): 			return self.gpx10.get_max_alt()
  def get_average_speed(self): 	return self.gpx10.get_average_speed()
  def get_max_speed(self): 		return self.gpx10.get_max_speed()
  def get_gpx11_points_no(self): 	return self.gpx11.get_points_no()
  def get_gpx10_points_no(self): 	return self.gpx10.get_points_no()
  def get_location_at(self, timepoint): 	return self.gpx10.get_location_at(timepoint)
  def get_speed_for_all_points(self): 	return self.gpx10.get_speed_for_all_points()
  def get_elevation_for_all_points(self): return self.gpx10.get_elevation_for_all_points()


  def DebugFiles(self):
    # print some fancy info about files"
    print(self.PrintSummary())


  def Distance(self, A, B):

    return gpxpy.geo.distance( A.latitude, A.longitude, A.elevation,
                   B.latitude, B.longitude, B.elevation,
                   haversine=True )






# ##########################################################################################################
#
# creates a light version of TCX compatible with strava. Add support for POWER and TEMPERATURE values
# http://www8.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd
#
# ##########################################################################################################

class TCXBuilder:

    def __init__(self):
        pass

    activities = { 'biking', 'running', 'hiking', 'walking' , 'swimming' }
    header = """<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
<Activities>
<Activity Sport="{activity}">
  <Id>{starttime}</Id>
  <Lap StartTime="{starttime}">
    <TotalTimeSeconds>{totaltime}</TotalTimeSeconds>
    <DistanceMeters>{distance}</DistanceMeters>
    <Calories>{calories}</Calories>
    <Intensity>Active</Intensity>
    <TriggerMethod>Manual</TriggerMethod>
    <Track>
"""

    footer = """    </Track>
   </Lap>
</Activity>
</Activities>
</TrainingCenterDatabase>
"""

    entry = """          <Trackpoint>
            <Time>{time}</Time>
            <Position>
              <LatitudeDegrees>{latitude}</LatitudeDegrees>
              <LongitudeDegrees>{longitude}</LongitudeDegrees>
            </Position>
            <AltitudeMeters>{altitude}</AltitudeMeters>
            <DistanceMeters>{distance}</DistanceMeters>
            <HeartRateBpm>
              <Value>{hr}</Value>
            </HeartRateBpm>
            <Cadence>{cad}</Cadence>
            <Extensions>
              <TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
                <Speed>{speed}</Speed>
                <Watts>{watts}</Watts>
              </TPX>
            </Extensions>
          </Trackpoint>
"""






    def _header(self, activity, name, starttime, totaltime, distance, calories):
      # activity from self.activities
      # starttime in this format 2014-06-01T08:45:04.000Z
      # totaltime in seconds 222.11
      # distance in meters 2132.33
      # calories in int 923

      args = {
                'activity': activity,
                'name': name,
                'starttime': starttime,
                'totaltime': totaltime,
                'distance': distance,
                'calories': calories
             }

      return self.header.format(**args)

    def _footer(self):

      args = {}
      return self.footer.format(**args)


    def _entry(self, time, latitude, longitude, altitude, distance, hr, cad=0, speed=0.0, watts=0):
        # time      2014-06-01T10:20:00.000Z
        # latitude  42.79107732698321
        # longitude 0.2279058750718832
        # altitude  1153.800048828125
        # distance  22174.689453125
        # hr        92
        # cad       100*
        # speed     0.0*
        # watts     0*
      #* left_pedal_smoothness: 20.0 [percent]
      #* left_torque_effectiveness: 70.5 [percent]

        args = {
            'time':         time,
            'latitude':     latitude,
            'longitude':    longitude,
            'altitude':     altitude,
            'distance':     distance,
            'hr':           hr,
            'cad':          cad,
            'speed':        speed,
            'watts':        watts,
        }

        return self.entry.format(**args)


    def BuildTCX(self, name, gpx, activity='biking', calories='0'):


        points = gpx.get_points()

        starttime = GPXItem().UTCTime(points[0].time)
        #totaltime = "%0.2f" % gpx_track.get_duration()
        #distance  = "%0.2f" % gpx_track.length_3d()
        totaltime = "%0.2f" % gpx.get_totaltime()
        distance  = "%0.2f" % gpx.get_distance()


        # 'biking',"2014-06-01T08:45:04.000Z","2014-06-01T08:45:04.000Z","950.34","900"


        header = self._header( activity, name, starttime, totaltime, distance, calories )
        #body  = self._entry( '2014-06-01T08:45:04.000Z', '42.79080541804433', '0.227922135964036', '1152.199951171875', '0.0', '84', '100', '6.5', '270'  )

        body = ""

        distanceacc = 0.0

        ext_attrs = [ 'hr', 'cadence', 'speed', 'temperature', 'power', 'distance' ]

        for i in range(len(points)):
            p = points[i]

            #
            # fix missing values. They can be inside the "extensions" attribute, or in the root.
            # create empty if not found, then, if extensions exists, try to copy data
            #
            for attr in ext_attrs:
                if not attr in p.__dict__.keys():
                    p.__dict__[attr] = 0

            if hasattr(p, 'extensions') and p.extensions != None:
                for attr in ext_attrs:
                    if attr in p.extensions.keys():
                        p.__dict__[attr] = p.extensions[attr]


            p.time_utc = GPXItem().UTCTime(p.time)
            #p.latitude
            #p.longitude
            p.altitude = p.elevation


            if i > 0:
                distanceacc += p.distance_3d(points[i-1])

            p.distance = distanceacc
            #p.hr
            p.cad = p.cadence
            if p.speed == None:
                p.speed = 0.0
            p.watts = p.power

            # debug. Remove after getting real data.

            #p.cad = 0 + random.randrange(100)
            #p.watts = 200 + random.randrange(-100,100)

            body += self._entry( p.time_utc, p.latitude, p.longitude, p.altitude, p.distance, p.hr, p.cad, p.speed, p.watts)


        footer = self._footer()

        tcx = header + body + footer
        return tcx

def utc_to_local(utc_dt):
    """convert a UTC datetime to a localtime Representation"""
    # get integer timestamp to avoid precision lost


    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

### TESTING CODE



def test_gpxitem():

  print("Testing GPXItem (GPX 1.0)")
  item = GPXItem()
  item.Load("../samples/bike_gpx10.gpx")
  print("Version: " + item.Version())
  print(item.Print())

  print("Testing GPXItem (GPX 1.1)")
  item = GPXItem()
  item.Load("../samples/bike_gpx11.xml")
  print("Version: " + item.Version())
  print(item.Print())


def test_gpxtoolbox():
  print("Testing GPXToolBox")

  gpxtool = GPXToolBox()
  xml = gpxtool.GPX11toGPX10("../samples/bike_gpx11.xml", "../samples/bike_gpx10.gpx")
  gpxtool.DebugFiles()

  print(xml)

if __name__ == "__main__":

  #test_gpxitem()
  test_gpxtoolbox()


  #converter = GPXToolBox()
  #xml = converter.GPX11toGPX10(sys.argv[1], sys.argv[2])

  #outf = file(sys.argv[3],"wb")
  #outf.write(xml)
  #outf.close()

