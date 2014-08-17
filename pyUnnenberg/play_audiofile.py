#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import closing
import alsaaudio, wave, time

from itertools import izip_longest

import logging
from logging_helper import *

# module-level logger
ml = logging.getLogger('PAF')
ml.addHandler(logging.NullHandler())
ml = LazyLoggerAdapter(ml)

def _pad(n, iterable, padvalue=None):
  return list(izip_longest(*[iter(iterable)]*n, fillvalue=padvalue))
  
# Copied and adopted from pySSTV.examples.
class PlayAudioFile:
  chunk = 1024

  def __init__(self, file):
    """ Init audio stream """ 
    self.wf = wave.open(file, 'rb')
    self.p = alsaaudio.PCM(card="default")
    self.p.setchannels(self.wf.getnchannels())
    self.p.setrate(self.wf.getframerate())
    # 8bit is unsigned in wav files
    if self.wf.getsampwidth() == 1:
      self.p.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif self.wf.getsampwidth() == 2:
      self.p.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif self.wf.getsampwidth() == 3:
      self.p.setformat(alsaaudio.PCM_FORMAT_S24_LE)
    elif self.wf.getsampwidth() == 4:
      self.p.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
      raise ValueError('Unsupported format')
    
    self.chunk = int(0.1 * self.wf.getframerate())
    self.p.setperiodsize(self.chunk)
    self._cached = None
    
    ml.debug(lambda:"Loaded wav-file, frame rate {}, chunk size {}".format(self.wf.getframerate(),self.chunk))

  def cache(self):
    self._cached = []
    
    data = self.wf.readframes(self.chunk)
    while data:
      self._cached += ["{0:\0<{1}}".format(data,self.chunk)]
      data = self.wf.readframes(self.chunk)
    
  def play(self):
    """ Play entire file """
    start_time = time.time()
    framecnt = 0
    if self._cached is not None:
      for chunk in self._cached:
        while self.p.write(chunk) == 0: time.sleep(0)
      framecnt = len(self._cached)
    else:
      data = self.wf.readframes(self.chunk)
      while data:
        framecnt += 1
        while self.p.write("{0:\0<{1}}".format(data,self.chunk)) == 0:
          time.sleep(0)
        data = self.wf.readframes(self.chunk)
      self.wf.rewind()
    #
    delta = start_time + 0.1 * framecnt - time.time()
    if delta > 0.1:
      time.sleep(delta)

  def close(self):
    """ Graceful shutdown """ 
    self.wf.close()
    
if __name__=='__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("file",nargs="+")
  args = parser.parse_args()
  
  for file in args.file:
    with closing(PlayAudioFile(file)) as a:
      a.play()
