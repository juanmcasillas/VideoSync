import sys


import os.path
import os
import argparse
import xml.dom.minidom as xmlp
from engine import *
from baseconfig import BaseConfig
import gauges
import pygame



class Config(BaseConfig):
        def __init__(self, resolution, fps):
            BaseConfig.__init__(self)
            self.width = resolution[0]
            self.height = resolution[1]
            self.fps    = fps


            self.default_values()

        def __str__(self):
            s = ""
            for i in self.__dict__.keys():
                s += "%s:\t%s\n" % (i, self.__dict__[i])
            return s

        def default_values(self):
            # the names SHOULDN'T BE SUBSTRINGS!!!
            self.position = BaseConfig()
            self.position.width         = self.width
            self.position.height        = self.height
            self.position.top           = 0
            self.position.bottom        = self.position.height
            self.position.left          = 0
            self.position.right         = self.position.width
            self.position.topl          = (0, 0)
            self.position.topr          = (self.position.width,0)
            self.position.bottomr       = (self.position.width, self.position.height)
            self.position.bottoml       = (0, self.position.height)
            self.position.center        = (self.position.width/2, self.position.height/2)
            self.position.cx            = self.position.center[0]
            self.position.cy            = self.position.center[1]

        # mappers for default options

        def MapPosition(self, value):

            r = value
            for p in self.position.__dict__.keys():
                if r.find(p.upper()) != -1:
                    r = r.replace(p.upper(), str(self.position.__dict__[p]))
            return eval(r)

        def MapFontName(self, item):

            r = item
            fnamedef = self.default_font_path

            if item.find("DEFAULT") != -1:
                r = item.replace("DEFAULT", fnamedef)

            return r

        def MapFontSize(self, item):

            r = item
            fsizedef = self.default_font_size
            if r.find("DEFAULT") != -1:
                    r = item.replace("DEFAULT", str(fsizedef))
            return eval(r)

        def MapDefaultColor(self, item):

            r = item
            defcolor = self.default_color
            if r.find("DEFAULT") != -1:
                    r = item.replace("DEFAULT", str(defcolor))
            return r


class ConfigManager:
    def __init__(self, resolution, fps):
        self.parsers = {}
        self.gauges = {}

        self.gauges["slope"] = gauges.OneValueGauge
        self.gauges["distance"] = gauges.DistanceGauge
        self.gauges["elevation"] = gauges.ElevationGauge
        self.gauges["speed"] = gauges.SpeedGauge
        self.gauges["label"] = gauges.Label
        self.gauges["time"] = gauges.TimeGauge
        self.gauges["cadence"] = gauges.OneValueIntegerGauge
        self.gauges["temperature"] = gauges.TemperatureGauge
        self.gauges["hr"] = gauges.HRGauge
        self.gauges["power"] = gauges.PowerGauge
        self.gauges["gpsinfo"] = gauges.GPSInfoGauge
        self.gauges["osmmap"] = gauges.OSMMapGauge
        self.gauges["altgraph"] = gauges.AltGraphGauge
        self.gauges["bearing"] = gauges.BearingGauge
        self.gauges["ecg"] = gauges.ECGGauge
        self.gauges["picture"] = gauges.Picture
        self.gauges["rect"] = gauges.Rect
        self.gauges["line"] = gauges.Line

        self.width = resolution[0]
        self.height = resolution[1]
        self.fps = fps


    def ReadConfig(self, fname):
        dom = xmlp.parse(fname)
        self.config = Config((self.width, self.height), self.fps)
        self.config.elements = []


        configuration = dom.getElementsByTagName("configuration")[0]
        preferences = configuration.getElementsByTagName("preferences")[0]
        layout =  configuration.getElementsByTagName("layout")[0]

        # read default font and default size
        units = preferences.getAttribute("units") or "metric"
        interpolate = preferences.getAttribute("interpolate") or "False"
        default_font = preferences.getElementsByTagName("default_font")[0]
        default_font_path = self.config._xmlgetTEXT(default_font.getElementsByTagName("path")[0])
        default_font_size = self.config._xmlgetTEXT(default_font.getElementsByTagName("size")[0])
        default_color = self.config._xmlgetTEXT(preferences.getElementsByTagName("default_color")[0])


        self.config.imperialunits = False
        self.config.interpolate = False

        self.config.default_font_path = default_font_path
        self.config.default_font_size = int(default_font_size)
        self.config.default_color = default_color

        if units.lower() == "imperial":
            self.config.imperialunits = True

        if interpolate.lower() in [ "true", "1",  "yes" ]:
            self.config.interpolate = True

        for tag in layout.childNodes:
            if tag.nodeType != tag.ELEMENT_NODE:
                continue
            if tag.tagName.lower() not in self.gauges.keys():
                raise Exception("Can't process %s tag" % tag.tagName)

            item = self.gauges[tag.tagName.lower()]()
            cfg = item.ParseAndConfigure(tag, self.config)
            self.config.elements.append(item)

        return self.config





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Configuration File")
    args = parser.parse_args()

    resolution = (960, 720) # width, height
    fps = 50

    pygame.init()
    pygame.font.init()

    engine = EngineNG(resolution, fps)
    engine.ReadConfigFromFile(args.config)
    engine.Init()



