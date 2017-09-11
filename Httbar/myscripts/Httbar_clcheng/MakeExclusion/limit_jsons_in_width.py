#LAST EDITED: 27/8/2017
#COMPLETE VERSION
import json
import ROOT
import argparse
import collections
from os.path import join
from pdb import set_trace
parser = argparse.ArgumentParser()

parser.add_argument(
    'inpath', default = "./",help="""Path to input json files""")
parser.add_argument(
    '--outpath', '-o',default = "./", help="""Path to output files""")
parser.add_argument(
    '--mint', default = 50, type = int,  help="""Mass bin width in GeV""") 
parser.add_argument(
    '--wint', default = 0.5, type = float, help="""Width bin width in pc""")     
args = parser.parse_args()

ROOT.gROOT.SetBatch(True)
c = ROOT.TCanvas(args.outpath,args.outpath)

for higgs in ["A","H"]:
 f = ROOT.TFile(higgs+"limit_M_width.root","RECREATE")	
 jsons = [i.GetName() for i in ROOT.TSystemDirectory(args.inpath, args.inpath).GetListOfFiles()]
 jsons = [i for i in jsons if "limits_{0}_".format(higgs) in i if "M" not in i]
 if len(jsons) == 0:
  print 'WARNING: No limit jsons file found for gg{0} process'.format(higgs)
  continue
 limits = {}
 for js in jsons:
  with open(join(args.inpath,js)) as data_file:
   data = json.load(data_file)
   for mh in data:
    if eval(mh) not in limits:
     limits[eval(mh)] = {}      #Convert str key to num key for ordering dictionary
    width = eval(js.replace('limits_{0}_'.format(higgs),'').replace('.json','').replace('p','.'))
    limits[eval(mh)][width] = {}
    for exp in data[mh]:
     limits[eval(mh)][width][exp] = data[mh][exp]
 limits = collections.OrderedDict(sorted(limits.items()))
 for mh in limits:
  limits[mh] = collections.OrderedDict(sorted(limits[mh].items()))
 #Store expected limits in a root file
 xMax = limits.keys()[-1] + args.mint
 xMin = limits.keys()[0] - args.mint
 yMax = limits[limits.keys()[0]].keys()[-1] + args.wint
 yMin = limits[limits.keys()[0]].keys()[0] - args.wint
 for exp in ["exp-2","exp-1","exp0","exp+1","exp+2"]:
  h = ROOT.TH2F("gg{0}_{1}".format(higgs,exp),"",int((xMax-xMin)/args.mint),xMin,xMax,int((yMax-yMin)/args.wint),yMin,yMax)
  for mh in limits:
   for width in limits[mh]:
    try:
     h.Fill(mh,width,limits[mh][width][exp])
    except:
     set_trace()
  h.SetStats(0)
  h.GetXaxis().SetTitle("M_{0}".format(higgs))
  h.GetYaxis().SetTitle("width")
  h.GetZaxis().SetTitle("Coupling Modifier")
  h.GetXaxis().SetTitleOffset(2)
  h.GetYaxis().SetTitleOffset(2)
 f.Write()

 #Save expected limits into jsons file
 for mh in limits:
  js = {}
  for width in limits[mh]:
   js[str(width).replace("'","\"")] = {}  #Single quote may not work in jsons file, convert ' to "
   for exp in limits[mh][width]:
    js[str(width).replace("'","\"")][exp.replace("'","\"")] = limits[mh][width][exp]
  with open(join(args.inpath,"width_{0}_{1}.json".format(higgs,str(mh).replace(".0",""))), 'w') as fp:
   json.dump(js, fp)
