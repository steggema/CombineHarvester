#!/usr/bin/env python
from argparse import ArgumentParser
import numpy as np
parser = ArgumentParser()
parser.add_argument('input',nargs='+', help = "Input templates for scaling")
parser.add_argument(
    '--factor',default = 1000./35.9,type = float,help="""Factor by which all shapes are scaled (sgn, int, bkg)""")  
args = parser.parse_args()

import ROOT
import shutil
from pdb import set_trace

factor = args.factor

for files in args.input:
 print "Loading file {0} Scaling factor: {1}".format(files,args.factor)
 f = files.replace(".root","_all_scaled.root")
 shutil.copyfile(files, f)
 f = ROOT.TFile(f,"UPDATE")
 for category in [i.GetName() for i in f.GetListOfKeys()]:
  tdir = f.Get(category)
  tdir.cd()
  shapes = [i.GetName() for i in tdir.GetListOfKeys()]
  n = len(shapes)
  counter = 0
  print "Doing category: {0} # of shapes {1}".format(category,n)
  for shape in shapes:
   h = tdir.Get(shape)
   h.Scale(factor)
   h.Write(shape,ROOT.TObject.kOverwrite)
   counter += 1
   print "Doing shapes: {0}/{1}".format(counter,n)
 f.Close()   
