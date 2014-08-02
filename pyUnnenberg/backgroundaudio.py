#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['BackgroundAudio']

import alsaaudio, time
from array import array

from itertools import izip_longest

import multiprocessing

def _chunks(n, iterable, padvalue=None):
    return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)
 
class BackgroundAudio:
  """
  Diese Klasse schickt wiederholt den Inhalt des übergebenen Buffers an die Soundkarte.
  Durch start,stop,pause,resume kann die Wiedergabe kontrolliert werden.
  """
  CHUNK = 32
  FORMAT = alsaaudio.PCM_FORMAT_FLOAT_LE
  CARD = "default"

  def __init__(self, buffer, framerate, chunk = CHUNK):
    self.chunk = chunk
    if (len(buffer) % self.chunk):
      print("Warning: buffer length is not a multiple of {0}, padding with zeros".format(self.chunk))
    self.buffer = map(lambda x: array('f',x).tostring(), _chunks(self.chunk,buffer,0.))
    self.framerate = framerate
    
  def _setup(self):
    self.pcm.setchannels(1)
    self.pcm.setrate(self.framerate)
    self.pcm.setformat(self.FORMAT)
    self.pcm.setperiodsize(self.chunk)

  def play(self):
    # Note: multiprocessing spawns a new process, which is a copy of the current
    # process. The only link is via the managed objects (here: the lock).
    self.manager = multiprocessing.Manager()
    self.lock = self.manager.Lock()
    self.ba = multiprocessing.Process(target=self._play, args=(self.lock,))     
    self.ba.start()

  def pause(self):
    self.lock.acquire(True)

  def resume(self):
    self.lock.release()

  def stop(self):
    self.ba.terminate()
    

  def _play(self,lock):
    self.pcm = alsaaudio.PCM(card=self.CARD)
    self._setup()
    while True:
      for data in self.buffer:
        lock.acquire(True)
        while self.pcm.write(data) == 0:
          time.sleep(0)
        lock.release()
        
    
if __name__=='__main__':
  def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:
      a, b = b, a % b
    return a
  
  from math import sin, pi
  f = 2 * pi / 8000 * 600
  chunksize = gcd(1200,8000)
  sine = [sin(f*x) for x in xrange(chunksize)]
  print "Chunksize ist " + str(chunksize)
  print "Das entspricht {} ms".format(chunksize/8000.*1000)
  print "Und genau {} Schwingungen bei 1200 Hz".format(chunksize/8000.*1200)

  ba = BackgroundAudio(sine,8000,chunksize)
  
  import time
  print "Play"
  ba.play()
  time.sleep(5)
  print "Pause"
  ba.pause()
  time.sleep(2)
  print "Resume"
  ba.resume()
  time.sleep(2)
  print "Pause"
  ba.pause()
  time.sleep(2)
  print "Resume"
  ba.resume()
  time.sleep(2)
  print "Stop"
  ba.stop()
  time.sleep(2)
