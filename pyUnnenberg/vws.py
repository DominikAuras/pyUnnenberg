#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, logging

# module-level logger
ml = logging.getLogger('VWS')
ml.addHandler(logging.NullHandler())

class vws(object):
  def __init__(self,**kwargs):
    """ 
      keywords arguments
        vws, img_relpath, resolution, channel, dont_initialize
    """
    self.vws = kwargs.get('vws',"http://cameraserver")
    self.img_relpath = kwargs.get('img_relpath',"/Jpeg/CamImg.jpg")
    # ResType: 0: 176x144, 1: 352x288, 2: 320x240, 3: 640x80
    self.vws_res = "/ChangeResolution.cgi?ResType=" + str(kwargs.get('resolution',3))
    self.vws_cr = "/ChangeCompressRatio.cgi?Ratio=1" # High
    self.vws_chn = "/SetChannel.cgi?Channel="
    
    self.initialized = False
    if not kwargs.get('dont_initialize',False):
      self.setup()
    if self.initialized:
     self.set_channel(kwargs.get('channel',0))

  def setup(self):
    ml.info("Richte VWS ein")
    try:
      self._urlretrieve(self.vws + self.vws_res)
      self._urlretrieve(self.vws + self.vws_cr)      
      self.initialized = True
    except:
      ml.warn("Konnte VWS nicht initialisieren")
      import traceback
      for line in traceback.format_exc().splitlines():
        ml.debug(line)
    
  def download_image(self,filename = "tmp.jpg"):
    if not self.initialized: raise RuntimeError
    http_path = self.vws + self.img_relpath
    ml.debug("Lade {0} nach {1} herunter".format(http_path,filename))
    (fname,headers) = self._urlretrieve(http_path, filename)
    ml.debug("Ladevorgang erfolgreich: {0}".format(fname))
    return fname

  def set_channel(self,channel):
    ml.info("Wechsle VWS Kanal zu {0}".format(channel))
    self._urlretrieve(self.vws + self.vws_chn + str(channel))
    
  def _urlretrieve(self,url):
    ml.debug("URL Retrieve: \"{}\"".format(url))
    return urllib.urlretrieve(url)


if __name__=='__main__':
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("-v","--verbose",type=int,default=1,help="Verbosity level. 0: Critical, 1: error, 2: warning, 3: info, 4: debug")
  args = parser.parse_args()
  
  ll = 10*(4-args.verbose)
  rootlogger = logging.getLogger('')
  rootlogger.setLevel(ll)
  ch = logging.StreamHandler()
  ch.setLevel(ll)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  rootlogger.addHandler(ch)
  
  e = vws()
  if not e.initialized:
    ml.info("Abbruch des Tests")
    raise SystemExit
  for channel in xrange(0,4):
    e.set_channel(channel)
    e.download_image("chan{0}.jpg".format(channel))
