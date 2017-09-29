import ROOT
import argparse
from pdb import set_trace
from PlotUtil import *
parser = argparse.ArgumentParser()

parser.add_argument(
    'input',help="""Input hMSSM root file""")
parser.add_argument(
    '--masses',default = "400,450,500,550,600,650,700,750",help="""Masses to map""")
parser.add_argument(
    '--widths',default = "1,2.5,5",help="""Widths to map (in pc)""")    
parser.add_argument(
    '--output', '-o',default = "./mapped_tanb_from_width.txt", help="""Output file name""")
parser.add_argument(
    '--higgs',default = "A", help="""type of massive neutral Higgs boson""")
args = parser.parse_args()

f = ROOT.TFile(args.input)
h = f.Get("width_"+args.higgs)
h2 = f.Get("g_"+args.higgs)
masses = [eval(m) for m in args.masses.split(",")]
widths = [eval(w) for w in args.widths.split(",")]

dat = []
for mass in masses:
 for width in widths:
  _,arr = TH2FixAxisPlot(h,0.1,Xfix=mass)
  width_GeV = mass*width/100.
  try:
   tanb = min(InverseInterpolate(arr,width_GeV))
   dat.append([mass,width_GeV,h2.GetBinContent(h2.FindBin(mass,tanb))]) 
  except:
   set_trace()

out = open(args.output,"w")
out.write("# mass(GeV) width(GeV) tanb\n")
for elem in dat:
 out.write('\t'.join(str(s) for s in elem)+"\n")
