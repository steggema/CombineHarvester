from os import listdir
from os.path import isfile, isdir, join
import argparse
from pdb import set_trace
import math  
parser = argparse.ArgumentParser()
parser.add_argument(
    'dir',help="""Input directory containing the SusHi output""")
parser.add_argument(
    '--param', default = "m*,tan(beta),* width in GeV,ggh XS in pb,sin(beta-alpha)",help="""Parameters to be extracted""")
parser.add_argument(
    '--show',action='store_true' ,help="""Display results""")
parser.add_argument(
    '--output', '-o', default = "./SusHi_out.txt",help="""Name of the output file""")
parser.add_argument(
    '--higgs', default = "A",help="""type of massive neutral Higgs boson""")
args = parser.parse_args()

def extract(src, keys , pos = -1):
 result = []
 for key in keys:
  for s in src:
   if key in s:
    if pos is -1:
     result.append(s)
    else:
     result.append(s.split()[pos])
 return result

param = ["# {0}".format(s.replace("*",args.higgs).lstrip()) for s in args.param.split(",")]

files = [join(args.dir,f) for f in listdir(args.dir)]
files = [f for f in files if "murdep" not in f if isfile(f)]

dat = []

#set_trace()
for f in files:
 dat.append(map(eval,extract(open(f).readlines(),param,1)))
 try:
  dat[-1][0] = int(5*round((dat[-1][0])/5))   #Round the mass to nearest 5
 except:
  set_trace()
 if args.higgs=="A":  #g_A = 1/tanb
  dat[-1][4] = 1/dat[-1][1]
 elif args.higgs=="H": #g_H = sina/sinb
  beta = math.atan(dat[-1][1])
  beta_alpha = math.asin(dat[-1][4])
  alpha = beta - beta_alpha
  sina = math.sin(alpha)
  sinb = math.sin(beta)
  dat[-1][4] = sina/sinb
 else:
  raise "ERROR: Wrong input of Higgs type (either H or A)"
dat = [i for i in dat if len(i) > 0]
dat.sort()

out = open(args.output,"w")

out.write('# {0}\n'.format(args.param.replace("*",args.higgs).replace("sin(beta-alpha)","g").replace(",","\t")))
for elem in dat:
 s = '{0}'.format('\t'.join(map(str,elem)))
 if args.show:
  print s
 out.write(s + "\n")
