
from urllib.request import Request, urlopen
import io
from PIL import Image, ImageDraw

# Function to get the page content
def get_page_content(url, head=None):
    """
    Function to get the page content
    """
    if not head:
        head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        #'refere': 'https://example.com',
        #'cookie': """your cookie value ( you can get that from your web page) """
        }


    req = Request(url, headers=head)
    return urlopen(req)



import gpxpy.gpx
import sys
import datetime

import os
os.environ["OPENCV_FFMPEG_READ_ATTEMPTS"] = "8192"
import cv2
from gpxtoolbox import GPXToolBox, GPXItem
from gpxpy import geo
from mapper import *
import pygame

if __name__ == "__main__":

    gpxmanager = GPXToolBox()
    gpxmanager.LoadFiles(gpx11=".\samples\gopro7\GH011502.gpx")
    gpx = gpxmanager.gpx11
    gpx_points = gpx.Segment().points
    gpx_point_index = 0
    gpx_point = gpx_points[gpx_point_index]
    
    gpx_item = GPXItem(gpx_points)
    bounds = gpx_item.Bounds()
    NW = geo.Location(bounds.max_latitude, bounds.min_longitude)
    NE = geo.Location(bounds.max_latitude, bounds.max_longitude)
    SE = geo.Location(bounds.min_latitude, bounds.max_longitude)
    SW = geo.Location(bounds.min_latitude, bounds.min_longitude)

    img_size     = Size(640,480)
    mapper       = OSMMapper(img_size)


    mapimg = mapper.GetMapBB((NW,NE,SE,SW), mapempty=False, 
                                        mapcolor=(20,20,20), 
                                        bounding_box=False)

    # use created map (speed up things)

    maptemp = mapimg.copy()

    # some position info. TBD


    mapper.ProjectPoints(gpx_points, maptemp)
    mapper.ProjectCircle(gpx_points[0], maptemp, (100,0,0)) # start
    mapper.ProjectCircle(gpx_points[-1], maptemp, (0,100,0)) # end

    if False:
        distance_i = DistanceI( gpx_points[gpx_point_index-1], gpx_points[gpx_point_index], current_time )
        bearing = geo.bearing(gpx_points[gpx_point_index-1] , gpx_points[gpx_point_index])

        interpolated_point = geo.LocationDelta(distance=distance_i, angle=bearing)
        lat, lon = interpolated_point.move_by_angle_and_distance(gpx_point)

        interpolated_point.latitude = lat
        interpolated_point.longitude = lon
        mapper.ProjectCircle(interpolated_point, maptemp, (100,0,0)) #
    else:
        mapper.ProjectCircle(gpx_point, maptemp,(0,0,100)) #


    mode = maptemp.imagemap.mode
    size = maptemp.imagemap.size
    data = maptemp.imagemap.tobytes() # tostring() was deprecated

    map_image = pygame.image.fromstring(data, size, mode)

    #sf_x = preferences.map.size[0]
    #sf_y = preferences.map.size[1]
    #sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA)

    #map_image.set_colorkey((242,239,233)) # OSM BG
    pygame.draw.rect(map_image, (100,100,100), (0,0,map_image.get_rect().width, map_image.get_rect().height),1)
    #map_image = map_image.convert()
    map_image.set_alpha(255)

    #sf.blit(map_image,((prev_sf.get_rect().width/2)-map_image.get_rect().width/2,prev_sf.get_rect().height))



    # if self.config.halign.upper() == "LEFT":
    #     if blitit: surface.blit(map_image,map_image.get_rect(topleft=self.config.position.pos))

    # if self.config.halign.upper() == "CENTER":
    #     if blitit: surface.blit(map_image,map_image.get_rect(center=self.config.position.pos))

    # if self.config.halign.upper() == "RIGHT":
    #     if blitit: surface.blit(map_image,map_image.get_rect(topright=self.config.position.pos))

    #save it
    #map_image
    pygame.image.save(map_image, ".\samples\gopro7\mapa.png")
    sys.exit(0)

    vfile = ".\samples\gopro7\GH011502_nosound.mp4"
    stream = cv2.VideoCapture(vfile)
    cv2.OPENCV_FFMPEG_READ_ATTEMPTS = 8192
    while True:

        (grabbed, frame) = stream.read()
        if  not grabbed:
            break
        cv2.imshow("Frame", frame)
        key = cv2.pollKey()

        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    stream.release()
    cv2.destroyAllWindows()
    sys.exit(0)

    latitude = 40.0
    longitude = 20.0
    altitude = 10.0
    timestamp = datetime.datetime.utcnow()
    p = gpxpy.gpx.GPXTrackPoint(latitude, longitude, altitude, timestamp)

    p.extensions.append({})
    p.extensions[0]['hr'] = 100
    p.extensions[0]['cadence'] = 75
    p.extensions[0]['temperature'] = 32
    p.extensions[0]['power'] = 178
    
    if p.extensions[0]:
        for ext_item in [ "cadence", "temperature", "hr", "power"]:
            if ext_item in list(p.extensions[0].keys()):
                print(ext_item)


    url = "https://b.tile.openstreetmap.org/19/255800/197938.png"
    fd = get_page_content(url)
    image_file = io.BytesIO(fd.read())
    fd.close()
    
    tileimage = Image.open(image_file)
    tileimage.save("demo","PNG")
    
    