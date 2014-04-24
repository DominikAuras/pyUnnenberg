#!/usr/bin/env python
# -*- coding: utf-8 -*-

import alsaaudio, time
from array import array

from itertools import izip_longest

def _chunks(n, iterable, padvalue=None):
    return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)
  
class PlayFloatBuffer:
  CHUNK = 1024
  FORMAT = alsaaudio.PCM_FORMAT_FLOAT_LE
  CARD = "default"

  def __init__(self, buffer, framerate):
    """ Init audio stream """
    self.buffer = map(lambda x: array('f',x).tostring(), _chunks(self.CHUNK,buffer,0.))
    self.p = alsaaudio.PCM(card=self.CARD)
    self.p.setchannels(1)
    self.p.setrate(framerate)
    self.p.setformat(self.FORMAT)
    self.p.setperiodsize(self.CHUNK)
    self._stop = False

  def play(self):
    """ Play entire buffer """
    for data in self.buffer:
      while self.p.write(data) == 0:
        time.sleep(0)
    
if __name__=='__main__':
  from math import sin, pi
  f = 2 * pi / 8000 * 600
  sine = [sin(f*x) for x in xrange(16000)]
  PlayFloatBuffer(sine,8000).play()
