#!/usr/bin/env python

def main():
  import argparse

  parser = argparse.ArgumentParser(description="Konvertiere Text zu Morsecode.",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--wpm",type=int,default=12,help="Morse code rate in words per minute")
  parser.add_argument("--fpwm",type=int,default=12,help="Farnsworth rate in words per minute")
  parser.add_argument("-o","--output",type=str,default="morse.wav",help="Output file")
  parser.add_argument("-f","--freq",type=float,default=1200,help="Frequenz in Hertz")
  parser.add_argument("-s","--sample-rate",type=int,default=8000,help="Samplerate in Hertz")
  parser.add_argument("text",type=str, nargs="+",help="Input text")
  args = parser.parse_args()

  morsetext = ' '.join(args.text)
  print("Schreibe '{0}' als Morsecode in {1}".format(morsetext,args.output))

  import ditndah
  m = ditndah.MorseGen(format=ditndah.FORMAT_S16LE,\
                       pitch=args.freq,\
                       sampleRate=args.sample_rate,\
                       wpm=args.wpm,fwpm=args.fpwm)
  m.textToWaveFile(morsetext, args.output)

if __name__ == '__main__':
  main()
