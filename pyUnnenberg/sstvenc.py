#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFont, ImageDraw
from pysstv.color import *
import logging

# module-level logger
ml = logging.getLogger('SSTVEnc')
ml.addHandler(logging.NullHandler())

class SSTVEnc(object):
  def __init__(self,**kwargs):    
    try:
      self.font = ImageFont.truetype( "OCRA.ttf", 14 )
      ml.info("Using OCR-A font")
    except:
      self.font = ImageFont.load_default()
      ml.info("Using default font")
      
    self.sample_rate = int(kwargs.get('sample_rate',12000))
      
  def encode(self,wavfilename,sstvmode,imgfilename,text=None):
    img = self.open_image_and_resize(imgfilename,(sstvmode.WIDTH,sstvmode.HEIGHT))
    if text: self.overlay_text(img,text)
    ml.debug("Encoding SSTV ...")
    sstvmode(img, self.sample_rate, 16).write_wav(wavfilename)
    ml.debug("... done (SSTV encoding)")

  def open_image_and_resize(self,filename,size):    
    ml.debug("Opening image and resizing")
    return Image.open(filename).resize(size,Image.ANTIALIAS)

  def overlay_text(self,img,text):
    if ml.isEnabledFor(logging.DEBUG): ml.debug("Overlaying text: {}".format(text))
    width, height = img.size
    draw = ImageDraw.Draw(img)
    draw.rectangle( (0,0,width,16), fill=(255,255,255) )
    draw.text( (1,1), text, font=self.font, fill=(0,0,0) )
    return img

if __name__ == '__main__':
  import pysstv, pysstv.color, pysstv.grayscale
  def build_module_map():
    module_map = {}
    for module in [pysstv.color, pysstv.grayscale]:
        for mode in module.MODES:
            module_map[mode.__name__] = mode
    return module_map
  module_map = build_module_map()
  
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("wav",metavar="WAVFILENAME")
  parser.add_argument("img",metavar="IMGFILENAME")
  parser.add_argument("--overlay-text",default=None,metavar="TEXT")
  parser.add_argument("--mode",default="MartinM1",choices=module_map,metavar="MODE",help="SSTV mode, available: {}".format(", ".join(sorted(module_map.iterkeys()))))
  parser.add_argument("-v","--verbose",type=int,default=3,help="Verbosity level. 0: Critical, 1: error, 2: warning, 3: info, 4: debug")
  args = parser.parse_args()
  
  ll = 10*(4-args.verbose)
  rootlogger = logging.getLogger('')
  rootlogger.setLevel(ll)
  ch = logging.StreamHandler()
  ch.setLevel(ll)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  rootlogger.addHandler(ch)
  
  enc = SSTVEnc()
  enc.encode(args.wav,module_map[args.mode],args.img,args.overlay_text)
