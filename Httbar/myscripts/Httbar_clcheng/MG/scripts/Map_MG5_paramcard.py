import argparse
from pdb import set_trace
parser = argparse.ArgumentParser()
parser.add_argument(
    'input', help="""Input file""")
parser.add_argument(
    'output', help="""Output file""")
parser.add_argument(
    '--mass', default = "400")
parser.add_argument(
    '--width', default = "10")
parser.add_argument(
    '--coupling', default = "1")
parser.add_argument(
    '--higgs', default = "A",help="""type of massive scalar higgs boson""")
args = parser.parse_args()
with open(args.input,'r') as f:
 l = f.readlines()

compliment = "H" if args.higgs == "A" else "A"
index = [i for i,s in enumerate(l) if "# g"+args.higgs+"0tt" in s]
try:
 l[index[0]] = l[index[0]].replace(l[index[0]].split()[1],args.coupling)
except:
 set_trace()

index = [i for i,s in enumerate(l) if "# "+args.higgs+"0Width" in s]
try:
 l[index[0]] = l[index[0]].replace(l[index[0]].split()[1],args.width)
except:
 set_trace()
index = [i for i,s in enumerate(l) if "# M"+args.higgs+"0" in s]
l[index[0]] = l[index[0]].replace(l[index[0]].split()[1],args.mass)

index = [i for i,s in enumerate(l) if "# g"+compliment+"0tt" in s]
l[index[0]] = l[index[0]].replace(l[index[0]].split()[1],"0")


with open(args.output, 'w') as file:
    file.writelines( l )
 




