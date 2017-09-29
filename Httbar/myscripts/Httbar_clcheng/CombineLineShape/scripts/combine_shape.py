import ROOT
import argparse
from pdb import set_trace
from os.path import join
import numpy as np
parser = argparse.ArgumentParser()
parser.add_argument(
    'input',help="""Input root file with signal interference and background shapes i.e. template*.root""")
parser.add_argument(
    '--masses',default = "400,550,750",help="""Masses to analyse""")
parser.add_argument(
    '--widths',default = "2.5,5,25,50",help="""Widths to analyse""")   
parser.add_argument(
    '--outdir', '-o',default = "./", help="""Output directory""")
parser.add_argument(
    '--higgs',default = "A,H", help="""type of massive neutral Higgs boson(s) to analyse""")
args = parser.parse_args()


c = ROOT.TCanvas("","",1024,768)
widths = ["-"+i.replace(".","p") + "pc-" for i in args.widths.split(",")]
masses = ["M"+i for i in args.masses.split(",")]
higgses = ["gg"+i for i in args.higgs.split(",")]

f = ROOT.TFile(args.input,"READ")
newf = ROOT.TFile(join(args.outdir,"combined_shape.root"),"RECREATE")

for category in [i.GetName() for i in f.GetListOfKeys()]:
 tdir = f.Get(category)
 for higgs in higgses:
  for mass in masses:
   for width in widths:
    shape = tdir.Get("{0}_pos-sgn{1}{2}".format(higgs,width,mass)).Clone("combine")
    shape.Add(tdir.Get("{0}_neg-int{1}{2}".format(higgs,width,mass)),-1)
    shape.Add(tdir.Get("{0}_pos-int{1}{2}".format(higgs,width,mass)))
    shape.GetXaxis().SetTitle("m_{t#bar{t}}#otimes cos#theta_{t_{lep}}")
    shape.GetYaxis().SetTitle("Event")
    shape.SetTitle("{0} {1} GeV {2} width".format(higgs,mass,width.replace("-","")))
    shape.SetStats(0)
    shape.SetFillColorAlpha(ROOT.kRed-7,0.5)
    shape.Draw("HIST")
    shape.Write()
    c.SaveAs(join(out,"{0}{1}{2}_combined.pdf".format(higgs,width,mass)))
    c.Clear()
f.Close()
