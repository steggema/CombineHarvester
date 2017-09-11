#!/usr/bin/env python
from argparse import ArgumentParser
import numpy as np
parser = ArgumentParser()
parser.add_argument('input',nargs='+', help = "Input templates for scaling")
parser.add_argument(
    '--sgnfactor',default = "400:2.84E+00,450:2.47E+00,500:2.27E+00,550:2.13E+00,600:2.03E+00,650:1.95E+00,700:1.89E+00,750:1.83E+00",help="""Factor by which all the signal shapes scales (mass:scale)""")  
parser.add_argument(
    '--intfactor',default = "400:2.243323698,450:2.089229843,500:2.002623867,550:1.942805476,600:1.895686751,650:1.856694249,700:1.829439044,750:1.801913174",help="""Factor by which all the interference shapes scales (mass:scale)""") 
args = parser.parse_args()

import ROOT
import shutil
import re
from pdb import set_trace

factor = {"sgn": {} , "int": {}}
for f in args.sgnfactor.split(","):
 factor["sgn"][f.split(":")[0]] = eval(f.split(":")[1])
for f in args.intfactor.split(","):
 factor["int"][f.split(":")[0]] = eval(f.split(":")[1]) 
 

for files in args.input:
 print "Loading file {0}".format(files)
 f = files.replace(".root","_k_factor_scaled.root")
 shutil.copyfile(files, f)
 f = ROOT.TFile(f,"UPDATE")
 for category in [i.GetName() for i in f.GetListOfKeys()]:
  tdir = f.Get(category)
  tdir.cd()
  shapes = [i.GetName() for i in tdir.GetListOfKeys()]
  shapes = [i for i in shapes if (i.startswith('ggA_') or i.startswith('ggH_'))]
  shapes = { "sgn" : [i for i in shapes if '_pos-sgn' in i], "int" : [i for i in shapes if '-int-' in i]}
  n = { "sgn" : len(shapes["sgn"]), "int" : len(shapes["int"])}
  print "Doing category: {0} # of sgn shapes: {1} # of int shapes: {2}".format(category, n["sgn"], n["int"])
  for _type in shapes:
   counter = 0
   for shape in shapes[_type]:
    mass = shape.split("-")[3].split("_")[0].replace("M","")
    h = tdir.Get(shape)
    try:
     h.Scale(factor[_type][mass])
    except:
     set_trace()
    h.Write(shape,ROOT.TObject.kOverwrite) #maybe safer to use ROOT.TObject.kWriteDelete but is slower
    counter += 1
    print "Doing {0} shapes: {1}/{2}".format(_type,counter,n[_type])
 f.Close()
