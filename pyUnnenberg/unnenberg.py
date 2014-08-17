#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from backgroundaudio import BackgroundAudio
from play_audiofile import PlayAudioFile
from datetime import datetime, timedelta
import calendar
import time
from contextlib import closing
import logging
from vws import vws
from glob import glob
from itertools import cycle
from sstvenc import SSTVEnc
from pysstv.color import MartinM1, PasokonP3
from timeout import *
from cStringIO import StringIO
from math import ceil
import multiprocessing
from logging_helper import *

# module-level logger
ml = logging.getLogger('BEACON')
ml.addHandler(logging.NullHandler())
ml = LazyLoggerAdapter(ml)

def gcd(a, b):
  """Return greatest common divisor using Euclid's Algorithm."""
  while b:
    a, b = b, a % b
  return a

def get_carrier_process(sample_rate=12000): 
  f = 800.
  from math import sin, pi
  chunksize = int(sample_rate / gcd(f,sample_rate))
  if chunksize / float(sample_rate) < 0.1:
    chunksize = int(ceil(0.1 * sample_rate / chunksize) * chunksize)
  sine = [sin(2 * pi / sample_rate * f *float(x)) for x in xrange(chunksize)]
    
  schwingungen = chunksize*f/float(sample_rate) 
  assert( schwingungen - int(schwingungen) == 0 )
  ml.info(lambda:"Carrier chunksize ist " + str(chunksize))
  ml.info(lambda:"Das entspricht {} ms".format(chunksize*1000./sample_rate))
  ml.info(lambda:"Und genau {} Schwingungen bei {} Hz".format(chunksize*f/float(sample_rate),f))

  return BackgroundAudio(sine,sample_rate,chunksize)


def get_nextfullminute(offset=None,min_delay=5):
  r""" Return time: next full minute minus "offset" seconds, 
  but with at least "min_delay" seconds left. """
  tm = datetime.utcnow() + timedelta(minutes=1)  
  tm = tm.replace(second=0,microsecond=0)
  if offset is not None: tm += offset
  if datetime.utcnow() > (tm - timedelta(seconds=min_delay)):     
    tm += timedelta(minutes=1)
  return tm

def ts_nextfullminute(**kwargs):
  r""" Timestamp of next full minute. """
  return calendar.timegm(get_nextfullminute(**kwargs).timetuple())

    
def freq_shift(sstvmode,offset):
  r""" Return a frequency shifted pySSTV mode. """
  class SSTVModeShifted(sstvmode):
    def gen_freq_bits(self):
      for (f,t) in super(SSTVModeShifted,self).gen_freq_bits():
        yield (f + offset, t)
  SSTVModeShifted.__name__ = "SSTVModeShifted_" + sstvmode.__name__
  return SSTVModeShifted


def main(hbq):
  r""" Main Process, sends heartbeats to supervisor process via the heartbeat queue 'hbq'. """
  ml.info(lambda:"Process {}: main() gestartet".format(multiprocessing.current_process().pid))
  
  sample_rate = 12000
  
  static_images = glob("images/*.jpg") + glob("images/*.bmp") + glob("images/*.png")
  ml.info(lambda:"Static images: {}".format(", ".join(static_images)))
  static_images = cycle(static_images)
  
  carrier = get_carrier_process(sample_rate)
  carrier.play()
  
  sstv_mode = cycle(map(lambda x: freq_shift(x,-400),[MartinM1, PasokonP3]))
  pi4 = PlayAudioFile("pi4.wav")
  pi4.cache()
    
  def send_heartbeat():
    hbq.put("alive")
  
  send_heartbeat()
    
  while True:
    for pi4repeat in xrange(10):
      # wait till end of 0.5s before full minute
      nextfullminute = ts_nextfullminute()
      ml.debug(lambda:"Now: {}, wait for: {}".format(time.time(),nextfullminute))
      ml.debug("Warte")
      time.sleep(nextfullminute - time.time() - .5)
      ml.debug("Zurück")
      
      send_heartbeat()
      
      carrier.pause()
      # PI4    
      time.sleep(nextfullminute - time.time())
      ml.debug("Starte PI4")
      pi4.play()
      ml.debug("Ende PI4")
      #
      carrier.resume()
      
      send_heartbeat()
    
    
    try:
      with time_limit(10):
        e = vws()
        imgfilename = e.download_image()
    except:
      if ml.isEnabledFor(logging.DEBUG):
        ml.debug("Verbindung zu VWS fehlgeschlagen")
        import traceback
        for line in traceback.format_exc().splitlines():
          ml.debug(line)
      #
      imgfilename = next(static_images)
      ml.debug(lambda:"Wähle statisches Bild " + imgfilename)
      
    send_heartbeat()
      
    try:
      sm = next(sstv_mode)
      if ml.isEnabledFor(logging.DEBUG):
        ml.debug(lambda:"Kodiere Bild im SSTV-Modus {}".format(sm.__name__))
      with closing(StringIO()) as sstv_file:
        SSTVEnc().encode(sstv_file,sm,imgfilename,"DB0LTG JO31TB " + time.strftime("%d.%m.%y %H:%M"))
        sstv_wf = sstv_file.getvalue()
      
      send_heartbeat()
      
      carrier.pause()
      time.sleep(.5)
      with closing(StringIO(sstv_wf)) as sstv_file:
        with closing(PlayAudioFile(sstv_file)) as a:
          ml.debug("Starte SSTV ...")
          a.play()
          ml.debug("Ende SSTV")
      time.sleep(.5)
      #
      carrier.resume()      
    except:
      ml.warn("SSTV Kodierung fehlgeschlagen")
      if ml.isEnabledFor(logging.DEBUG):
        import traceback
        for line in traceback.format_exc().splitlines():
          ml.debug(line)
          
    send_heartbeat()
      
    
def guarded_main():
  r"""
  We start main() in a separate process. It will send "heartbeats" via an IPC
  channel to us. If we do not receive a heartbeat in a 10 minute interval,
  we kill the main() process, wait 5 seconds, then restart it.
  """
  import Queue
    
  ml.info(lambda:"Process {}: guarded_main() gestartet".format(multiprocessing.current_process().pid))
  
  mgr = multiprocessing.Manager()
  while True:
    q = mgr.Queue()
    p = multiprocessing.Process(target=main, args=(q,))
    
    ml.info("Starte Hauptprozess")
    p.start()
    
    try:
      while True:
        q.get(True,timeout=10*60) # 10 minutes
        ml.info("Heartbeat empfangen")
    except Queue.Empty:
      ml.error("Heartbeat timed out")
      p.terminate()
      time.sleep(5)
      ml.info("Recovery")
  
      
if __name__=='__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("-v","--verbose",type=int,default=3,help="Verbosity level. 0: Critical, 1: error, 2: warning, 3: info, 4: debug")
  parser.add_argument("--syslog",action="store_true",default=False,help="Enable syslog logging")
  args = parser.parse_args()
  
  
  ll = 10*(4-args.verbose)
  rootlogger = logging.getLogger('')
  rootlogger.setLevel(ll)
  ch = logging.StreamHandler()
  ch.setLevel(ll)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  rootlogger.addHandler(ch)
  
  if args.syslog:
    # Add a file /etc/rsyslog.d/unnenberg.conf with one line:
    # local0.* /var/log/unnenberg
    # Then all log messages of level warning or above will be recorded to
    # /var/log/unnenberg.
    from logging.handlers import SysLogHandler
    import socket
    sh = SysLogHandler(address="/dev/log",facility="local0")
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    rootlogger.addHandler(sh)
    ml.warn("Beacon schreibt auf syslog")
    
  
  guarded_main()
