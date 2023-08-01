import pygame
import pygame.gfxdraw
from pygame.locals import *
from gauges import *
import time
import math
import fxtools
from mapper import *
from gradientmap import GradientMap
from xml.dom.minidom import *
from baseconfig import *
from PIL import Image
from metrics import *
import gpxtoolbox

class EmptyClass:
  pass

class BaseGauge:
  """
  A gauge that shows a title, a value, and max and min
  """
  #def __init__(self, value=0, fps=30, max=0, min=999999):
  def __init__(self, fps=30):

    #self.pos    = pos
    #self.colors = colors
    #self.fonts  = fonts
    #self.title = title

    self.value = 0
    self.max   = 0
    self.min   = 0
    self.cfg   = None

    # animation cycle
    self.fps        = fps
    self.framecount = 0
    self.animated   = False

    # if you support metric or imperial units
    self.unit_label = None
    self.current_time = None


  def ParseAndConfigure(self, node, baseconfig):
    """
    <GENERIC label="GENERIC %" align="left" metric="METRIC" *function="XX" *max="0" *min="9999999" *value="" *animated="False">

        <position x="LEFT+20" y="BOTTOM-260" />
        <colors>
            <title>(255,255,255,0)</title>
            <value>(255,255,255,0)</value>
            <...>
        </colors>
        <fonts>
            <title font="DEFAULT" size="DEFAULT-20" />
            <value font="DEFAULT" size="DEFAULT+5" />
            <...>
        </fonts>
    </GENERIC>
    """
    cfg = BaseConfig()
    cfg.position = BaseConfig()
    cfg.colors = BaseConfig()
    cfg.fonts = BaseConfig()
    cfg.name = node.tagName
    cfg.imperialunits = baseconfig.imperialunits
    cfg.interpolate = baseconfig.interpolate

    id = node.getAttribute("id") or None
    halign = node.getAttribute("halign") or "left"
    label = node.getAttribute("label") or "**GENERIC_LABEL**"
    metric = node.getAttribute("metric") or None
    function = node.getAttribute("function") or None
    animated = node.getAttribute("animated") or False

    value =  node.getAttribute("value") or None

    maxval = float(node.getAttribute("max") or "0")
    minval = float(node.getAttribute("min") or "999999999")

    position = node.getElementsByTagName("position")[0]
    x = baseconfig.MapPosition(position.getAttribute("x"))
    y = baseconfig.MapPosition(position.getAttribute("y"))

    cfg.id = id
    cfg.label = label
    if metric:
        cfg.metric = list(map(lambda x: x.strip(), metric.split(",")))
    else:
        cfg.metric = None
        
    cfg.function = function
    cfg.halign = halign.upper()
    cfg.max = maxval
    cfg.min = minval
    cfg.value = value

    cfg.position.x = x
    cfg.position.y = y
    cfg.position.pos = (x,y)

    cfg.animated = False
    if animated != False and animated.lower() == "true":
        cfg.animated = True


    colors = node.getElementsByTagName("colors")
    if colors:
        colors = colors[0]
        for child in colors.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                ctext = cfg._xmlgetTEXT(child)
                cfg.colors.__dict__[child.tagName.lower()] = BaseConfig()
                cfg.colors.__dict__[child.tagName.lower()].colorname = baseconfig.MapDefaultColor(ctext).encode('ascii', 'ignore')


    fonts = node.getElementsByTagName("fonts")
    if fonts:
        fonts = fonts[0]
        for child in fonts.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                font_attr = child.getAttribute("fontname") or "DEFAULT"
                size_attr = child.getAttribute("size") or "DEFAULT"
                cfg.fonts.__dict__[child.tagName.lower()] = BaseConfig()

                # MAP FONTS.
                font_attr = baseconfig.MapFontName(font_attr)
                size_attr = baseconfig.MapFontSize(size_attr)

                cfg.fonts.__dict__[child.tagName.lower()].fontname = font_attr
                cfg.fonts.__dict__[child.tagName.lower()].size = size_attr

    self.config = cfg

    # set basic parameters here.
    self.InitAfterConfig()
    return self.config



  def InitAfterConfig(self):

      self.value = self.config.value
      self.min = self.config.min
      self.max = self.config.max
      self.name = self.config.name
      self.id   = self.config.id
      self.animated = self.config.animated

      # manage imperial or metric
      if self.unit_label != None:
          self.config.label +=  " (%s)" % self.unit_label

  def animate(self):
      pass

  def EnableAnimation(self): self.animated = True
  def DisableAnimation(self): self.animated = False


  def update(self, values, current_time=None):
    #if value > self.max: self.max = value
    #if value < self.min: self.min = value
    # check the order of values, reflected on "metric="""

    ##print("update()", values, type(values))
    if len(values) == 0:
        self.value = None
    else:
        self.value = values[0]
    self.current_time = current_time

  def incr(self, amount=1):
    self.update(self.value+amount)

  def decr(self, amount=1):
    self.update(self.value-amount)

  def fvalue(self):
    if self.value != None:
        return("%3.1f" % self.value)
    return "---.-"


  def fmax(self): return("max %3.2f" % self.max)
  def fmin(self): return("min %3.2f" % self.min)

  # you know, how to draw the thing in a rect
  def draw(self, surface, blitit=True):

    print ("*" * 80)
    print ("WARNING -- DONT CALL")
    print ("*" * 80)
    sys.exit(0)

    value_r = fxtools.shadow(self.fvalue(), self.fonts.label, self.colors.label, 1)

    sf_x = value_r.get_rect().width
    sf_y = value_r.get_rect().height

    sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA,32)
    sf = sf.convert_alpha()

    if self.halign == 0:
        sf.blit(value_r, (0,0))
        if blitit: surface.blit(sf,sf.get_rect(topleft=self.pos))

    if self.halign == 1:
        sf.blit(value_r, (sf_x/2 - value_r.get_rect().width/2,0))
        if blitit: surface.blit(sf,sf.get_rect(center=self.pos))

    if  self.halign == 2:
        sf.blit(value_r, (sf_x-value_r.get_rect().width,0))
        if blitit: surface.blit(sf,sf.get_rect(topright=self.pos))

    return sf


###############################################################################
#
# OVERRIDE THIS CLASS (AS BASE)
#
###############################################################################






class Label(BaseGauge):
  def __init__(self, fps=30):
    BaseGauge.__init__(self, fps=fps)

  def fvalue(self):
      if self.value == None:
          return ""
      else:
          return self.value


  def draw(self, surface, blitit=True):
    """
    +--------------+
    |  VALUE HERE  |
    +--------------+
    """

    # draw each frame. Cycle the animation each FPS frames

    #value_r = self.fonts.label.render(self.fvalue() ,1, self.colors.label)
    
    value_r = fxtools.shadow(self.fvalue(), self.config.fonts.value.font, self.config.colors.value.color, 1)

    sf_x = value_r.get_rect().width
    sf_y = value_r.get_rect().height

    sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA,32)
    sf = sf.convert_alpha()

    if self.config.halign.upper() == "LEFT":
        sf.blit(value_r, (0,0))
        if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))

    if self.config.halign.upper() == "CENTER":
        sf.blit(value_r, (sf_x/2 - value_r.get_rect().width/2,0))
        if blitit: surface.blit(sf,sf.get_rect(center=self.config.position.pos))

    if  self.config.halign.upper() == "RIGHT":
        sf.blit(value_r, (sf_x-value_r.get_rect().width,0))
        if blitit: surface.blit(sf,sf.get_rect(topright=self.config.position.pos))

    return sf



class Rect(BaseGauge):
  def __init__(self, fps=30):
    BaseGauge.__init__(self, fps=fps)


  def ParseAndConfigure(self, node, baseconfig):
      #<position x="RIGHT-20" y="BOTTOM-65" width="WIDTH-20", height="HEIGHT-20" alpha="128" />
      BaseGauge.ParseAndConfigure(self,node, baseconfig)
      position = node.getElementsByTagName("position")[0]
      x = baseconfig.MapPosition(position.getAttribute("x"))
      y = baseconfig.MapPosition(position.getAttribute("y"))
      width = baseconfig.MapPosition(position.getAttribute("width"))
      height = baseconfig.MapPosition(position.getAttribute("height"))
      alpha =  position.getAttribute("alpha")


      self.config.x = int(x)
      self.config.y = int(y)
      self.config.width = int(width)
      self.config.height = int(height)
      self.config.size = (int(width), int(height))
      self.config.alpha = int(alpha)

      return self.config


  def draw(self, surface, blitit=True):


    # draw each frame. Cycle the animation each FPS frames

    #value_r = self.fonts.label.render(self.fvalue() ,1, self.colors.label)


    sf = pygame.Surface((self.config.width,self.config.height), pygame.SRCALPHA,32)
    sf.fill(self.config.colors.fill.color)
    sf = sf.convert()
    sf.set_alpha(self.config.alpha)

    if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))


    return sf


class Line(BaseGauge):
  def __init__(self, fps=30):
    BaseGauge.__init__(self, fps=fps)


  def ParseAndConfigure(self, node, baseconfig):
      #<position x="RIGHT-20" y="BOTTOM-65" i="WIDTH-20", j="HEIGHT-20" alpha="128" width="3" />
      BaseGauge.ParseAndConfigure(self,node, baseconfig)
      position = node.getElementsByTagName("position")[0]
      x = baseconfig.MapPosition(position.getAttribute("x"))
      y = baseconfig.MapPosition(position.getAttribute("y"))
      i = baseconfig.MapPosition(position.getAttribute("i"))
      j = baseconfig.MapPosition(position.getAttribute("j"))
      width = baseconfig.MapPosition(position.getAttribute("width"))
      alpha =  position.getAttribute("alpha")


      self.config.x = int(x)
      self.config.y = int(y)
      self.config.i = int(i)
      self.config.j = int(j)
      self.config.width = int(width)
      self.config.alpha = int(alpha)

      return self.config


  def draw(self, surface, blitit=True):

    pygame.draw.aaline(surface,  self.config.colors.fill.color, (int(self.config.x), int(self.config.y)), (int(self.config.i), int(self.config.j)), self.config.width)
    return surface

#### CUSTOMIZED ###############################################################




class OneValueGauge(BaseGauge):
  def __init__(self, fps=30):
    BaseGauge.__init__(self, fps=fps)


  def draw(self, surface, blitit=True):

    """
    +--------------+
    | TITLE           |
    | BIG NUMBER   |
    +--------------+
    not centered.
    halign:
        0 -> left
        1 -> center
        2 -> right


    """

    #value_r=self.fonts.value.render(self.fvalue(),1,self.colors.value)
    #title_r=self.fonts.title.render(self.title,1, self.colors.title)


    value_r = fxtools.shadow(self.fvalue(), self.config.fonts.value.font, self.config.colors.value.color, 1)
    title_r  = fxtools.shadow(self.config.label, self.config.fonts.title.font, self.config.colors.title.color, 1)


    sf_x = max([value_r.get_rect().width, title_r.get_rect().width])
    sf_y = value_r.get_rect().height + title_r.get_rect().height

    sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA)

    #print self.config.position.pos, self.fvalue(), self.config.halign
    #sf.fill((255,0,0,255))
    #pygame.draw.rect(sf, self.config.colors.value.color  , (0,0, sf.get_rect().width, sf.get_rect().height),1)

    if self.config.halign.upper() == "LEFT":
        sf.blit(title_r, (0,0))
        sf.blit(value_r, (0,title_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))

    if self.config.halign.upper() == "CENTER":
        sf.blit(value_r, (sf_x/2 - value_r.get_rect().width/2,0))
        sf.blit(title_r, (sf_x/2 - title_r.get_rect().width/2,value_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(center=self.config.position.pos))

    if  self.config.halign.upper() == "RIGHT":
        sf.blit(title_r, (sf_x-title_r.get_rect().width,0))
        sf.blit(value_r, (sf_x-value_r.get_rect().width,title_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(topright=self.config.position.pos))



    return sf











class OneValueIntegerGauge(OneValueGauge):
  def __init__(self, fps=30):
      OneValueGauge.__init__(self, fps=fps)

  def fvalue(self):
      if self.value != None:
          return("%d" % self.value)
      return "--"

# metric & imperial handling

class DistanceGauge(OneValueGauge):
  def __init__(self, fps=30):
      OneValueGauge.__init__(self,fps=fps)

  def InitAfterConfig(self):

      # handle after
      self.unit_label = None
      OneValueGauge.InitAfterConfig(self)

  def fvalue(self):
      # comes in meters

      if self.value == None:
          return "---"

      v = float(self.value)

      if self.config.imperialunits == False:
          if v > 999.9:
              return("%3.2f Km" % (v / 1000.0))
          return("%3.1f m" % float(v))

      #feet
      v = v * 3.280839895

      if v > 999.9:
          return("%3.2f mi" % (v / 5280.0))
      return("%3.1f ft" % float(v))



class TemperatureGauge(OneValueIntegerGauge):
  def __init__(self, fps=30):
      OneValueIntegerGauge.__init__(self,fps=fps)

  def InitAfterConfig(self):

      self.unit_label = "C"
      if self.config.imperialunits:
          self.unit_label = "F"

      OneValueGauge.InitAfterConfig(self)

  def fvalue(self):
      # comes in Celsius
      if self.value == None:
          return "---"

      v = float(self.value)
      if self.config.imperialunits:
          v =  (v * 9/5.0) + 32

      return("%3d" % v)

class SpeedGauge(OneValueGauge):
  def __init__(self, fps=30):
      OneValueGauge.__init__(self,fps=fps)

  def InitAfterConfig(self):
      # comes in Km/h

      self.unit_label = "Km/h"
      if self.config.imperialunits:
          self.unit_label = "mi/h"

      OneValueGauge.InitAfterConfig(self)

  def fvalue(self):

      if self.value == None:
          return "---"

      v = float(self.value)
      if self.config.imperialunits:
         v =  (v * 0.621371192)

      return("%3.1f" % v)

class ElevationGauge(OneValueGauge):
  def __init__(self, fps=30):
      OneValueGauge.__init__(self,fps=fps)

  def InitAfterConfig(self):
      # comes in Km/h

      self.unit_label = "m"
      if self.config.imperialunits:
          self.unit_label = "ft"

      OneValueGauge.InitAfterConfig(self)

  def fvalue(self):
      # comes in meters

      if self.value == None:
          return "---"

      v = float(self.value)

      if self.config.imperialunits == False:
          return("%3.1f m" % float(v))

      #feet
      v = v * 3.280839895

      return("%3.1f ft" % float(v))

  

class TimeGauge(OneValueGauge):
  def __init__(self, fps=30):
    OneValueGauge.__init__(self, fps)

  def fvalue(self): 
      if self.value:
          return( time.strftime("%H:%M:%S",self.value.timetuple()))
      return "--:--:--"




class HRGauge(OneValueIntegerGauge):
  def __init__(self, fps=30):
        OneValueIntegerGauge.__init__(self, fps=fps)

        # animation test.

        self.animated_font_size = 0

        # imitate a heart beat. the more high the value, the more kickly it beats.

        self.max_size= 3
        self.min_size= -3

        self.framecount = 0

        self.base_rate = 20
        self.rate = self.base_rate

  def animate(self):
      self.framecount += 1

  def draw(self, surface, blitit=True):

    if not self.animated:
        return OneValueIntegerGauge.draw(self, surface, blitit)

    #
    # simple animation cycle. Hardcoded - should be changed.
    #

    if self.framecount < self.rate:
        self.animated_font_size = self.max_size + int((self.value / 25)*1.4)
        self.framecount += 1

    if self.framecount >=self.rate and self.framecount < (2*self.rate):
        self.animated_font_size = 0
        self.framecount += 1

    if self.framecount >=(2*self.rate) and self.framecount < (3*self.rate):
        self.animated_font_size = self.min_size
        self.framecount += 1

    if self.framecount >=(3*self.rate):
        self.framecount = 0

        r = int(self.value / 10.0)
        if r > 2*self.base_rate: r = 2*self.base_rate
        if r < self.base_rate: r = self.base_rate
        self.rate = 28 - r


    f = pygame.font.Font(self.config.fonts.value.fontname, self.config.fonts.value.size+5 + self.animated_font_size)


    value_r = fxtools.shadow(self.fvalue(),f, self.config.colors.value.color, 1)
    title_r  = fxtools.shadow(self.config.label, self.config.fonts.title.font, self.config.colors.title.color, 1)


    sf_x = max([value_r.get_rect().width+ self.max_size, title_r.get_rect().width])
    sf_y = value_r.get_rect().height+self.max_size + title_r.get_rect().height

    sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA)



    if self.config.halign.upper() == "LEFT":
        sf.blit(title_r, (0,0))
        sf.blit(value_r, (0,title_r.get_rect().height-(title_r.get_rect().height/2)))

        if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))

    if self.config.halign.upper() == "CENTER":
        sf.blit(value_r, (sf_x/2 - value_r.get_rect().width/2,0))
        sf.blit(title_r, (sf_x/2 - title_r.get_rect().width/2,value_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(center=self.config.position.pos))


    if self.config.halign.upper() == "RIGHT":
        sf.blit(title_r, (sf_x-title_r.get_rect().width,0))
        sf.blit(value_r, (sf_x-value_r.get_rect().width,title_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(topright=self.config.position.pos))

    return sf


# compass gauge (bearing)



class PowerGauge(OneValueIntegerGauge):
  def __init__(self,  fps=30):
        OneValueIntegerGauge.__init__(self,  fps=fps)


  def animate(self):
      self.framecount += 1

  def draw(self, surface, blitit=True):


    #
    # simple animation cycle. Hardcoded - should be changed.
    #

    if not self.animated:
        return OneValueIntegerGauge.draw(self, surface, blitit)

    gmap = GradientMap()
    if not self.value:
        r,g,b = (self.config.colors.value.color.r, self.config.colors.value.color.g, self.config.colors.value.color.b)
    else:
        r,g,b = gmap.mapval(self.value)

    #(r,g,b,a) = self.colors.value
    #c = (g0 , b0, r ,a)
    color = (g,b,r,0)


    value_r = fxtools.shadow(self.fvalue(), self.config.fonts.value.font, color, 1)
    title_r  = fxtools.shadow(self.config.label, self.config.fonts.title.font, self.config.colors.title.color, 1)


    sf_x = max([value_r.get_rect().width, title_r.get_rect().width])
    sf_y = value_r.get_rect().height + title_r.get_rect().height

    sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA)



    if self.config.halign.upper() == "LEFT":
        sf.blit(title_r, (0,0))
        sf.blit(value_r, (0,title_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))

    if self.config.halign.upper() == "CENTER":
        sf.blit(value_r, (sf_x/2 - value_r.get_rect().width/2,0))
        sf.blit(title_r, (sf_x/2 - title_r.get_rect().width/2,value_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(center=self.config.position.pos))


    if self.config.halign.upper() == "RIGHT":
        sf.blit(title_r, (sf_x-title_r.get_rect().width,0))
        sf.blit(value_r, (sf_x-value_r.get_rect().width,title_r.get_rect().height-(title_r.get_rect().height/2)))
        if blitit: surface.blit(sf,sf.get_rect(topright=self.config.position.pos))

    return sf







class GPSInfoGauge(OneValueGauge):

    def __init__(self,fps=30):
      OneValueGauge.__init__(self, fps=fps)
      self.gpx_point = None

    def fvalue(self):
        if not self.gpx_point:
            msg = "Lat: --, Lon: --"
        else:
            msg = "Lat: %7.5f, Lon: %7.5f" % (self.gpx_point.latitude, self.gpx_point.longitude)
        return msg

    def update(self, values, current_time=None):
        self.gpx_point = values[0]
        self.current_time = current_time



class OSMMapGauge(OneValueGauge):

    def __init__(self, fps=30):
      OneValueGauge.__init__(self, fps=fps)
      self.gpx_points = None
      self.gpx_point = None
      self.gpx_point_index = 0


      # optimize map generation (cache things)
      self.bounds = None
      self.img_size = (0,0)
      self.mapper = None
      self.mapimg = None

    def ParseAndConfigure(self, node, baseconfig):
      OneValueGauge.ParseAndConfigure(self,node, baseconfig)
      mapval = node.getElementsByTagName("map")[0]
      width = mapval.getAttribute("width")
      height = mapval.getAttribute("height")
      empty = mapval.getAttribute("empty") or False
      alpha = mapval.getAttribute("alpha")


      self.config.map = BaseConfig()
      self.config.map.size = (int(width), int(height))
      self.config.map.alpha = int(alpha)
      self.config.map.empty = False
      if empty.lower() == "true":
          self.config.map.empty = True


      return self.config


    def CreateMap(self):
        gpx_item = GPXItem(self.gpx_points)
        self.bounds = gpx_item.Bounds()
        NW = geo.Location(self.bounds.max_latitude, self.bounds.min_longitude)
        NE = geo.Location(self.bounds.max_latitude, self.bounds.max_longitude)
        SE = geo.Location(self.bounds.min_latitude, self.bounds.max_longitude)
        SW = geo.Location(self.bounds.min_latitude, self.bounds.min_longitude)

        self.img_size     = Size(self.config.map.size[0],self.config.map.size[1])
        self.mapper       = OSMMapper(self.img_size)
        #map         = mapper.GetMapBB((NW,NE,SE,SW), mapempty=False)

        self.mapimg = self.mapper.GetMapBB((NW,NE,SE,SW), mapempty=self.config.map.empty, 
                                           mapcolor=self.config.colors.bg.colortuple, 
                                           bounding_box=False)
        #mapimg = mapper.GetMapCentered(gpx_point, 200, mapempty=True, bounding_box=False)


    def update(self, values, current_time=None):
        # map problem here
        self.gpx_point_index = values[0]
        self.gpx_point = self.gpx_points[self.gpx_point_index]
        self.current_time = current_time

    def set_points(self, points):
        self.gpx_points = points

    def draw(self, surface, blitit=True):

        # use created map (speed up things)

        maptemp = self.mapimg.copy()

        # some position info. TBD


        self.mapper.ProjectPoints(self.gpx_points, maptemp)
        self.mapper.ProjectCircle(self.gpx_points[0], maptemp, self.config.colors.start.colortuple) # start
        self.mapper.ProjectCircle(self.gpx_points[-1], maptemp, self.config.colors.end.colortuple) # end

        if self.config.interpolate:
            distance_i = DistanceI( self.gpx_points[self.gpx_point_index-1], self.gpx_points[self.gpx_point_index], self.current_time )
            bearing = gpxtoolbox.bearing(self.gpx_points[self.gpx_point_index-1] , self.gpx_points[self.gpx_point_index])

            interpolated_point = geo.LocationDelta(distance=distance_i, angle=bearing)
            lat, lon = interpolated_point.move_by_angle_and_distance(self.gpx_point)

            interpolated_point.latitude = lat
            interpolated_point.longitude = lon
            self.mapper.ProjectCircle(interpolated_point, maptemp, self.config.colors.point.colortuple) #
        else:
            self.mapper.ProjectCircle(self.gpx_point, maptemp, self.config.colors.point.colortuple) #


        mode = maptemp.imagemap.mode
        size = maptemp.imagemap.size
        data = maptemp.imagemap.tobytes() # tostring() was deprecated

        map_image = pygame.image.fromstring(data, size, mode)

        #sf_x = preferences.map.size[0]
        #sf_y = preferences.map.size[1]
        #sf = pygame.Surface((sf_x,sf_y), pygame.SRCALPHA)

        #map_image.set_colorkey((242,239,233)) # OSM BG
        pygame.draw.rect(map_image, self.config.colors.border.colortuple, (0,0,map_image.get_rect().width, map_image.get_rect().height),1)
        map_image = map_image.convert()
        map_image.set_alpha(self.config.map.alpha)

        #sf.blit(map_image,((prev_sf.get_rect().width/2)-map_image.get_rect().width/2,prev_sf.get_rect().height))



        if self.config.halign.upper() == "LEFT":
            if blitit: surface.blit(map_image,map_image.get_rect(topleft=self.config.position.pos))

        if self.config.halign.upper() == "CENTER":
            if blitit: surface.blit(map_image,map_image.get_rect(center=self.config.position.pos))

        if self.config.halign.upper() == "RIGHT":
            if blitit: surface.blit(map_image,map_image.get_rect(topright=self.config.position.pos))


        return map_image


#
# draw an altitude graph based on points.
#
######NEW####
class AltGraphGauge(OneValueGauge):

    def __init__(self, fps=30):
      OneValueGauge.__init__(self, fps=fps)
      self.gpx_points = None
      self.point_index = None
      self.elevation = None
      self.distance = None
      
      # optimize map generation (cache things)
      self.bounds = None
      self.img_size = (0,0)
      self.mapper = None
      self.mapimg = None
      self.track_length = 0
      
    def ParseAndConfigure(self, node, baseconfig):
      OneValueGauge.ParseAndConfigure(self,node, baseconfig)
      #<graph width="256" height="64" alpha="128" markradius="2" pointradius="3" xgap="10" ygap="15" />
      graph = node.getElementsByTagName("graph")[0]
      width = graph.getAttribute("width")
      height = graph.getAttribute("height")
      alpha = graph.getAttribute("alpha")
      markradius = graph.getAttribute("markradius")
      pointradius = graph.getAttribute("pointradius")
      xgap = graph.getAttribute("xgap")
      ygap = graph.getAttribute("ygap")


      self.config.graph = BaseConfig()
      self.config.graph.size = (int(width), int(height))
      self.config.graph.alpha = int(alpha)
      self.config.graph.markradius = int(markradius)
      self.config.graph.pointradius = int(pointradius)
      self.config.graph.xgap = int(xgap)
      self.config.graph.ygap = int(ygap)

      return self.config


    def CreateMap(self):

        #
        # create a empty cambas with the elevation data.
        # calculate space for the points, draw the elevation profile.
        #


        self.mapimg = pygame.Surface(self.config.graph.size, pygame.SRCALPHA, 32)
        self.mapimg.fill(self.config.colors.bg.color)
        self.mapimg.convert()
        self.mapimg.set_alpha(self.config.graph.alpha)

        ygap = self.config.graph.ygap
        xgap = self.config.graph.xgap

        gpx_item = GPXItem(self.gpx_points)
        (min_elevation, max_elevation) = gpx_item.gpx.get_elevation_extremes()
        self.track_length = gpx_item.get_distance()
  
        delta_elevation = (max_elevation - min_elevation)



  
        
        # calculate space based on distance instead gpx_points
        #
        #xincr = (self.config.graph.size[0]-(2*xgap)) / float((len(self.gpx_points)-1))
        xincr = (self.config.graph.size[0]-(2*xgap)) / self.track_length if  self.track_length > 0 else 0
        yincr = (self.config.graph.size[1]-(2*ygap)) / delta_elevation   if delta_elevation > 0 else 0

        fill_points = []

        y = 0
        x = 0
        d = 0
        for i in range(len(self.gpx_points)):
            
            if i > 0:
                d += Distance(self.gpx_points[i-1], self.gpx_points[i])
            
            
             
            x = (d*xincr)+xgap
            
            if i == 0:
                y = (self.config.graph.size[1]-ygap) - (yincr * (self.gpx_points[0].elevation - min_elevation))
            else:
                y = (self.config.graph.size[1]-ygap) - (yincr * (self.gpx_points[i-1].elevation - min_elevation))

            #print i, d, x, y, self.gpx_points[i].elevation, self.track_length
            # as we use the lines with array of points, we don't need to calculate next point.

            #if (i+1 < len(self.gpx_points)):
            #    k = ((i+1)*xincr) + xgap
            #    l = (self.config.graph.size[1]-ygap) - (yincr * (self.gpx_points[i+1].elevation - min_elevation))
            #else:
            #    k = x
            #    l = y

            #c = self.config.colors.fg.color
            #if i == 0:
            #    c = self.config.colors.start.color
            #if i == len(self.gpx_points)-1:
            #    c = self.config.colors.end.color

            fill_points.append((x,y))
            #pygame.draw.line(self.mapimg,  self.config.colors.line.color, (int(x), int(y)), (int(k), int(l)),width=2)
            #pygame.draw.aaline(self.mapimg,  self.config.colors.fg.color, (int(x), int(y)), (int(k), int(l)),3)
            #pygame.gfxdraw.filled_circle(self.mapimg, int(x), int(y), 3, (255,255,0))

        # add the rest.


        

        # end the polygon so we can fill it
        # ygap/10 to get some room at the bottom of the graph

        fill_points = [ (xgap, self.config.graph.size[1]-ygap+(ygap/5)) ] + fill_points # bottom left (first)
        fill_points.append( (x, self.config.graph.size[1]-ygap+(ygap/5))  ) # bottom right (last)
        
        pygame.draw.polygon( self.mapimg, self.config.colors.fg.colortuple, fill_points, 0)
        
        fill_points = fill_points[1:-1]
        pygame.draw.lines( self.mapimg, self.config.colors.line.colortuple, False, fill_points, 3)
        
        pygame.draw.rect(self.mapimg, self.config.colors.border.colortuple, (0,0,self.mapimg.get_rect().width, self.mapimg.get_rect().height),1)




    def update(self, values, current_time=None):
        # check metric="" field in xml configuration (multi metric)
        self.point_index = values[0]
        self.distance = values[1]
        self.elevation = values[2]
        self.current_time = current_time

        if not self.elevation:  self.elevation = 0

    def set_points(self, points):
        self.gpx_points = points

    def draw(self, surface, blitit=True):

        # use created map (speed up things)

        #elevation = self.gpx_points[self.point_index].elevation
        elevation = self.elevation or 0.0

        #if self.config.interpolate:

            #elevation = Interpolate( self.gpx_points[self.point_index-1].time, self.gpx_points[self.point_index-1].elevation ,
            #                         self.gpx_points[self.point_index].time,   self.gpx_points[self.point_index].elevation ,
            #                         self.current_time )


        maptemp = self.mapimg.copy()
        #maptemp = maptemp.convert()
        #maptemp.set_alpha(self.config.graph.alpha)

        ygap = self.config.graph.ygap
        xgap = self.config.graph.xgap

        gpx_item = GPXItem(self.gpx_points)
        (min_elevation, max_elevation) = gpx_item.gpx.get_elevation_extremes()
        delta_elevation = (max_elevation - min_elevation)


        max_r_v = "%3.2f m" % max_elevation
        min_r_v = "%3.2f m" % min_elevation
        len_r_v = "(%3.2f m)" % self.track_length
        #elev_r_v = "%3.2f m" % self.gpx_points[self.point_index].elevation
        if elevation:
            elev_r_v = "%3.2f m" % elevation
        else:
            elev_r_v = "--- m "

        if self.config.imperialunits:
            max_r_v = "%3.2f ft" % (max_elevation * 3.280839895)
            min_r_v = "%3.2f ft" % (min_elevation * 3.280839895)
            len_r_v = "(%3.2f ft)" % (self.track_length  * 3.280839895)
            elev_r_v = "%3.2f ft" % (elevation * 3.280839895)

        max_r = fxtools.shadow(max_r_v , self.config.fonts.label.font, self.config.colors.label.color, 1)
        min_r = fxtools.shadow(min_r_v, self.config.fonts.label.font, self.config.colors.label.color, 1)
        len_r = fxtools.shadow(len_r_v , self.config.fonts.label.font, self.config.colors.label.color, 1)
        elev_r = fxtools.shadow(elev_r_v , self.config.fonts.mark.font, self.config.colors.mark.color, 1)

        maptemp.blit(max_r, (2,1))
        maptemp.blit(min_r, (0,maptemp.get_rect().height-15))
        maptemp.blit(len_r, (maptemp.get_rect().width-len_r.get_rect().width-2,1))


        # calculate space.
        #
        #xincr = (self.config.graph.size[0]-(2*xgap)) / float((len(self.gpx_points)-1))
        xincr = (self.config.graph.size[0]-(2*xgap)) / self.track_length if self.track_length > 0 else 0
        yincr = (self.config.graph.size[1]-(2*ygap)) / delta_elevation   if delta_elevation > 0 else 0

        
        if not self.distance:
            x = xgap
        else:
            x = (self.distance*xincr)+xgap
        
        #x = (self.point_index*xincr)+xgap
        #y = (self.config.graph.size[1]-ygap) - (yincr * (self.gpx_points[self.point_index].elevation - min_elevation))
        y = (self.config.graph.size[1]-ygap) - (yincr * (elevation - min_elevation))

        #if self.config.interpolate: 
        #    x -= 1  # cludge to fix the "averaging of points over the line :/"
        #    y += 1  # the problem IS IN THE ELEVATION, no in the DISTANCE value.

        #print x, y, self.distance, elevation

        #XXX
        xx = int(x)
        yy = int(y)

        ## move label before point if we are at the end. Gravity it in order to fix the spaces.
        ##
        if yy - elev_r.get_rect().height < (ygap):    # top
            yy = int(y) +2
        elif yy - elev_r.get_rect().height > maptemp.get_rect().height-ygap: # bottom
            yy = int(y) +2
        else:
            yy = int(y) - elev_r.get_rect().height - 2

        if xx + elev_r.get_rect().width > maptemp.get_rect().width-xgap: # right
            xx = int(x) - elev_r.get_rect().width - 2
        else:
            xx = int(x) +2





        maptemp.blit( elev_r, elev_r.get_rect(topleft=(int(xx), int(yy))) )

        #print self.point_index, x, y

        pygame.gfxdraw.filled_circle(maptemp, int(x), int(y), self.config.graph.pointradius, self.config.colors.markpoint.colortuple)



        if self.config.halign.upper() == "LEFT":
            if blitit: surface.blit(maptemp,maptemp.get_rect(topleft=self.config.position.pos))

        if self.config.halign.upper() == "CENTER":
            if blitit: surface.blit(maptemp,maptemp.get_rect(center=self.config.position.pos))

        if self.config.halign.upper() == "RIGHT":
            if blitit: surface.blit(maptemp,maptemp.get_rect(topright=self.config.position.pos))
        
        # update counter
        self.framecount += 1
        return maptemp




######NEW####



#
# draw an altitude graph based on points.
#

class ECGGauge(OneValueGauge):

    def __init__(self,fps=30):
      OneValueGauge.__init__(self,  fps=fps)
      self.idx = 0
      self.fcounter = 0
      self.paint = 0

    def ParseAndConfigure(self, node, baseconfig):
      OneValueGauge.ParseAndConfigure(self,node, baseconfig)
      #<ecgmonitor width="256" height="32" alpha="128" markradius="2" pointradius="3" ygap="15" />
      ecgmonitor = node.getElementsByTagName("ecgmonitor")[0]
      width = ecgmonitor.getAttribute("width")
      height = ecgmonitor.getAttribute("height")
      alpha = ecgmonitor.getAttribute("alpha")
      markradius = ecgmonitor.getAttribute("markradius")
      pointradius = ecgmonitor.getAttribute("pointradius")
      ygap = ecgmonitor.getAttribute("ygap")

      self.config.ecgmonitor = BaseConfig()
      self.config.ecgmonitor.size = (int(width), int(height))
      self.config.ecgmonitor.alpha = int(alpha)
      self.config.ecgmonitor.markradius = int(markradius)
      self.config.ecgmonitor.pointradius = int(pointradius)
      self.config.ecgmonitor.ygap = int(ygap)

      return self.config

    def draw(self, surface, blitit=True):

        # use created map (speed up things)

        sf = pygame.Surface(self.config.ecgmonitor.size, pygame.SRCALPHA)
        sf.fill(self.config.colors.bg.color)


        pygame.draw.rect(sf, self.config.colors.border.colortuple, (0,0,sf.get_rect().width, sf.get_rect().height),1)

        bpm_r = fxtools.shadow("BPM: %3d" % self.value , self.config.fonts.mark.font, self.config.colors.mark.color, 1)
        sf.blit(bpm_r, (2,1))

        #
        # calculate the point where we are. Go from left to right, then scroll the points
        # to the right. Try to move based on seconds.
        #
        ygap = self.config.ecgmonitor.ygap
        x = self.idx % self.config.ecgmonitor.size[0]
        y = (self.config.ecgmonitor.size[1] - ygap)

        frame_t = 1 / self.fps
        bpm_t = 0
        if self.value != 0:
            bpm_t = 60.0 / self.value

        if self.fcounter >= bpm_t:
            self.paint = 5
            self.fcounter = 0.0

        self.fcounter += frame_t

        if self.paint > 0:
            incry = (self.config.ecgmonitor.size[1]) / 2.0
            y = y - incry
            self.paint -= 1




        #max_hr = 200
        #min_hr = 30
        #deltahr = (max_hr - min_hr)
        #ygap = preferences.altmap.ygap
        #yincr = (preferences.hrecg.size[1]-(2*ygap)) / float(deltahr)
        #y = (preferences.hrecg.size[1]-ygap) - (yincr * (self.value - min_hr))
        #print x,y, self.value

        self.idx += 1

        #pygame.draw.aaline(self.mapimg,  self.colors.fg, (int(x), int(y)), (int(k), int(l)),3)
        pygame.gfxdraw.filled_circle(sf, int(x), int(y), self.config.ecgmonitor.markradius, self.config.colors.fg.color)



        if self.config.halign.upper() == "LEFT":
            if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))

        if self.config.halign.upper() == "CENTER":
            if blitit: surface.blit(sf,sf.get_rect(center=self.config.position.pos))

        if self.config.halign.upper() == "RIGHT":
            if blitit: surface.blit(sf,sf.get_rect(topright=self.config.position.pos))


        return sf





class BearingGauge(OneValueGauge):

    def __init__(self,  fps=30):
      OneValueGauge.__init__(self, fps=fps)

    def ParseAndConfigure(self, node, baseconfig):
      OneValueGauge.ParseAndConfigure(self,node, baseconfig)
      #<compass width="40" height="40" alpha="128" markradius="2" pointradius="3" ygap="15" png="res/arrow_dark.png"/>
      compass = node.getElementsByTagName("compass")[0]
      width = compass.getAttribute("width")
      height = compass.getAttribute("height")
      alpha = compass.getAttribute("alpha")
      markradius = compass.getAttribute("markradius")
      pointradius = compass.getAttribute("pointradius")
      ygap = compass.getAttribute("ygap")
      png = compass.getAttribute("png")

      self.config.compass = BaseConfig()
      self.config.compass.size = (int(width), int(height))
      self.config.compass.alpha = int(alpha)
      self.config.compass.markradius = int(markradius)
      self.config.compass.pointradius = int(pointradius)
      self.config.compass.ygap = int(ygap)
      self.config.compass.png = png
      #self.config.compass.img = pygame.image.load(self.config.compass.png).convert_alpha()

      imgpil = Image.open(self.config.compass.png)
      self.config.compass.img = pygame.image.frombuffer( imgpil.tobytes('raw', 'BGRA', 0, 1), imgpil.size, 'RGBA')
      self.config.compass.img.fill((255, 255, 255, self.config.compass.alpha), None, pygame.BLEND_RGBA_MULT)

      return self.config

    def rot_center(self, image, angle):
        """rotate a Surface, maintaining position."""

        newsf = pygame.Surface(self.config.compass.size, pygame.SRCALPHA, 32)
        newsf.convert()
        newsf.set_alpha(self.config.compass.alpha)
        loc = image.get_rect().center  #rot_image is not defined
        rot_sprite = pygame.transform.rotate(image, angle)
        #rot_sprite.get_rect(center=self.rect.center)
        newsf.blit(rot_sprite, rot_sprite.get_rect(center=loc))
        return newsf

    def fvalue(self):
        if self.value == None:
            return "---"

        return "%03d" % (round(self.value) % 360)

    def draw(self, surface, blitit=True):

        # use created map (speed up things)

        sf = pygame.Surface(self.config.compass.size, pygame.SRCALPHA,32)
        sf.fill(self.config.colors.bg.color)
        sf.set_alpha(self.config.compass.alpha)
        bearing_r = fxtools.shadow(self.fvalue() , self.config.fonts.mark.font, self.config.colors.mark.color, 1)
        pygame.draw.rect(sf, self.config.colors.border.colortuple, (0,0,sf.get_rect().width, sf.get_rect().height),1)


        angle = 0
        if self.value != None:
            angle = self.value % 360
        sf = self.rot_center(self.config.compass.img, 360 - (angle))

        cx = ( sf.get_rect().width / 2.0) - (bearing_r.get_rect().width / 2.0)
        cy = ( sf.get_rect().height / 2.0) -  (bearing_r.get_rect().height / 2.0)

        sf.blit(bearing_r, (cx, cy))

        #pygame.draw.aaline(self.mapimg,  self.colors.fg, (int(x), int(y)), (int(k), int(l)),3)
        #pygame.gfxdraw.filled_circle(sf, int(x), int(y), preferences.hrecg.markradius, self.colors.fg)

        #pygame.draw.rect(sf, self.colors.border, (0,0,sf.get_rect().width,sf.get_rect().height),1)

        if self.config.halign.upper() == "LEFT":
            if blitit: surface.blit(sf,sf.get_rect(topleft=self.config.position.pos))

        if self.config.halign.upper() == "CENTER":
            if blitit: surface.blit(sf,sf.get_rect(center=self.config.position.pos))

        if self.config.halign.upper() == "RIGHT":
            if blitit: surface.blit(sf,sf.get_rect(topright=self.config.position.pos))


        return sf



class Picture(BaseGauge):

    def __init__(self,  fps=30):
      BaseGauge.__init__(self, fps=fps)

    def ParseAndConfigure(self, node, baseconfig):
      BaseGauge.ParseAndConfigure(self,node, baseconfig)
      #<img width="256" height="256" alpha="128" png="res/sample_bitmap.png" />
      img = node.getElementsByTagName("img")[0]
      width = int(img.getAttribute("width"))
      height = int(img.getAttribute("height"))
      alpha = img.getAttribute("alpha")
      png = img.getAttribute("png")

      self.config.img = BaseConfig()
      self.config.img.size = (width, height)
      self.config.img.alpha = int(alpha)
      self.config.img.png = png
      # use this, get wrong color channels :/
      # better use PIL approach
      #self.config.img.img = pygame.image.load(self.config.img.png).convert_alpha()

      # load pil image, do the work to get the alpha and values working
      imgpil = Image.open(self.config.img.png)
      self.config.img.img = pygame.image.frombuffer( imgpil.tobytes('raw', 'BGRA', 0, 1), imgpil.size, 'RGBA')
      self.config.img.img.fill((255, 255, 255, self.config.img.alpha), None, pygame.BLEND_RGBA_MULT)

      # scale image to size.
      if self.config.img.img.get_rect().width != width or self.config.img.img.get_rect().height != height:
          self.config.img.img = pygame.transform.smoothscale(self.config.img.img, (width, height))

      return self.config



    def draw(self, surface, blitit=True):


        if self.config.halign.upper() == "LEFT":
            if blitit: surface.blit(self.config.img.img,self.config.img.img.get_rect(topleft=self.config.position.pos))

        if self.config.halign.upper() == "CENTER":
            if blitit: surface.blit(self.config.img.img,self.config.img.img.get_rect(center=self.config.position.pos))

        if self.config.halign.upper() == "RIGHT":
            if blitit: surface.blit(self.config.img.img,self.config.img.img.get_rect(topright=self.config.position.pos))


        return self.config.img.img

















