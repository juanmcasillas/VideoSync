# -*- coding: utf-8 -*-

# Copyright 2011 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys as mod_sys
import math as mod_math
import xml.sax.saxutils as mod_saxutils
from decimal import *

PYTHON_VERSION = mod_sys.version.split(' ')[0]


def Points2GPXWayPoints(points):
    ## see 
    ## http://www.topografix.com/GPX/1/1/#type_wptType
    xml_header = """<?xml version="1.0"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtrx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:trp="http://www.garmin.com/xmlschemas/TripExtensions/v1" xmlns:adv="http://www.garmin.com/xmlschemas/AdventuresExtensions/v1" xmlns:prs="http://www.garmin.com/xmlschemas/PressureExtension/v1" xmlns:tmd="http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1" xmlns:vptm="http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1" xmlns:ctx="http://www.garmin.com/xmlschemas/CreationTimeExtension/v1" xmlns:gpxacc="http://www.garmin.com/xmlschemas/AccelerationExtension/v1" xmlns:gpxpx="http://www.garmin.com/xmlschemas/PowerExtension/v1" xmlns:vidx1="http://www.garmin.com/xmlschemas/VideoExtension/v1" creator="Garmin Desktop App" version="1.1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/ActivityExtension/v1 http://www8.garmin.com/xmlschemas/ActivityExtensionv1.xsd http://www.garmin.com/xmlschemas/AdventuresExtensions/v1 http://www8.garmin.com/xmlschemas/AdventuresExtensionv1.xsd http://www.garmin.com/xmlschemas/PressureExtension/v1 http://www.garmin.com/xmlschemas/PressureExtensionv1.xsd http://www.garmin.com/xmlschemas/TripExtensions/v1 http://www.garmin.com/xmlschemas/TripExtensionsv1.xsd http://www.garmin.com/xmlschemas/TripMetaDataExtensions/v1 http://www.garmin.com/xmlschemas/TripMetaDataExtensionsv1.xsd http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensions/v1 http://www.garmin.com/xmlschemas/ViaPointTransportationModeExtensionsv1.xsd http://www.garmin.com/xmlschemas/CreationTimeExtension/v1 http://www.garmin.com/xmlschemas/CreationTimeExtensionsv1.xsd http://www.garmin.com/xmlschemas/AccelerationExtension/v1 http://www.garmin.com/xmlschemas/AccelerationExtensionv1.xsd http://www.garmin.com/xmlschemas/PowerExtension/v1 http://www.garmin.com/xmlschemas/PowerExtensionv1.xsd http://www.garmin.com/xmlschemas/VideoExtension/v1 http://www.garmin.com/xmlschemas/VideoExtensionv1.xsd">
  <metadata>
    <link href="http://www.garmin.com">
      <text>Garmin International</text>
    </link>
  </metadata>
    """

    xml_footer = """</gpx>"""


    xml_wp_tpl = """
      <wpt lat="%f" lon="%f">
        <ele>%f</ele>
        <name>%s</name>
        <desc>%s</desc>
        <sym>Flag, Blue</sym>
        <type>user</type>
        <extensions>
          <gpxx:WaypointExtension>
            <gpxx:DisplayMode>SymbolAndName</gpxx:DisplayMode>
          </gpxx:WaypointExtension>
          <wptx1:WaypointExtension>
            <wptx1:DisplayMode>SymbolAndName</wptx1:DisplayMode>
          </wptx1:WaypointExtension>
        </extensions>
      </wpt>        
    """ 
    # %f lat
    # %f lon
    # %f elevation
    # %s name    
    # %s description

    r = xml_header
    for p in points:

        w = xml_wp_tpl % (p.latitude, p.longitude, p.elevation, p.name, p.description)
        r += w
        
    r += xml_footer
    return r



def to_xml(tag, attributes=None, content=None, default=None, escape=False):
    attributes = attributes or {}
    result = '\n<%s' % tag

    if content is None and default:
        content = default

    if attributes:
        for attribute in attributes.keys():
            result += make_str(' %s="%s"' % (attribute, attributes[attribute]))

    if content is None:
        result += '/>'
    else:
        if escape:
            result += make_str('>%s</%s>' % (mod_saxutils.escape(content), tag))
        else:
            result += make_str('>%s</%s>' % (content, tag))

    result = make_str(result)

    return result


def is_numeric(object):
    try:
        float(object)
        return True
    except TypeError:
        return False
    except ValueError:
        return False


def to_number(s, default=0, nan_value=None):
    try:
        result = float(s)
        if mod_math.isnan(result):
            return nan_value
        return result
    except TypeError:
        pass
    except ValueError:
        pass
    return default


def total_seconds(timedelta):
    """ Some versions of python dont have timedelta.total_seconds() method. """
    if timedelta is None:
        return None
    return (timedelta.days * 86400) + timedelta.seconds

# Hash utilities:


def __hash(obj):
    result = 0

    if obj is None:
        return result
    elif isinstance(obj, dict):
        raise RuntimeError('__hash_single_object for dict not yet implemented')
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return hash_list_or_tuple(obj)

    return hash(obj)


def hash_list_or_tuple(iteration):
    result = 17

    for obj in iteration:
        result = result * 31 + __hash(obj)

    return result


def hash_object(obj, *attributes):
    result = 19

    for attribute in attributes:
        result = result * 31 + __hash(getattr(obj, attribute))

    return result


def make_str(s):
    """ Convert a str or unicode object into a str type. """
    if PYTHON_VERSION[0] == '2':
        if isinstance(s, unicode):
            return s.encode("utf-8")
    return str(s)

# compute if a point is inside a polygon, based on klunky method of raycasting.
# if decimal mode is not used for computations, it doesn't work.


def point_inside_polygon(point,poly):

   getcontext().prec = 6

   x = Decimal(point.longitude)
   y = Decimal(point.latitude)

   # check if point is a vertex
   #if (x,y) in poly: return True
   for p in poly:
       px = Decimal(p[0])
       py = Decimal(p[1])
       if x == px and y == py:
           return True

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if Decimal(p1[1]) == Decimal(p2[1]) and Decimal(p1[1]) == y and x > min(Decimal(p1[0]), Decimal(p2[0])) and x < max(Decimal(p1[0]), Decimal(p2[0])):
         return True

   n = len(poly)
   inside = False

   p1x,p1y,d = poly[0]

   p1x = Decimal(p1x)
   p1y = Decimal(p1y)

   for i in range(n+1):
      p2x,p2y,d = poly[i % n]

      p2x = Decimal(p2x)
      p2y = Decimal(p2y)

      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y


   return inside

##import  shapely.geometry
def shapely_point_inside_polygon(point, poly):

    l = ()
    for p in poly:
        l += (float(p[0]),float(p[1])),

    s_poly = shapely.geometry.MultiPoint(l).convex_hull
    #s_poly = shapely.geometry.polygon.LinearRing(l)
    #s_poly = shapely.geometry.Polygon(l)

    return s_poly.contains(shapely.geometry.Point(point.longitude, point.latitude))


def CHECK_POLY():
    poly = [(u'-4.49939745260145', u'40.4138620870208', u'0'), (u'-4.49949541855114', u'40.4139643257625', u'0'), (u'-4.4996252102608', u'40.4138910232361', u'0'), (u'-4.49964907252832', u'40.4138775610314', u'0'), (u'-4.49947469858371', u'40.4137315405383', u'0'), (u'-4.49934315551365', u'40.4138053160456', u'0'), (u'-4.49939745260145', u'40.4138620870208', u'0'), (u'-4.49939745260145', u'40.4138620870208', u'0')]
    point_out = geo.Location(40.413967 , -4.499751, 0)
    point_in = geo.Location( 40.413850 , -4.499564, 0)

    #for p in poly: print p[0],",",p[1],",",0

    #print point_inside_polygon(point_out,poly)
    #print point_inside_polygon(point_in,poly)
    # test shapely

    print(point_inside_polygon(point_out,poly))
    print(point_inside_polygon(point_in,poly))

    #print point_inside_polygon(point_out,poly)
    #print point_inside_polygon(point_in,poly)
    sys.exit(0)
