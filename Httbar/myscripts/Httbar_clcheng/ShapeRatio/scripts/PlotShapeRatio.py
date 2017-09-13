import ROOT
import CombineHarvester.CombineTools.plotting as plot
import argparse
from PlotUtil import RatioPlot
from pdb import set_trace

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument(
    'input', nargs='+', help="""Input root files""")
parser.add_argument(
    '--output','-o', default='', help="""Output directory""")
parser.add_argument(
    '--criteria', default="-2p5pc-,-5pc-", help="""Criteria for choosing the histograms to compare""")
parser.add_argument(
    '--padstyle', help="""Style for Pad""")
parser.add_argument(
    '--ratiostyle', help="""Style for Ratio Plot""")

args = parser.parse_args()

def RemoveAllStringInList( s, li):
 result = s
 for item in li:
  result = result.replace(item,'')
 return result 

for file in args.input:
 f = ROOT.TFile(file)
 for category in f.GetListOfKeys():
  tdir = f.Get(category.GetName())
  tdir.cd()
  select = args.criteria.split(',')
  shapes = [i.GetName() for i in tdir.GetListOfKeys() if any(criteria in i.GetName() for criteria in args.criteria.split(','))]
  grouped_shapes = { RemoveAllStringInList(i,select) :[tdir.Get(j) for j in shapes if RemoveAllStringInList(i,select) == RemoveAllStringInList(j,select)]for i in shapes}
  for key,hist in grouped_shapes.iteritems():
   if len(hist)>1:
    RatioPlot(hist,output = args.output+category.GetName()+"_"+key, pad = args.padstyle, ratio = args.ratiostyle)
