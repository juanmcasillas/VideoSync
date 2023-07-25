import math
import random
from PIL import Image


# A map of rgb points in your distribution
# [distance, (r, g, b)]
# distance is percentage from left edge


#for x in range(im.size[0]):
#    r, g, b = pixel(x, width=3000, map=heatmap)
#    r, g, b = [int(256*v) for v in (r, g, b)]
#    for y in range(im.size[1]):
#        ld[x, y] = r, g, b

class GradientMap:
    def __init__(self):
        # from white to red
        self.heatmap = [
        [0.0, (.9, .9, .9)],
        #[0.0, (.7, .7, 0.7)],
        [0.20, (.4, .1, .1)],
        [0.40, (0.4, .1, .1)],
        [0.60, (.4, 0, 0)],
        [0.80, (.2, 0, 0)],
        [0.90, (0.1, 0, 0)],
        [1.00, (0.05, 0, 0)],
    ]

    def gaussian(self, x, a, b, c, d=0):
        return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

    def pixel(self,x, width=100, map=[], spread=1):
        width = float(width)
        r = sum([self.gaussian(x, p[1][0], p[0] * width, width/(spread*len(map))) for p in map])
        g = sum([self.gaussian(x, p[1][1], p[0] * width, width/(spread*len(map))) for p in map])
        b = sum([self.gaussian(x, p[1][2], p[0] * width, width/(spread*len(map))) for p in map])
        return min(1.0, r), min(1.0, g), min(1.0, b)

    def mapval(self, value, rmin=100, rmax=1000):
        r, g, b = self.pixel(value, width=rmax, map=self.heatmap)
        #r, g, b = [int(256*v) for v in (r, g, b)]
        r, g, b = [int(255*v) for v in (r, g, b)]
        return r,g,b

if __name__ == "__main__":

    gmap = GradientMap()

    random.seed()

    im = Image.new('RGB', (3000, 2000))
    ld = im.load()

    for x in range(im.size[0]):
        r,g,b = gmap.mapval(random.randrange(0,1000))
        for y in range(im.size[1]):
            ld[x,y] = r,g,b


    im.save('grad.png')