from __future__ import division 
import json
import argparse
import collections
import bisect
import scipy.interpolate
from os.path import join
import re
from pdb import set_trace
  
parser = argparse.ArgumentParser()
parser.add_argument(
    'input',nargs='+',help="""Input json files in width : coupling format obtained from the limit plots of datacards""")
parser.add_argument(
      '--ref',default = "SusHi_mA_out.txt", help="""Reference txt file in mass-tanb-width-xs-coupling format""")
parser.add_argument(
    '--outdir', '-o', default = "./",help="""Output directory""")
parser.add_argument(
    '--wint', default=0.5, help="""Intervals between sucessive widths""")
parser.add_argument(
    '--tanbcut', default=10.,type=float, help="""Cut off for tanb after which the hMSSM data is neglected (prevent multiple intersections)""")
parser.add_argument(
    '--higgs', default="A", help="""Type of heavy neutral Higgs boson (A or H)""")

args = parser.parse_args()

#It is better to use ordered dict if you ever want to reference by index
def dict_ref_by_index(dic, indices):
 return dict_ref_by_index(dic[dic.keys()[indices.pop(0)]],indices) if len(indices) is not 0 else dic

def intersection_4p(p1,p2,p3,p4): #Intersection between the line joining (p1 and p2) and that joining (p3 and p4)
 try:
  m1 = (p2[1] - p1[1])/(p2[0] - p1[0])
  m2 = (p4[1] - p3[1])/(p4[0] - p3[0])
  c1 = p1[1] - m1*p1[0]
  c2 = p3[1] - m2*p3[0]
  x = (c2-c1)/(m1-m2)
  y = (m1*c2 - c1*m2)/(m1-m2)
 except ZeroDivisionError as detail:
  print 'Handling run-time error:',detail
 return x,y

raw_data = { i:{} for i in ['exp+2','exp+1','exp0','exp-1','exp-2']}

for input in args.input:
 mh = re.split("_|\.",input)[-2]
 with open(input) as file:
  data = json.load(file)
  data = dict( [float(a),b] for a,b in data.iteritems())
  data = collections.OrderedDict(sorted(data.items()))
  for category in raw_data:
   if mh not in raw_data[category]:
    raw_data[category][mh] = []
   for width in data:  
    if width!=0 :
     raw_data[category][mh].append([width,data[width][category]])      #Now the dictionary reads: raw_data[category][mA] = [ [width (pc), coupling modifier], ... []] 

wMin = min(dict_ref_by_index(raw_data,[0,0]))[0]
wMax = max(dict_ref_by_index(raw_data,[0,0]))[0]

ref = open(args.ref)
l = [i.split() for i in ref.readlines() if not i.startswith("#")]
ref_data = {}
ref_g_tanb = {}
for mh,tanb,width,xs,g in l:
 if mh not in ref_data:
  ref_data[mh] = []
  ref_g_tanb[mh] = []
 w = (eval(width)/eval(mh))*100 #width in pc
 if ((wMin - args.wint) < w < (wMax + 10)) and (eval(tanb)<args.tanbcut):
  ref_data[mh].append([w,eval(g)]) #Now the dictionary reads: ref_data[mA] = [ [width (pc),coupling], ... []]  *g = cotb for A; sina/sinb for H
  ref_g_tanb[mh].append([eval(g),eval(tanb)]) #For later conversion from g to tanb in mh-tanb plane

for mh in ref_data:
 ref_data[mh].sort()
 ref_g_tanb[mh].sort()
 


result = { str(mh):{} for mh in dict_ref_by_index(raw_data,[0]).keys()}
for category in raw_data:
 for mh in raw_data[category]:
  ref_wMax = max(ref_data[mh])[0]
  if mh not in ref_data:
   print "warning: mass "+str(mh)+" GeV not found in reference data file"
   break 
  if category not in result[mh]:
   result[str(mh)][category] = None
  x,y = zip(*ref_data[mh])    #x must be sorted
  interp = scipy.interpolate.interp1d(x,y)
  try:
   if (float(interp(raw_data[category][mh][0][0])) > raw_data[category][mh][0][1]):  #The coupling modifer is smaller than cotb even for the lowest widths available, no intersection
    continue
  except:
   set_trace()
  for i,pt in enumerate(raw_data[category][mh]):
   if (pt[0] > ref_wMax):
    break
   try:
    if (float(interp(pt[0])) > pt[1]):
     p1,p2 = (raw_data[category][mh][i-1], pt)
     p3,p4 = ([p1[0],float(interp(p1[0]))],[p2[0],float(interp(p2[0]))]) 
     if args.higgs == "A":
      result[str(mh)][category] = 1/intersection_4p(p1,p2,p3,p4)[1]  #1/cotb = tanb
     elif args.higgs == "H":
      g = intersection_4p(p1,p2,p3,p4)[1]
      x,y = zip(*ref_g_tanb[mh])
      interp_tanb = scipy.interpolate.interp1d(x,y)
      result[str(mh)][category] = float(interp_tanb(g))
     break
   except:
    print "Problem two"
    set_trace()

#Hack: if no intersection for exp+2, make it the same as exp+1; exp+1 -> exp0; exp0 -> exp-1
for mh in result:
 for category in ["exp-1","exp0","exp+1","exp+2"]:
  if result[mh][category] == None:
   if category == "exp-1":
    result[mh][category] = result[mh]["exp-2"]  
   elif category == "exp0":
    result[mh][category] = result[mh]["exp-1"]  
   elif category == "exp+1":
    result[mh][category] = result[mh]["exp0"]
   elif category == "exp+2":
    result[mh][category] = result[mh]["exp+1"]

result = collections.OrderedDict(sorted(result.items()))
print result
 
with open(join(args.outdir,"limit_m{0}_tanb.json".format(args.higgs)), 'w') as out:
 json.dump(result,out)  
