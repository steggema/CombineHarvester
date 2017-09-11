import json
import argparse
import collections
import copy
from os.path import join
from pdb import set_trace

parser = argparse.ArgumentParser()
parser.add_argument(
    'indir', help="""Input directory containing the limit json files""")
parser.add_argument(
    '--higgs',default="A,H", help="""Type of Higgs particles""")
parser.add_argument(
    '--ref', default="1,1p5", help="""Reference points for linear extrapolation""")
parser.add_argument(
    '--make', default="0,0.2,0.5", help="""Points to make""")    
args = parser.parse_args()

def linear_extrapolate(x1,x2,y1,y2,x3):
 return (((x3-x1)*(y2-y1))/(x2-x1)+y1)

widths = args.ref.split(",")
ref = map(eval,args.ref.replace("p",".").split(","))
to_make = map(eval,args.make.split(","))
result = { i:{} for i in to_make}
for h in args.higgs.split(","):
 ref1 = json.load(open(join(args.indir,"limits_{0}_{1}.json".format(h,widths[0]))))
 ref2 = json.load(open(join(args.indir,"limits_{0}_{1}.json".format(h,widths[1]))))
 for make in to_make:
  result[make] = copy.deepcopy(ref1)
 for mh in ref1:
  for exp in ref1[mh]:
   for make in to_make:
    result[make][mh][exp] = linear_extrapolate(ref[0],ref[1],ref1[mh][exp],ref2[mh][exp],make)
 for make in to_make:
  result[make] = collections.OrderedDict(sorted(result[make].items()))
  with open(join(args.indir,"limits_{0}_{1}.json".format(h,str(make).replace(".","p"))), 'w') as fp:
   json.dump(result[make],fp)
