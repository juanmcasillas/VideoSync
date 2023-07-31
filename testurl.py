
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


if __name__ == "__main__":

    vfile = ".\samples\gopro7\GH011502_NS.mp4"
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
    
    