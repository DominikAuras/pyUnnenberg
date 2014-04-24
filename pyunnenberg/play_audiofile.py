#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import closing
import alsaaudio, wave, time

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
    
    self.p.setperiodsize(self.chunk)

  def play(self):
    """ Play entire file """
    data = self.wf.readframes(self.chunk)
    while data:
      while self.p.write(data) == 0:
        time.sleep(0)
      data = self.wf.readframes(self.chunk)

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
