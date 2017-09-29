import argparse
from pdb import set_trace
import math
parser = argparse.ArgumentParser()
parser.add_argument(
    'input', help="""Input 2HDMC """)
parser.add_argument(
    'mapoutput', help="""Output file to be mapped""")
parser.add_argument(
    '--model', default = "2",help="""model: 0 = SM, 1 = MSSM, 2 = 2HDM, 3 = NMSSM; default = 2""")
parser.add_argument(
    '--gghlo', default = "2",help="""0 = LO 1 = NLO 2 = NNLO 3 = NNNLO; default = 2""")
parser.add_argument(
    '--bbhlo', default = "2",help="""0 = LO 1 = NLO 2 = NNLO 3 = NNNLO; default = 2""")
parser.add_argument(
    '--higgs', default = "21",help="""Higgs type: 11 = h, 12 = H, 21 = A""")
parser.add_argument(
    '--gghscale','-s', default = "0.5",help="""Renormalization and factorization scale for muR | muF  /mh""")
args = parser.parse_args()

with open(args.input,'r') as f:
 l = f.readlines()
with open(args.mapoutput,'r') as f:
 m = f.readlines()



def map_line(inputlist, matchstr, strpos, newvalue):
 index = [i for i,s in enumerate(inputlist) if matchstr in s]
 if len(index)>0:
  inputlist[index[0]] = m[index[0]].replace(m[index[0]].split()[strpos],str(newvalue))
 

to_map = ["tan(beta)","lambda_1","lambda_2","lambda_3","lambda_4","lambda_5","lambda_6","lambda_7","m_h","m_H","m_A","m_H+","sin(b-a)","cos(b-a)","Z4","Z5","Z7"]
be_map = ["# tan(beta)","# lambda1","# lambda2","# lambda3","# lambda4","# lambda5","# lambda6","# lambda7","# mh","# mH","# mA","# mC","# sin(beta-alpha)","# cos(beta-alpha)","Z4","Z5","Z7"]


for param_to_map, param_be_map in zip(to_map, be_map):
 try:
  value = [s.split()[1] for s in l if param_to_map in s][0]
 except:
  set_trace()
 index = [i for i,s in enumerate(m) if param_be_map in s]
 if len(index)>0:
  m[index[0]] = m[index[0]].replace(m[index[0]].split()[1],value)

m_12 = str(math.sqrt(float([s.split()[1] for s in l if "m12^2" in s][0])))
index = [i for i,s in enumerate(m) if "# m12" in s]
if len(index)>0:
 m[index[0]] = m[index[0]].replace(m[index[0]].split()[1],m_12)
 
map_line(m,"# order ggh:",1,args.gghlo)
map_line(m,"# order bbh:",1,args.bbhlo)
map_line(m,"# model: 0 = SM, 1 = MSSM, 2 = 2HDM, 3 = NMSSM",1,args.model)
map_line(m,"# 11 = h, 12 = H, 21 = A",1,args.higgs)
map_line(m,"# renormalization scale muR/mh",1,args.gghscale)
map_line(m,"# factorization scale muF/mh",1,args.gghscale)

#map_line(m,"# mH",1,1000)
#map_line(m,"# m12",1,250)

with open(args.mapoutput, 'w') as file:
    file.writelines( m )
file.close() 




