
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


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

# quality settings for stream

QUALITY_FASTEST = 0.0
QUALITY_FAST = 0.25
QUALITY_NORMAL = 0.5
QUALITY_GOOD = 0.75
QUALITY_BEST = 1.0

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
        else:
            self.ffmpeg = "ffmpeg"

    def CopyAudioStream(self, sourcefile, destfile):
        outfile = next(tempfile._get_candidate_names()) + os.path.splitext(sourcefile)[1]
        #cmd = "%s -i '%s' -i '%s' -c copy -map 0:1 -map 1:0 -shortest '%s'" % (self.ffmpeg, sourcefile, destfile, outfile)
        cmd = [ self.ffmpeg, "-loglevel", "info", "-i", "%s" % sourcefile,
                             "-i", "%s" % destfile,
                             "-c", "copy", "-map","0:1", "-map","1:0", "-shortest", "%s" % outfile]
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







    def _run(self, cmd):
        ##print cmd
        p = subprocess.Popen( cmd , stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = p.communicate()
        return out,err

