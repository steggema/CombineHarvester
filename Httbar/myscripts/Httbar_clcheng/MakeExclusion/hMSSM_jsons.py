import json
import argparse
import collections
from pdb import set_trace

parser = argparse.ArgumentParser()
parser.add_argument(
    'input', help="""Input txt file in mass-tanb-width-xs-coupling format (SusHi output)""")
parser.add_argument(
    '--outdir','-o', default='./', help="""Output directory""")
parser.add_argument(
    '--minwidth','-min', default=0,type = float, help="""Minimum widths (in pc) available from the data cards""")
parser.add_argument(
    '--maxwidth','-max', default=50,type = float , help="""Maximum widths (in pc) available from the data cards""")   
parser.add_argument(
    '--higgs', default="A", help="""Type of heavy neutral Higgs particle (A or H)""")
 
args = parser.parse_args()


src = [i.split() for  i in open(args.input).readlines() if not i.startswith("#")]

data = {}
wMin = args.minwidth
wMax = args.maxwidth
for mh,tanb,width,xs,g in src:
 if mh not in data:
  data[mh] = []                            #elem[0] = mass ; elem[1] = tanb; elem[2] = width; elem[3] = xs; elem[4] = g 
 w = (eval(width)/eval(mh))*100            #width in pc 
 if wMin < w < wMax:                         #only uses available widths from the data cards
  data[mh].append([eval(g),w])  #data[mass] = [g, width]  

for mh in data:
 data[mh].sort()      #Now data starts from small coupling to large coupling

for mh in data:
 result = {"Inc":[],"Dec":[]}   #Divide the result into a part that is increasing coupling with increasing width (Inc) and a part that is decreasing coupling with increasing width (Dec)
 switch = 0
 wTemp = wMax
 for g,width in data[mh]:
  wPrev = wTemp
  wTemp = width        #Width is decreasing for small coupling but increasing for large coupling
  if wPrev < wTemp:    #Transition from small coupling region to large coupling region
   switch = 1
  if (switch == 0):
   result["Dec"].append([mh,wTemp,g])  # g = 1/tanb for A & sina/sinb for H
  else:
   result["Inc"].append([mh,wTemp,g])
 result["Inc"].sort()
 if len(result["Inc"]) >0 :
  result["Inc"].pop(0) #Discard the transition point
 
 for category in result:
  out = {}
  for mh,width,g in result[category]:
   out[width] = {}
   for limit in ["exp0"]:
    out[width][limit] = g
  out = collections.OrderedDict(sorted(out.items()))
  with open(args.outdir+"hMSSM_"+args.higgs+"_"+mh+"_coupling-width_"+category+".json", 'w') as fp:
   json.dump(out,fp)
