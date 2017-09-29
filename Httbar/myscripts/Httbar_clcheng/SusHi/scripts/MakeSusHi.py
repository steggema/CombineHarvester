import argparse
import ROOT
from pdb import set_trace
parser = argparse.ArgumentParser()
parser.add_argument(
    'input',help="""Input txt file in mass-tanb-width-xs-g format (i.e. SusHi output)""")
parser.add_argument(
    '--output', '-o', default = "./SusHi_width_xs",help="""Name of the output root file (without extension)""")
parser.add_argument(
    '--higgs', default = "A",help="""Type of Higgs boson (A or H)""")
args = parser.parse_args()


dat = [map(float,i.split()) for i in open(args.input).readlines() if not i.startswith("#")]

f = ROOT.TFile("{0}_{1}.root".format(args.output,args.higgs),"RECREATE")

masses = set([i[0] for i in dat])
tanbs = set([i[1] for i in dat])

h1 = ROOT.TH2F("width_{0}".format(args.higgs),"width_gg{0}".format(args.higgs),len(masses),min(masses),max(masses),len(tanbs),min(tanbs),max(tanbs))
h2 = ROOT.TH2F("xs_{0}".format(args.higgs),"xs_gg{0}".format(args.higgs),len(masses),min(masses),max(masses),len(tanbs),min(tanbs),max(tanbs))
h3 = ROOT.TH2F("g_{0}".format(args.higgs),"g_{0}".format(args.higgs),len(masses),min(masses),max(masses),len(tanbs),min(tanbs),max(tanbs))

for elem in dat:
 h1.Fill(elem[0],elem[1],elem[2])
 h2.Fill(elem[0],elem[1],elem[3])
 h3.Fill(elem[0],elem[1],elem[4])

f.Write()
f.Close()
