#!/usr/bin/env python
# -*- coding: utf-8 -*-

import alsaaudio, time
from array import array

from itertools import izip_longest

def _chunks(n, iterable, padvalue=None):
    return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)
  
class PlayFloatBuffer:
  CHUNK = 32
  FORMAT = alsaaudio.PCM_FORMAT_FLOAT_LE
  CARD = "default"

  def __init__(self, buffer, framerate, chunk = CHUNK):
    """ Init audio stream """
    self.chunk = chunk
    if (len(buffer) % self.chunk):
      print("Warning: buffer length is not a multiple of {0}, padding with zeros".format(self.chunk))
    self.buffer = map(lambda x: array('f',x).tostring(), _chunks(self.chunk,buffer,0.))
    self.pcm = alsaaudio.PCM(card=self.CARD)
    self.framerate = framerate
    self._setup()
    
  def _setup(self):
    self.pcm.setchannels(1)
    self.pcm.setrate(self.framerate)
    self.pcm.setformat(self.FORMAT)
    self.pcm.setperiodsize(self.chunk)

  def play(self):
    """ Play entire buffer """
    for data in self.buffer:
      while self.pcm.write(data) == 0:
        time.sleep(0)
        
    
if __name__=='__main__':
  from math import sin, pi
  f = 2 * pi / 8000 * 600
  sine = [sin(f*x) for x in xrange(16000)]
  PlayFloatBuffer(sine,8000).play()
