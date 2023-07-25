import pygame

# EMBFADE - does a 3d emboss-like effect
def embfade(textstring, textsize, amount, displaysize, trgb = [255, 255, 255]):
  displaysurface = pygame.Surface(displaysize)
  font = pygame.font.Font(None, textsize)
  for i in range(amount):
    text = font.render(textstring, True, [c / (i + 1) for c in trgb])
    displaysurface.blit(text, [i, i])
  return displaysurface

# Do a simple drop-shadow on text, with a darker color offset by a certain
# number of pixels.
def shadow(text, font, color, offset = 1, color2 = None):
  # Allow integers or fonts for 'font'.
  if isinstance(font, int): font = pygame.font.Font(None, font)
  if color2 == None: color2 = [c / 9 for c in color]


  t1 = font.render(text, True, color)
  t2 = font.render(text, True, color2)


  s = pygame.Surface([i + offset for i in t1.get_size()], pygame.SRCALPHA, t1 )

  s.blit(t2, [offset, offset])
  s.blit(t1, [0, 0])

  return s

def crappyshadow(text, font, color, offset = 1, color2 = None, alpha=128):
  # Allow integers or fonts for 'font'.
  if isinstance(font, int): font = pygame.font.Font(None, font)
  if color2 == None: color2 = [c / 9 for c in color]

  ckey= (178,218,222, 40)

  t1 = font.render(text, True, color, ckey)
  t1=t1.convert()
  t1.set_colorkey(ckey)
  t2 = font.render(text, True, color2, ckey)
  t2=t2.convert()
  t1.set_colorkey(ckey)

  s = pygame.Surface([i + offset for i in t1.get_size()], pygame.SRCALPHA, t1 )


  s.blit(t2, [offset, offset])
  s.blit(t1, [0, 0])

  #s = s.convert()
  s=s.convert()
  s.set_alpha(alpha)
  s.set_colorkey(ckey)
  return s


# SHADEFADE - does a 3d dropshadow-like effect
def shadefade(textstring, textsize, amount, displaysize, trgb=(255,255,255)):
  displaysurface = pygame.Surface(displaysize, pygame.SRCALPHA, 32)
  font = pygame.font.Font(None, textsize)
  for i in range(amount - 1, 0, -1):
    text = font.render(textstring, True, [c / i for c in trgb])
    displaysurface.blit(text, [i, i])
  return displaysurface