import ROOT
import argparse
from pdb import set_trace
import numpy as np
parser = argparse.ArgumentParser()
parser.add_argument(
    'input',help="""Input root file with signal interference and background shapes""")
parser.add_argument(
    '--masses',default = "400,450,500,550,600,650,700,750",help="""Masses to analyse""")
parser.add_argument(
    '--widths',default = "2.5:5",help="""Widths to compare""")   
parser.add_argument(
    '--type',default = "sgn,-int-",help="""Widths to compare""")   
parser.add_argument(
    '--outdir', '-o',default = "./", help="""Output directory""")
parser.add_argument(
    '--higgs',default = "A,H", help="""type of massive neutral Higgs boson(s) to analyse""")
args = parser.parse_args()

def splittokeys(src, keys):
 result = {}
 for key in keys:
  result[key] = [i for i in src if key in i]
 return result

out_txt = open(args.outdir + "shape_ratio.txt","w")
#out_root = open(args.outdir + "shape_ratio.root")

result = {}
widths = ["-"+i.replace(".","p") + "pc-" for i in args.widths.split(":")]
if len(widths)!=2 :
 raise "ERROR: you should only compare two widths"
masses = ["M"+i for i in args.masses.split(",")]
higgses = ["gg"+i for i in args.higgs.split(",")]
types = args.type.split(",")

f = ROOT.TFile(args.input,"READ")
newf = ROOT.TFile(args.outdir+"shape_ratio.root","RECREATE")
out_txt.write("#category\thiggs\tprocess\tmass\tmean\tstandard deviation\n") 

for category in [i.GetName() for i in f.GetListOfKeys()]:
 result[category] = {}
 tdir = f.Get(category)
 shapes = [i.GetName() for i in tdir.GetListOfKeys() if (widths[0] in i.GetName()) or (widths[1] in i.GetName())]
 shapes = splittokeys(shapes,higgses)
 for higgs in higgses:
  shapes[higgs] = splittokeys(shapes[higgs],types)
  if higgs not in result[category]:
   result[category][higgs] = {}
  for _type in types:
   shapes[higgs][_type] = splittokeys(shapes[higgs][_type],masses)
   result[category][higgs][_type] = {}
   if _type not in result[category][higgs]:
    result[category][higgs][_type] = {}
   for mass in masses:
    shapes[higgs][_type][mass] = splittokeys(shapes[higgs][_type][mass],widths)
    for width in shapes[higgs][_type][mass]:
     shapes[higgs][_type][mass][width].sort()
    ratio = [] 
    for i,j in zip(shapes[higgs][_type][mass][widths[0]],shapes[higgs][_type][mass][widths[1]]):
     ratio.append(tdir.Get(i).GetMaximum()/tdir.Get(j).GetMaximum())
    #set_trace()
    h = ROOT.TH1F("{0}_{1}_{2}_{3}".format(category,higgs,_type,mass),"{0}_{1}_{2}_{3}".format(category,higgs,_type.replace("-",""),mass),10,min(ratio),max(ratio))
    result[category][higgs][_type][mass] = {"mean":np.mean(ratio),"std":np.std(ratio)}
    for elem in ratio:
     h.Fill(result[category][higgs][_type][mass]["mean"])
    h.Write()
    out_txt.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(category,higgs,_type.replace("-",""),mass,result[category][higgs][_type][mass]["mean"],result[category][higgs][_type][mass]["std"]))    
f.Close()
newf.Write()
newf.Close()
f = ROOT.TFile(args.outdir+"shape_ratio.root","RECREATE")

 
 
