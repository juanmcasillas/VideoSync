# mapquest handle data.
# http://otile1.mqcdn.com/tiles/1.0.0/osm/10/10/10.png
# server from otitle1-4
# http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
# http://otile[1-4].mqcdn.com/tiles/1.0.0/osm/ZOOM/X/Y.png
# This returns the NW-corner of the square. Use the function with xtile+1 and/or ytile+1 to get the other corners.
# With xtile+0.5 & ytile+0.5 it will return the center of the tile. // Doens't work.
# http://wiki.openstreetmap.org/wiki/Zoom_levels
# tiles are 256x256 pixels

#
# MAPPER.py
# create some classes and libraries to improve the mapper based on OpenStreetMaps
# Juan M. Casillas <juanm.casillas@gmail.com>
# 10/Nov/2015
#

import math
import random
import urllib.request, urllib.error, urllib.parse
import io
import os.path
from collections import namedtuple
from PIL import Image, ImageDraw

from gpxtoolbox import *
from gpxpy import geo
import rainbowvis
from helpers import set_http_proxy, get_page_content

Size = namedtuple('Size', 'width height')
Point2D = namedtuple('Point', 'x y')

DEBUG_ME = True
random.seed()




class MapItem:
		"A container to store the data associated with the map created"

		def __init__(self,imagemap, zoom, origin, crop_origin, tiles_sz):
			self.imagemap 		= imagemap		# image where map is draw (PIL)
			self.zoom	  		= zoom			# calculated zoom (OSM, 0 - 19)
			self.origin			= origin		# Origin Tile (NW) use for project data in the map relative to it)
			self.crop_origin	= crop_origin	# Origin of Crop (to center the map)
			self.tiles_sz		= tiles_sz		# size of the map, in tiles

		def  __copy__(self):
			return MapItem(self.imagemap.copy(), self.zoom, self.origin, self.crop_origin, self.tiles_sz)

		def copy(self):
			return self.__copy__()
		
		def resolution(self):
			EARTH_SIZE = 156543.03
			#zoom = int(math.ceil( math.log( self.EARTH_SIZE / resolution, 2) ))
			return (EARTH_SIZE / (math.pow(2,self.zoom)))
			
			
class GenericMapper:


	def __init__(self, img_sz):
		self.debug = True
		self.img_sz = img_sz

	def Debug(self, debugme):
		self.debug = debugme
		
	def GetMapBB(self,bb):
		"""
		Get a PIL image element, of the given size (Size), inside the Bounding Box (BB). Zoom is calculated
		automatically to fix inside the image. Coords are given:
		bb = ( NW, NE, SE, SW )
		"""

		pass

	def GetMapCentered(self,point,radius):
		"""
		Get a PIL image element of the given size, centered on point, with radius "radius" in meters
		zoom is set to fix inside the image automatically
		"""
		pass

	def GetEmptyMap(self):
		"""
		return an empty image with the image size.
		"""
		pass

	def tile2url(tile, zoom):
		"""
		Given a (X,Y) tile, calculate the URL from the tile server. By default, use
		mapquest format
		"""

		servernum = random.randrange(1,4)
		url = "http://otile%d.mqcdn.com/tiles/1.0.0/osm/%d/%d/%d.png" % (servernum, zoom, tile[0], tile[1])
		return url




class OSMMapper(GenericMapper):

	EARTH_SIZE 	= 156543.03		# size of the earth in meters
	TILE_X_SZ  	= 256			# tile x size from OSM Maps
	TILE_Y_SZ 	= 256			# tile y size from OSM Maps
	#cachedir   	= "cache"		# directory name where cache tiles is stored.
	debug	   	= 2				# debug level, from 0 to 10
	MAX_ZOOM	= 19

	def __init__(self, img_sz, cachedir="cache"):
		GenericMapper.__init__(self, img_sz)
		self.cachedir = cachedir

	def GetMapBB(self,bb, mapempty=False,mapcolor=None, zoom_base=None, bounding_box=True):

		NW,NE,SE,SW = bb
		OffSetNW = Point2D(0,0)
		OffSetSE = Point2D(0,0)

		BOUNDING_BOX = bounding_box



		# calculate ZOOM that fits on that.
		# 0 zoom	360 degreess 	156412 m/p
		# 1 zoom	180	degreess	78206 m/p (half)
		# 2 zoom	90				39103 m/p ....

		# 2^zoom = 156412 / Resolution
		# some math inside...
		# zoom = ABS( log_2 ( 156412 / Resolution ) )
		# tile_res = EARTH_SIZE / (math.pow(2,zoom))
		# resolution = 1.193 gives zoom 17. Right.

		#for zoom in range(18,-1,-1):
		#	resolution = math.fabs( EARTH_SIZE * math.cos(gpx.Center().latitude) / (math.pow(2,zoom)))
		#	if resolution*tiles_sz.width*TILE_X_SZ >= width and resolution*tiles_sz.height*TILE_Y_SZ>=height:
		#		break

		#print NW,NE,SW,SE
		if zoom_base:
			zoom = zoom_base
		else:
			distance = self._offset_meters(SE,NW)

			meters_per_pixel_required_x =  (distance.width  / self.img_sz.width  )
			meters_per_pixel_required_y =  (distance.height / self.img_sz.height )

			resolution = max( meters_per_pixel_required_x, meters_per_pixel_required_y)

			if DEBUG_ME and self.debug:
				print("W,H: ", distance)
				print("Mrx, Mry: ",meters_per_pixel_required_x, meters_per_pixel_required_y)
				print("res", resolution)
			try:
				zoom = int(math.ceil( math.log( self.EARTH_SIZE / resolution, 2) ))
				if zoom > self.MAX_ZOOM:
					zoom = self.MAX_ZOOM
			except:
				zoom = 1

		while True:
			#resolution = math.fabs( EARTH_SIZE * math.cos(NW.latitude) / (math.pow(2,zoom)))

			tiles_NW = self.deg2num( NW, zoom )
			tiles_SE = self.deg2num( SE, zoom )

			tiles_sz = Size( int(math.fabs(tiles_NW.x-tiles_SE.x))+1,  int(math.fabs(tiles_NW.y-tiles_SE.y))+1 )
			#tiles_sz.width = int(math.fabs(tiles_NW.x-tiles_SE.x))+1
			#tiles_sz.height = int(math.fabs(tiles_NW.y-tiles_SE.y))+1

			NWpx = self._Point2XY(NW, tiles_NW, zoom )
			SEpx = self._Point2XY(SE, tiles_NW, zoom )

			# distance in pixels from NWpx to SEpx
			bb_width,bb_height = (SEpx.x-NWpx.x, SEpx.y-NWpx.y )

			if DEBUG_ME and self.debug:
				print("-" * 50)
				print("NWpx:    ", NWpx)
				print("SEpx:    ", SEpx)
				print("BBWidth: ", bb_width, bb_height)
				print("Zoom: %f" % (zoom))
				print("NW: %s, SE: %s" % (tiles_NW, tiles_SE))
				print("XY Size : ", tiles_sz)
				print("IMG Size: %d, %d" % (self.img_sz.width, self.img_sz.height))
				print("XY px size: %d,%d" % (tiles_sz.width* self.TILE_X_SZ, tiles_sz.height* self.TILE_Y_SZ))

			if bb_width > self.img_sz.width or bb_height > self.img_sz.height and not zoom_base:
				zoom -= 1
			else:
				break


		#
		# now, we have to calculate if we are going to move the grid to match the size of the image.
		# BB has to be inside the canvas. If not, add some room.
		#

		img_center = Size( self.img_sz.width / 2, self.img_sz.height / 2)
		bb_center  = Point2D( NWpx.x+int(math.fabs((SEpx.x- NWpx.x) / 2)), NWpx.y+int(math.fabs((SEpx.y- NWpx.y) / 2)) )# The center from the NW point
		crop_origin = Point2D( bb_center.x - img_center.width, bb_center.y - img_center.height)

		if DEBUG_ME and self.debug:
			print("=" * 80)
			print("FINAL CONFIG")
			print("NWpx:    ", NWpx)
			print("SEpx:    ", SEpx)
			print("BBWidth: ", bb_width, bb_height)
			print("Zoom: %f" % (zoom))
			print("NW: %s, SE: %s" % (tiles_NW, tiles_SE))
			print("XY Size : " , tiles_sz)
			print("IMG Size: %d, %d" % (self.img_sz.width, self.img_sz.height))
			print("XY px size: %d,%d" % (tiles_sz.width*self.TILE_X_SZ, tiles_sz.height*self.TILE_Y_SZ))
			print("Image Center: %s", img_center)
			print("BB Center   : %s", bb_center)
			print("Crop Origin : %s", crop_origin)

		if crop_origin.x < 0:
			if DEBUG_ME and self.debug: print("need space from LEFT (X)")
			tilediff = int(math.ceil(math.fabs(crop_origin.x/self.TILE_X_SZ)))
			OffSetNW = Point2D(OffSetNW.x-tilediff, OffSetNW.y)
			#tiles_sz.width += tilediff
			tiles_sz = Size( tiles_sz.width + tilediff, tiles_sz.height )

			crop_origin = Point2D(crop_origin.x+(self.TILE_X_SZ*tilediff), crop_origin.y)


		if crop_origin.y < 0:
			if DEBUG_ME and self.debug: print("need space from TOP (Y)")
			tilediff = int(math.ceil(math.fabs(crop_origin.y/self.TILE_Y_SZ)))
			OffSetNW= Point2D(OffSetNW.x, OffSetNW.y-tilediff)
			#tiles_sz.height += tilediff
			tiles_sz = Size( tiles_sz.width, tiles_sz.height+ tilediff )

			crop_origin = Point2D(crop_origin.x, crop_origin.y+(self.TILE_Y_SZ*tilediff))

		if math.fabs(crop_origin.y)+self.img_sz.height > self.TILE_Y_SZ*tiles_sz.height:
			if DEBUG_ME and self.debug: print("need space from BOTTOM (Y)")
			tilediff = int(math.ceil((math.fabs(crop_origin.y)+self.img_sz.height-(self.TILE_Y_SZ*tiles_sz.height))/self.TILE_Y_SZ))
			OffSetSE= Point2D(OffSetSE.x, OffSetSE.y+tilediff)
			#tiles_sz.height += tilediff
			tiles_sz = Size( tiles_sz.width, tiles_sz.height+ tilediff )

		if math.fabs(crop_origin.x)+self.img_sz.width > self.TILE_X_SZ*tiles_sz.width:
			if DEBUG_ME and self.debug: print("need space from RIGHT (X)")
			tilediff = int(math.ceil((math.fabs(crop_origin.x)+self.img_sz.width-(self.TILE_X_SZ*tiles_sz.width))/self.TILE_X_SZ))
			OffSetSE= Point2D(OffSetSE.x+tilediff, OffSetSE.y)
			#tiles_sz.width += tilediff
			tiles_sz = Size( tiles_sz.width + tilediff, tiles_sz.height )

		if DEBUG_ME and self.debug:
			print("Offset NW: %s", OffSetNW)
			print("Offset SE: %s", OffSetSE)

		# get the box, do the magic.

		if not mapempty:
			canvas = self.GetMapTiles((tiles_NW.x+OffSetNW.x, tiles_NW.y+OffSetNW.y),zoom,tiles_sz)
		else:
			canvas = Image.new("RGBA",(self.TILE_X_SZ*(tiles_sz.width), self.TILE_Y_SZ*(tiles_sz.height)),mapcolor)

		#
		# generate the proyection of a LAT,LON to our coordinate space in the image.
		# (0,0) -> LEFT,TOP of the image. This point is:
		#

		tile_origin = tiles_NW
		tile_origin = (tiles_NW.x+OffSetNW.x, tiles_NW.y+OffSetNW.y)

		# debug info
		if BOUNDING_BOX:
			self._DrawBBox(NW,NE,SE,SW, canvas, tile_origin, zoom)

		retmap = MapItem(canvas, zoom, tile_origin, crop_origin, tiles_sz)
		return self._FinishMap(retmap)



	def GetMapCentered(self,center,radius,mapempty=False,zoom_base=None, bounding_box=True):
		"""
		Get a Point (center) and calculate the borders of the bounding box, using radius in meters.
		From GEO:
			NORTH = 0
			EAST = 90
			SOUTH = 180
			WEST = 270
		"""

		NW = geo.Location(center.latitude, center.longitude)
		NE = geo.Location(center.latitude, center.longitude)
		SE = geo.Location(center.latitude, center.longitude)
		SW = geo.Location(center.latitude, center.longitude)

		NW.move(geo.LocationDelta(distance=radius, angle=270+45))
		NE.move(geo.LocationDelta(distance=radius, angle=0+45))
		SE.move(geo.LocationDelta(distance=radius, angle=90+45))
		SW.move(geo.LocationDelta(distance=radius, angle=180+45))

		return self.GetMapBB( (NW,NE,SE,SW), mapempty, zoom_base,bounding_box)






	# internal functions ##################################################################################

	# latitude, longitude converstion to X,Y

	def _deg2num(self,point, zoom):
		"""
		convert a Latitude, Longitude, Zoom point to X,Y tile. Use float, in order to use this function
		to calculate the proyection
		"""

		lat_rad = math.radians(point.latitude)
		n = 2.0 ** zoom
		xtile = (point.longitude + 180.0) / 360.0 * n
		ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
		return Point2D(xtile, ytile)

	def deg2num(self,point , zoom):
		"convert a Latitude, Longitude, Zoom point to X,Y tile"
		x, y = self._deg2num(point , zoom)
		return Point2D(int(x), int(y))

	def num2deg(self,xtile, ytile, zoom):
		"get a given tile, calculate the NW point of the TILE. + (0.5,0,5) gives the center of the tile"
		n = 2.0 ** zoom
		lon_deg = xtile / n * 360.0 - 180.0
		lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
		lat_deg = math.degrees(lat_rad)
		return (lat_deg, lon_deg)


	# tile & cache management

	def tile2url(self,tile, zoom):
		letters = [ 'a', 'b', 'c' ]
		letter = letters[random.randrange(0,3)]
		# changed to SECURE.
		url = "https://%s.tile.openstreetmap.org/%d/%d/%d.png" % (letter, zoom, tile[0], tile[1])
		return url

	def TileCache(self,tile,zoom):

		url = self.tile2url(tile,zoom)

		cachedir = [self.cachedir] + url.split('/')[-4:]
		urlp = os.sep.join(cachedir)
		cache_tile = True

		if os.path.exists(urlp):
			r = Image.open(urlp)
			if DEBUG_ME:
				print("C %d, %d, %s" % (tile.x, tile.y, url))
			return r
		else:
			if DEBUG_ME:
				print("X %d, %d, %s" % (tile.x, tile.y, url))

		# get and save
		try:
			#set the proxy if required.
			#set_http_proxy('proxy.addr.com:8080')
			#fd = urllib.request.urlopen(url)
			fd = get_page_content(url)
			image_file = io.BytesIO(fd.read())
			fd.close()
			tileimage = Image.open(image_file)
			
		except Exception as e:
			# create an empty tile, and save it.
			#
			print("[E] Creating empty tile: TileUrl Not found: [%s](%s))" % (url,e))
			image_file = Image.new("RGB", (self.TILE_X_SZ, self.TILE_Y_SZ), "red")
			tileimage = image_file
			cache_tile = False
		
		dirp = os.path.dirname(urlp)
		if not os.path.exists(dirp):
			os.makedirs(dirp)
		if cache_tile:
			tileimage.save(urlp,"PNG")
		return tileimage


	def GetMapTiles(self,tile, zoom, tiles_sz):
		"""
		Get a map from tile (X,Y) with the BB of (X+tiles_sz.width, y+tiles_sz.height)
		returns the image. Form OSM, MapQuest, and so on.
		"""

		# get the tiles sequentially

		mapcanvas = Image.new("RGB",(self.TILE_X_SZ*(tiles_sz.width), self.TILE_Y_SZ*(tiles_sz.height)), "white")

		for y in range(0, tiles_sz.height):
			for x in range(0, tiles_sz.width):

				tileimage = self.TileCache(Point2D(tile[0]+x,tile[1]+y),zoom)

				mapcanvas.paste(tileimage, (self.TILE_X_SZ*x, self.TILE_Y_SZ*y))
				tileimage.close()


		return mapcanvas


	def _offset_meters(self, Origin, Point):
		"""
		calculate the width, height in meters (absolute from Origin to Point)
		requires some functions from geo lib (gpxpy)
		"""

		coef = math.cos(Point.latitude / 180. * math.pi)
		y = Origin.latitude - Point.latitude
		x = (Origin.longitude - Point.longitude) * coef

		y = math.fabs(y)
		x = math.fabs(x)
		return Size(x *geo.ONE_DEGREE, y*geo.ONE_DEGREE)


	def _Point2XY(self,point, origin, zoom, crop_origin=None):
		"""
		if crop_origin, it's used to fix the position of the projection (e.g. when you have
		"finished" the map (aka cropping and repositioning)) and you want to project something
		inside.
		"""

		a,b = self._deg2num(point, zoom)

		a = a - (origin[0])
		b = b - (origin[1])

		if not crop_origin:
			crop_origin = Point2D(0,0)

		i = int(a * self.TILE_X_SZ) - crop_origin.x
		j = int(b * self.TILE_Y_SZ) - crop_origin.y



		return Point2D(i,j)




	def _XY2Point(self, tile, origin, zoom, crop_origin=None):

		# tile is the PIXEL coordinates. We have to add some info about ORIGIN.

		if not crop_origin:
			crop_origin = Point2D(0,0)

		i = ((tile.x + crop_origin.x) / float(self.TILE_X_SZ)) + origin[0]
		j = ((tile.y + crop_origin.y) / float(self.TILE_Y_SZ)) + origin[1]

		a,b = self.num2deg(i, j, zoom)

		return(a,b)

	def ProjectR(self, tile, mapimg):
		"really not used"
		return self.XY2Point(tile, mapimg.origin, mapimg.zoom)

	def Project(self, point, mapimg, color=(200,100,100)):

		i,j = self._Point2XY(point, mapimg.origin, mapimg.zoom, mapimg.crop_origin)
			# sanity check to paint INSIDE the canvas.

		#if i in range(0,(self.TILE_X_SZ)*map.tiles_sz.width) and j in range(0,(self.TILE_Y_SZ)*map.tiles_sz.height):
		if i in range(0,self.img_sz.width) and j in range(0,self.img_sz.height):
			mapimg.imagemap.putpixel((i,j),color)
		else:
			#print "Skipping %s, (%d,%d)" % (point,i,j)
			pass

	def ProjectPoints(self, points, mapimg, color=(200,100,100), width=2):

		rainbow = rainbowvis.Rainbow()
		rainbow.setSpectrum('#0000D0','#00C000', '#FF0000')
		rainbow.setNumberRange(-10, 10);
		
		for i in range(len(points)-1):
			a = points[i]
			b = points[i+1]
			
			distance = gpxpy.geo.distance(a.latitude, a.longitude, a.elevation,
				   						  b.latitude, b.longitude, b.elevation,
				   				   		  haversine=True )
			elevation = b.elevation - a.elevation
			
			if "slope_avg" in dir(a):
				slope = a.slope_avg
			else:
				slope = 0	
					

			ai,aj = self._Point2XY(a, mapimg.origin, mapimg.zoom, mapimg.crop_origin)
			bi,bj = self._Point2XY(b, mapimg.origin, mapimg.zoom, mapimg.crop_origin)

			if ai in range(0,self.img_sz.width) and aj in range(0,self.img_sz.height) and\
			   bi in range(0,self.img_sz.width) and bj in range(0,self.img_sz.height):

				draw = ImageDraw.Draw(mapimg.imagemap)
				draw.line( (ai,aj, bi, bj), fill="#%s" % rainbow.colourAt(slope), width=width)
				del draw
				#mapimg.imagemap.putpixel((i,j),color)


	def ProjectCircle(self, point, mapimg, color=(200,100,100), radius=3, outline=None):


			if not outline:
				outline = color
				
			i,j = self._Point2XY(point, mapimg.origin, mapimg.zoom, mapimg.crop_origin)
			if i in range(0,self.img_sz.width) and j in range(0,self.img_sz.height):

				draw = ImageDraw.Draw(mapimg.imagemap)
				draw.ellipse((i-radius, j-radius, i+radius, j+radius), fill=color, outline=outline)
				del draw

	def ProjectDirection(self, position, mapimg, cw, color=(200,100,100), radius=8, width=2):
			
			DrawCW(mapimg.imagemap, position, radius, cw, color=color, width=width)
			

	def ProjectArrows(self, length, points, mapimg, color=(200,100,100), width=3):

		# calculates how many pixels need in 
		res = mapimg.resolution()  #resmeters/pixel
		#print res, length, len(points)
		dist = (10 * res) + (width*10) 
		
		# use the half point of the track
		d = 0
		j = len(points)/2
		while d < 200.0 and j < len(points):
			d += geo.length_2d([points[j-1], points[j]])
			j += 1
			
		
		d = 0
		k = j
		while d < dist and k < len(points):
			d += geo.length_2d([points[k-1], points[k]])
			k += 1
		
		if j>= len(points): 
			if len(points)-100 > 0: 
				j = len(points)-100
			else:
				j = 0
				
		
		if k>= len(points): k=len(points)-1

		#print len(points),j,k 
		
		a = points[j]
		b = points[k]	

		ai,aj = self._Point2XY(a, mapimg.origin, mapimg.zoom, mapimg.crop_origin)
		bi,bj = self._Point2XY(b, mapimg.origin, mapimg.zoom, mapimg.crop_origin)

		if ai != bi and aj != bj and j != k:

		#print "*" * 10
		#print len(points)
		#print j, k
		#print ai,aj
		#print bi,bj

			if ai in range(0,self.img_sz.width) and aj in range(0,self.img_sz.height) and\
			   bi in range(0,self.img_sz.width) and bj in range(0,self.img_sz.height):
				
				vi,vj = (float(bi-ai), float(bj-aj))
				
				vm = math.sqrt( (vi*vi) + (vj*vj) )
				
				M=width
				vp0i, vp0j = (M*-vj/vm, M*vi/vm)
				vp1i, vp1j = (M*vj/vm, M*-vi/vm)
				# draw here the things.
				
				#vp0 = (-vj+ai, vi+aj)
				#vp1 = (vj+ai, -vi+aj)
				
				vp0 = (vp0i+ai, vp0j+aj)
				vp1 = (vp1i+ai, vp1j+aj)
				
				
				draw = ImageDraw.Draw(mapimg.imagemap)
				#draw.line( (vp0[0],vp0[1], bi, bj), fill=color, width=width)
				#draw.line( (vp1[0],vp1[1], bi, bj), fill=color, width=width)
				coords = [ vp0[0],vp0[1], bi, bj, vp1[0],vp1[1] ]
				draw.polygon(coords, fill=color, outline=(150,0,0))
				del draw
			
		#self.ProjectCircle(points[0], mapimg, color=(10,180,10), radius=4)
		#self.ProjectCircle(points[-1], mapimg, color=(10,10,180), radius=4)
		
		return

# 		i=0
# 		j=i+1
# 		step = 5
# 		arrc = 7
# 		while j < len(points):
# 			a = points[i]
# 			b = points[j]
# 
# 			ai,aj = self._Point2XY(a, mapimg.origin, mapimg.zoom, mapimg.crop_origin)
# 			bi,bj = self._Point2XY(b, mapimg.origin, mapimg.zoom, mapimg.crop_origin)
# 
# 			if ai in range(0,self.img_sz.width) and aj in range(0,self.img_sz.height) and\
# 			   bi in range(0,self.img_sz.width) and bj in range(0,self.img_sz.height):
# 				
# 				vi,vj = (float(bi-ai), float(bj-aj))
# 				
# 				vm = math.sqrt( (vi*vi) + (vj*vj) )
# 				
# 				if vm == 0.0:
# 					j +=step
# 					continue
# 				
# 				if j % arrc != 0:
# 					i = j
# 					j += step
# 					continue
# 				
# 				
# 				M=width
# 				vp0i, vp0j = (M*-vj/vm, M*vi/vm)
# 				vp1i, vp1j = (M*vj/vm, M*-vi/vm)
# 				# draw here the things.
# 				
# 				#vp0 = (-vj+ai, vi+aj)
# 				#vp1 = (vj+ai, -vi+aj)
# 				
# 				vp0 = (vp0i+ai, vp0j+aj)
# 				vp1 = (vp1i+ai, vp1j+aj)
# 				
# 				
# 				draw = ImageDraw.Draw(mapimg.imagemap)
# 				#draw.line( (vp0[0],vp0[1], bi, bj), fill=color, width=width)
# 				#draw.line( (vp1[0],vp1[1], bi, bj), fill=color, width=width)
# 				coords = [ vp0[0],vp0[1], bi, bj, vp1[0],vp1[1] ]
# 				draw.polygon(coords, fill=color, outline=color)
# 				del draw
# 				
# 			i = j
# 			j += step
				

	def _DrawBBox(self, NW,NE,SE,SW, img, origin, zoom):

		nwp = self._Point2XY(NW, origin, zoom)
		nep = self._Point2XY(NE, origin, zoom)
		sep = self._Point2XY(SE, origin, zoom)
		swp = self._Point2XY(SW, origin, zoom)

		draw = ImageDraw.Draw(img)
		draw.line([ nwp, nep, sep, swp, nwp ], (100,100,255), 1)
		del draw

	def _FinishMap(self,mapimg):
		"""
		do everything at last to finish the map and return the image. For now, only crop
		properly
		"""

		#
		# crop.
		#
		# the problem is in the CROP and stablishing the required space

		imgout = Image.new("RGBA",(self.img_sz.width,self.img_sz.height),"white")
		region = mapimg.imagemap.crop((	mapimg.crop_origin.x,
										mapimg.crop_origin.y,
										self.img_sz.width+int(math.fabs(mapimg.crop_origin.x)),
										self.img_sz.height+int(math.fabs(mapimg.crop_origin.y))
									))

		imgout.paste(region,(0,0))
		region.close()
		mapimg.imagemap.close()

		#
		# create the new map, modify the references in order to allow proper projection
		#
		mapimg.imagemap = Image.new("RGBA",(self.img_sz.width,self.img_sz.height),(255,0,0,0))
		mapimg.imagemap.paste(imgout,(0,0))
		imgout.close()
		return(mapimg)

## helper FUNCTIONS

def arc(draw, bbox, start, end, fill, width=1, segments=100):
	"""
	Hack that looks similar to PIL's draw.arc(), but can specify a line width.
	"""
	# radians
	start *= math.pi / 180
	end *= math.pi / 180

	# angle step
	da = (end - start) / segments

	# shift end points with half a segment angle
	start -= da / 2
	end -= da / 2

	# ellips radii
	rx = (bbox[2] - bbox[0]) / 2
	ry = (bbox[3] - bbox[1]) / 2

	# box centre
	cx = bbox[0] + rx
	cy = bbox[1] + ry

	# segment length
	l = (rx+ry) * da / 2.0

	for i in range(segments):

		# angle centre
		a = start + (i+0.5) * da

		# x,y centre
		x = cx + math.cos(a) * rx
		y = cy + math.sin(a) * ry

		# derivatives
		dx = -math.sin(a) * rx / (rx+ry)
		dy = math.cos(a) * ry / (rx+ry)

		draw.line([(x-dx*l,y-dy*l), (x+dx*l, y+dy*l)], fill=fill, width=width)


def DrawCW(img, position, radius, cw=True, color=(255,0,0), width=2):
	
	# position is the CENTER of the circle.
	# calculate bb.
	

	
	
	TW = 8
	TH = 10
	
	cx = position[0]
	cy = position[1]
	
	bb = [ cx-radius, cy-radius, cx+radius, cy+radius ]
	
	draw = ImageDraw.Draw(img)
	if cw:
		#print "CW->"
		arc(draw, bb, 180, -90, color, width)
		arrow = [ (cx-radius-(TW/2), cy-1) , (cx-radius+(TW/2)+1, cy+1) , (cx-radius+2, cy-(TH)) ]
		draw.polygon(arrow, fill=color)
	else:
		#print "AW<-"
		#draw.arc( bb, 0, 270, fill = color )
		arc(draw, bb, 0, 270, color, width)
		arrow = [ (cx+radius-(TW/2)-1, cy+1) , (cx+radius+(TW/2), cy-1) , (cx+radius-2, cy-(TH)) ]
		draw.polygon(arrow, fill=color)
		
	del draw
	
	return img
