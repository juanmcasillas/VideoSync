
import sys
from builtins import float





import os
import os.path
from manager import HRMManager
from mapper import *
import gpxpy
import gpxtoolbox


import argparse
import imutils

import numpy as np
import math
import datetime
import time
import timecode

# interpolate values

def DistanceI(A, B, tdelta, tag=""):

    # interpolate the distance based in tdelta point from A (time)
    d = Distance(A, B)

    if d == 0.0 or tdelta == 0.0:
        return 0.0
    # d has the distance from A, B, complete.
    #tdiff = B.time - A.time
     
    x1 = getseconds(gpxtoolbox.utc_to_local(A.time))
    x2 = getseconds(gpxtoolbox.utc_to_local(B.time))
    
    if type(tdelta) != float:
        tdelta = getseconds(tdelta) + (tdelta.microsecond / 1000000.0) - x1
    
    goal = interp(x1 + tdelta, [float(x1), float(x2) ], [ 0.0, d])
    #print("%s A(%3.6f, %3.6f) B(%3.6f, %3.6f) Goal: %3.6f -> %3.6f" % (tag, x1,0,x2,d, x1 + tdelta, goal))
    return goal    
    
    
    #     #td = getseconds(tdelta) + (tdelta.microsecond / 1000000.0) - x1 
    #     #tdiff = getseconds(tdiff) + (tdelta.microsecond / 1000000.0)
    #     tdiff = tdiff.total_seconds() + (tdiff.microseconds / 1000000.0)
    # 
    #     # support date time objects
    #     
    #         
    # 
    #     time_d = tdelta
    #     if time_d > tdiff: time_d = tdiff
    # 
    #     if tdiff == 0.0:
    #         return 0.0
    #         
    #     s = (d*time_d) / float(tdiff)
    #     return s
    

def getseconds(t):

    if hasattr(t, "timetuple"):
        return time.mktime(t.timetuple())
    else:
        return time.mktime(t)

def Interpolate( x1, y1, x2, y2, tdelta ):
    #
    # interpolate. Line across two points:
    #
    # x - x1   y - y1
    # ------ = ------        given two points A(x1,y1) and B(x2,y2)
    # x2 - x1  y2 - y1
    #
    # in our case, the X component is allways TIME, and Y are the
    # distance, speed, and so on.
    #y1 = Distance(gpx_point_prev, gpx_point)            # current
    #y2 = Distance(gpx_point, gpx_points[gpx_index+1])   # next
    #x1 = gpx_point_prev.time
    #x2 = gpx_point.time

    # x - x1 = ( y - y1 / y2 - y1 ) * ( x2 - x1)
    # x = ( ( y - y1 / y2 - y1 ) * ( x2 - x1) ) + x1
    #


    x1 = getseconds(gpxtoolbox.utc_to_local(x1))
    x2 = getseconds(gpxtoolbox.utc_to_local(x2))
    #tdelta = getseconds(tdelta) + (tdelta.microsecond / 1000000.0)

    # using now tdelta as seconds after X1.
    

    #print x1
    #print tdelta
    #print x2



    goal = interp(x1 + tdelta, [float(x1), float(x2) ], [ float(y1), float(y2)])
    #print("A(%3.6f, %3.6f) B(%3.6f, %3.6f) Goal: %3.6f -> %3.6f" % (x1,y1,x2,y2, x1 + tdelta, goal))
    return goal



def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

## calculation helpers.

## calculation helpers.

def Distance(A, B):

    if A.latitude == B.latitude and A.longitude == B.longitude:
        #print("A.elev: ", A.elevation)
        #print("B.elev: ", B.elevation)
        return 0.0

    return gpxpy.geo.distance( A.latitude, A.longitude, A.elevation,
                   B.latitude, B.longitude, B.elevation,
                   haversine=True )






def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def savitzky_golay(y, window_size, order, deriv=0, rate=1):

    import numpy as np
    from math import factorial

    try:
        window_size = np.abs(int(window_size))
        order = np.abs(int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = list(range(order+1))
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


class DataSerie(object):
    def __init__(self, time=None, latitude=None, longitude=None, elevation=None, time_delta= None, distance_delta=None, speed=None, slope=None, elevation_delta=None, bearing=None):
        object.__init__(self)
        self.time = time
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.time_delta = time_delta
        self.distance_delta = distance_delta
        self.speed = speed
        self.slope = slope
        self.elevation_delta = elevation_delta
        self.bearing = bearing

    def __getitem__(self, item):
        return self.__dict__[item]

    def __str__(self):
        s = "%s %s %s %s %s %s %s %s %s %s" % (self.time, self.latitude, self.longitude, self.elevation, self.time_delta, self.distance_delta, self.speed, self.slope, self.elevation_delta, self.bearing)
        return s

    def header(self):
        s = "Date Time Latitude Longitude Elevation TimeDelta DistanceDelta Speed Slope ElevationDelta Bearing"
        return s


#DataSerie = namedtuple('DataSerie',['time', 'latitude', 'longitude', 'elevation', 'distance_delta', 'speed', 'slope', 'elevation_delta'])

def Smooth(series, elements, size_hint=0):
    """
    get the elements array items and extract them as arrays. Then, smooth it, and build again the DataSerie, but smoothed.
    """

    r = {}
    for e in elements: r[e] = []

    for item in series:

        for e in elements:
            r[e].append(item.__getattribute__(e))


    ## r has a dict with all the items. Smooth them.

    window_size = 71
    if size_hint > 0:
        if size_hint < 20:
            window_size = 11

    for e in elements:
        #r[e] = savitzky_golay(np.array(r[e]), 71, 5)
        r[e] = savitzky_golay(np.array(r[e]), window_size, 5)


    ## build again the dataserie, but smoothed.

    for i in range(len(series)):
        for e in elements:
            series[i].__setattr__(e,r[e][i])

    return series


    #slopes = savitzky_golay(np.array(slopes), 51, 3) # window size 51, polynomial order 3
    #slopes = savitzky_golay(np.array(slopes), 71, 5) # window size 51, polynomial order 3
    #slopes = smooth(slopes, 3)
    #slopes = smooth(slopes, 9)
    #for i in range(len(r)):
    #    k.append( DataSerie(r[i].time, r[i].latitude, r[i].longitude, r[i].elevation, r[i].distance_delta, r[i].speed, r[i].slope, r[i].elev_delta, slopes[i]) )



## DON'T use this method. Generates invalid SLOPE calculations

# def CreateSeriesAcc(points):
#     """
#     create a data series ordered by date, with the relative information for the points
#     """
#
#     r = []
#
#     distance = 0.0
#     slope_space = 10    # use 10m minimum # was 20
#     Acc = False
#
#     slopes = []
#
#
#     for i in range(len(points)):
#
#         if i == 0:
#             distance_delta = 0.0
#             slope = 0.0
#             speed = 0.0
#             elev_delta = 0.0
#             elevation_begin = 0.0
#             slope_distance_acc = 0.0
#         else:
#             distance_delta = Distance(points[i-1], points[i])
#             time_delta = points[i].time - points[i-1].time
#             elev_delta = points[i].elevation - points[i-1].elevation
#             speed = 3.6 * (distance_delta / time_delta.total_seconds() ) # km/h
#
#             if Acc:
#                 slope_distance_acc += distance
#                 if slope_distance_acc > slope_space:
#                    slope = 100.0 * (float(points[i].elevation - elevation_begin)/slope_distance_acc)
#                    elevation_begin = 0.0
#                    Acc = False
#                    slope_distance_acc = 0.0
#                 else:
#                     slope_distance_acc += distance_delta
#             else:
#                 if distance_delta > slope_space:
#                     slope = 100.0 * (float(elev_delta)/distance_delta)
#                     Acc = False
#                 else:
#                     slope_distance_acc += distance_delta
#                     if not Acc:
#                         elevation_begin = points[i].elevation
#                     Acc = True
#
#                 #print("%3.2f %3.2f %3.2f %3.2f %3.2f %3.2f" % (slope_distance_acc, slope_space, points[i].elevation, elevation_begin, points[i].elevation-elevation_begin, slope))
#
#                 elevation_begin = points[i].elevation
#                 slope_distance_acc = slope_distance_acc - slope_space
#
#             # degree (angle - not realistic)
#             # slope =  g = math.degrees(math.asin(elevation_delta_p/distance_delta_p))
#
#             # based on hipotenuse ()
#             #a^2 + b^2 = c^2
#             # a^2 = c^2 - b^2 ; b = elevation, c= distance.
#
#             #bside = math.pow(elevation_delta_p,2)
#             #cside = math.pow(distance_delta_p,2)
#             #aside = math.sqrt(cside - bside)
#             #slope = (slope + (100.0 *((elevation_delta_p) / aside))) / 2.0 # median
#
#             # topographic method
#             # slope = ( slope + (100.0 * (elevation_delta_p) / distance_delta_p)) / 2.0
#
#             # small slope diference. Store it, calculate later.
#             #slope = (100.0 * (elevation_delta_p) / float(distance_delta_p))
#
#
#
#             #
#             # when distance IS TOO small, the SLOPE is calculated WRONG. (too much slope).
#             # the approach: calculate the Slope in the same distance, then map the values
#             # for the required points: NORMALIZE SLOPE to X Distance.
#             #
#
#
#         data = DataSerie(points[i].time, points[i].latitude, points[i].longitude, points[i].elevation, time_delta, distance_delta, speed, slope, elev_delta )
#         r.append(data)
#
#     #sys.exit(0)
#     return r


# simple slope calculation based on topographic formula

def CreateSeries(points):
    """
    create a data series ordered by date, with the relative information for the points
    """

    r = []

    distance = 0.0

    slopes = []

    for i in range(len(points)):



        if i == 0:
            distance_delta = 0.0
            slope = 0.0
            speed = 0.0
            elev_delta = 0.0
            elevation_begin = 0.0
            bearing = 0.0
            time_delta = timedelta(seconds=0)
        else:
            distance_delta = math.fabs(Distance(points[i-1], points[i]))
            time_delta = points[i].time - points[i-1].time
            elev_delta = points[i].elevation - points[i-1].elevation

            if distance_delta > 0.0:
                speed = 3.6 * (distance_delta / time_delta.total_seconds()) # ms/s
                slope = 100.0 * (float(elev_delta)/distance_delta)
            else:
                speed = 0.0
                slope = 0.0
                

            # calculate bearing if there is some movement (at least, 0.2m)
            if distance_delta > 0.2:
                bearing = geo.bearing(points[i-1], points[i])


            #print("%3.2f %3.2f %3.2f %3.2f %3.2f %3.2f" % (slope_distance_acc, slope_space, points[i].elevation, elevation_begin, points[i].elevation-elevation_begin, slope))

            # degree (angle - not realistic)
            # slope =  g = math.degrees(math.asin(elevation_delta_p/distance_delta_p))

            # based on hipotenuse ()
            #a^2 + b^2 = c^2
            # a^2 = c^2 - b^2 ; b = elevation, c= distance.

            #bside = math.pow(elevation_delta_p,2)
            #cside = math.pow(distance_delta_p,2)
            #aside = math.sqrt(cside - bside)
            #slope = (slope + (100.0 *((elevation_delta_p) / aside))) / 2.0 # median

            # topographic method
            # slope = ( slope + (100.0 * (elevation_delta_p) / distance_delta_p)) / 2.0

            # small slope diference. Store it, calculate later.
            #slope = (100.0 * (elevation_delta_p) / float(distance_delta_p))



            #
            # when distance IS TOO small, the SLOPE is calculated WRONG. (too much slope).
            # the approach: calculate the Slope in the same distance, then map the values
            # for the required points: NORMALIZE SLOPE to X Distance.
            #


        data = DataSerie(points[i].time, points[i].latitude, points[i].longitude, points[i].elevation, time_delta.total_seconds(), distance_delta, speed, slope, elev_delta, bearing )
        r.append(data)

    #sys.exit(0)
    return r
