from os import listdir
from os.path import isfile, isdir, join
import argparse
import re
import collections
from pdb import set_trace

parser = argparse.ArgumentParser()
parser.add_argument(
    'path',help="""Path to the MadGraph template file, e.g. PATH/TO/MG5_aMC_v*/bin/template/ """)
parser.add_argument(
    '--param',default = "m*0,g*0tt,*0width",help="""Parameters to be extracted""")
parser.add_argument(
    '--output', '-o', default = "./MG_out.txt",help="""Name of the output file""")
parser.add_argument(
    '--higgs', default = "A",help="""type of the massive neutral higgs particle""")


args = parser.parse_args()

def extract(src, keys , pos = -1):
 result = []
 for key in keys:
  for s in src:
   if key.lower() in s.lower():
    if pos is -1:
     result.append(s)
    else:
     result.append(s.split()[pos])
 return result

param = ["# {0}".format(s.lstrip()) for s in args.param.replace("*",args.higgs).split(",")]

runs = [f for f in listdir(join(args.path,"Events")) if isdir(join(args.path,"Events",f)) and "run_" in f]
files = [join(args.path,"Events",run,f) for run in runs for f in listdir(join(args.path,"Events",run)) if "banner.txt" in f]

dat = {}

for f,run in zip(files,runs):
 dat[run] = extract(open(f).readlines(),param,1)

src = [i for i in open(join(args.path,"crossx.html")).readlines() if "<font face=symbol>&#177;</font>" in i]
for s in src:
 run = re.search('/HTML/(.+?)/results.html"> ',s)
 if run:
  run = run.group(1)
  if run in dat:
   dat[run].append(s.split()[3])  # cross-section
   dat[run].append(s.split()[6].replace("</a>","")) #cross-section uncertainty
  else:
   continue

dat = collections.OrderedDict(sorted(dat.items()))

print '#{0}\t{1}\t{2}\t{3}'.format("run#",'\t'.join(map(str,args.param.replace("*",args.higgs).split(","))),"xs (pb)","uncertainty (pb)")

out = open(args.output,"w")
out.write('#{0}\t{1}\t{2}\t{3}'.format("run#",'\t'.join(map(str,args.param.replace("*",args.higgs).split(","))),"xs (pb)","uncertainty (pb)\n"))
for key in dat:
 s = '{0}\t{1}'.format(str(key),'\t'.join(map(str,dat[key])))
 print s
 out.write(s + "\n")
