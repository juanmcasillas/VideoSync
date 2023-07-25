import pygame
from pygame.locals import *
from gauges import *
from readconfig import *

class Engine:
    def __init__(self, screen_resolution, fps=30):
        self.config = None
        self.fps = fps
        self.screen_resolution = screen_resolution

    def ReadConfigFromFile(self, fname):
        cm = ConfigManager(self.screen_resolution, self.fps)
        self.config = cm.ReadConfig(fname)

        print( "Engine::ReadConfigFromFile")
        if self.config.imperialunits == False:
            print( "Engine::Using METRIC units (Km/h, m, C)")
        else:
            print ("Engine::Using IMPERIAL units (mi/h, mi, F)")

        if self.config.interpolate == False:
            print ("Engine::Using discrete values (non interpolated)")
        else:
            print ("Engine::Using Interpolating values")
            
        for e in self.config.elements:
            print ("Engine::Element Loaded:", e.config.name, e)

    
    def CreatePygameElements(self):

        self.config.default_font = pygame.font.Font(self.config.default_font_path, self.config.default_font_size)

        for i in range(len(self.config.elements)):
            # create fonts
            for f in self.config.elements[i].config.fonts.keys():
                self.config.elements[i].config.fonts[f].font = pygame.font.Font(self.config.elements[i].config.fonts[f].fontname, self.config.elements[i].config.fonts[f].size)

            # create colors (convert from string to colors)
            for f in self.config.elements[i].config.colors.keys():
                print(self.config.elements[i].config.colors[f].colorname)
                self.config.elements[i].config.colors[f].color = pygame.Color(self.config.elements[i].config.colors[f].colorname.decode())
                self.config.elements[i].config.colors[f].colortuple = (self.config.elements[i].config.colors[f].color.r,
                                                                    self.config.elements[i].config.colors[f].color.g,
                                                                    self.config.elements[i].config.colors[f].color.b,
                                                                    self.config.elements[i].config.colors[f].color.a)

    def Init(self):
        self.CreatePygameElements()


    def Update(self, metrics):
        "map the metric element with the item"

        for item in self.config.elements:

            # to allow static values work
            value = item.value
            value_list = ()
            if metrics and item.config.metric:
                for lmetric in item.config.metric:
                    if  lmetric in metrics.keys():
                        value_list += (metrics[lmetric],)
                        
                        # call the function, if available
                        if item.config.function != None:
                            r = item.config.function
                            for j in metrics.keys():
                                r = r.replace(j.upper(), str(metrics[j]))

                            value_list += (eval(r),)
            
            if len(value_list) > 0:
                item.update(value_list, metrics.time)
            else:
                # preserve static values
                item.update( (value,), metrics.time)

    def Draw(self, sf):
        for item in self.config.elements:
            item.draw(sf)


    def GetItemsByName(self, name):
        a = []
        for item in self.config.elements:
            if item.name == name:
                a.append(item)
        return a



