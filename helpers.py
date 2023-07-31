
# removed due using ffprobe - json format.
#from hachoir.parser import createParser
#from hachoir.metadata import extractMetadata


import os
import sys
import os.path
import shutil
import subprocess
import tempfile
import platform

from collections import deque
import numpy as np
import imutils
import cv2
import pygame
import urllib.request
from urllib.request import Request, urlopen

import json

# quality settings for stream

QUALITY_FASTEST = 0.0
QUALITY_FAST = 0.25
QUALITY_NORMAL = 0.5
QUALITY_GOOD = 0.75
QUALITY_BEST = 1.0

# see https://stackoverflow.com/questions/34576665/setting-proxy-to-urllib-request-python3
def set_http_proxy(proxy):
    if proxy == None: # Use system default setting
        proxy_support = urllib.request.ProxyHandler()
    elif proxy == '': # Don't use any proxy
        proxy_support = urllib.request.ProxyHandler({})
    else: # Use proxy
        proxy_support = urllib.request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)


# see https://stackoverflow.com/questions/16627227/problem-http-error-403-in-python-3-web-scraping
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


class EmptyClass(): pass


def metaDataFile(filePath):
    filename, realname = filePath, filePath

    parser = createParser(filename, realname)
    try:
        metadata = extractMetadata(parser, QUALITY_BEST)
    except OSError as err:
        print(("Metadata extraction error: %s" % str(err)))
        metadata = None
    if not metadata:
        print(metadata)
        print( "Unable to extract metadata")
        exit(1)
    return metadata


def pygame_to_cvimage(surface):
    """Convert a pygame surface into a cv image"""

    r = pygame.surfarray.pixels3d(surface)
    return r.swapaxes(0,1)

def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    #return pygame.image.frombuffer(image.tostring(), image.shape[1::-1],"RGB")

    r = pygame.surfarray.make_surface(image.swapaxes(0,1))
    return r.convert_alpha()



class FFMPEGAdapter:
    def __init__(self):
        if platform.system() == "Windows":
            self.ffmpeg = "C:\\dev\\ffmpeg\\bin\\ffmpeg.exe"
            self.ffprobe = "C:\\dev\\ffmpeg\\bin\\ffprobe.exe"
            
        else:
            self.ffmpeg = "ffmpeg"
            self.ffprobe = "ffprobe"

    def CopyAudioStream(self, sourcefile, destfile, offset=0, duration=0):
        outfile = next(tempfile._get_candidate_names()) + os.path.splitext(sourcefile)[1]
        #cmd = "%s -i '%s' -i '%s' -c copy -map 0:1 -map 1:0 -shortest '%s'" % (self.ffmpeg, sourcefile, destfile, outfile)
        
        
        cmd = [ self.ffmpeg, "-loglevel", "info",  ]

        cmd += [ "-ss", "%f" % offset ]
        
        cmd += [ "-t", "%f" % duration ]
     
     
        # "-shortest" removed using crop
        cmd += [ "-i", "%s" % sourcefile, "-i", "%s" % destfile , "-c", "copy", "-map","0:1", "-map","1:0",  "%s" % outfile]
        

        print(( "Copying audio track from %s to %s" % (sourcefile, destfile)))
        print(("Invoking: " + " ".join(cmd)))

        out,err  = self._run( cmd )
        ##print out,err

        ##
        ## move outfile to created output.
        ##

        print(("Removing: %s" % destfile))
        os.remove(destfile)
        print(( "Moving: %s -> %s" % (outfile,destfile)))
        try:
            #os.rename(outfile, destfile)
            shutil.copy(outfile, destfile)
            os.remove(outfile)
        except Exception as e:
            if os.path.exists(destfile):
                os.remove(destfile)
            #os.rename(outfile, destfile)
            shutil.copy(outfile, destfile)
            os.remove(outfile)


    #
    # This version does the same as before,
    # but using 3 steps for clarity and debug purpouses.
    # 
    def ClipAudioStream(self, sourcefile, destfile, offset=0, duration=0):
        outfile = next(tempfile._get_candidate_names()) + os.path.splitext(sourcefile)[1]
        outfile_2 = next(tempfile._get_candidate_names()) + os.path.splitext(sourcefile)[1]
        #cmd = "%s -i '%s' -i '%s' -c copy -map 0:1 -map 1:0 -shortest '%s'" % (self.ffmpeg, sourcefile, destfile, outfile)

        if offset == 0 and duration == 0:
            return self.CopyAudioStream(sourcefile, destfile)
        
        #see https://superuser.com/questions/1631188/replace-section-of-audio-in-a-video-with-ffmpeg
        
        # 1 extract audio and trim it
        # ffmpeg -i RecordingA.mp4 -vn -acodec copy audio.ogg
        
        cmd = [ self.ffmpeg, "-loglevel", "info", 
               "-ss","%f" % offset, "-t", "%f" % duration, 
               "-i", "%s" % sourcefile,
               "-vn", "-acodec", "copy", "%s" % outfile ]

        print(( "Extracting audio track from %s -> %s (offset: %ds, duration %ds)" % (sourcefile, outfile, offset, duration)))
        print(("Invoking: " + " ".join(cmd)))
        out,err  = self._run( cmd )
        #print(out,err)
       
        # merge
        # ffmpeg -i RecordingA.mp4 -i final.ogg -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 RecordingB.mp4

        # "0:1"
        cmd = [ self.ffmpeg, "-loglevel", "info", "-i", "%s" % outfile,
                 "-i", "%s" % destfile , "-c", "copy", "-map","0:0", "-map","1:0",  "%s" % outfile_2 ]

        print(( "Copying audio track from %s to %s" % (outfile, destfile)))
        print(("Invoking: " + " ".join(cmd)))

        out,err  = self._run( cmd )
        #print(out,err)
        ##
        ## move outfile to created output.
        ##

        print(("Removing: %s" % destfile))
        print(("Removing: %s" % outfile))
        try:
            os.remove(destfile)
            os.remove(outfile)
        except Exception as e:
            pass

        print(( "Moving: %s -> %s" % (outfile_2,destfile)))
        try:
            #os.rename(outfile, destfile)
            shutil.copy(outfile_2, destfile)
            os.remove(outfile_2)
        except Exception as e:
            if os.path.exists(destfile):
                os.remove(destfile)
            #os.rename(outfile, destfile)
            shutil.copy(outfile_2, destfile)
            os.remove(outfile_2)


    def GetJsonMetadata(self, fname, tag=None):
        cmd = [ self.ffprobe, 
                "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", "%s" % fname ]
        out,err  = self._run( cmd )
        try:
            data = json.loads(out)
        except json.JSONDecodeError as e:
            print("Error getting json metadata for %s (%s)" % (fname, e))
        
        if not tag:
            return(data)
        return data[tag]


    def _run(self, cmd):
        ##print cmd
        p = subprocess.Popen( cmd , stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = p.communicate()
        return out,err

