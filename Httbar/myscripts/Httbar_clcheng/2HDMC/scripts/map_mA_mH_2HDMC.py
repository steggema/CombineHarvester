import math
import subprocess
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    'input', default="./CalcHMSSM", help="""Path to the 2HDMC Calculator""")
parser.add_argument(
    '--mass', '-m', default="400-750:50", help="""Input pseudoscalar mass (mA). Example 1. from 400 to 750 GeV with 50 GeV interval: 400-750:50 ; Example 2. individual masses: 400,450,500,550,600,650,700,750""")
parser.add_argument(
    '--tanb', default="0.4-50:0.1", help="""Input tanb. Example 1. from 0.6 to 50 with 0.1 interval: 0.6-50:0.1 ; Example 2. individual values: 0.8,1,1.2""")
parser.add_argument(
    '--precision', '-p', default=0.1 , type=float , help="""Desired precision of mH""")
parser.add_argument(
    '--mrange', '-r', default=200 , type=float , help="""Range of mass allowed to span across mA in obtaining mH. E.g. 200 means +- 200 GeV""")
parser.add_argument(
    '--output', '-o', default="./mA_mH_mapped", help="""Name of the output file without extension""")
args = parser.parse_args()


def interp(src):
    if ":" in src:
        temp = [s.split("-") for s in src.split(":")]
        result = np.arange(eval(temp[0][0]), eval(
            temp[0][1])+eval(temp[1][0]), eval(temp[1][0]))
    else:
        result = [eval(s) for s in src.split(",")]
    return result

mh = "125"
Calc = args.input
masses = interp(args.mass)
tanbs = interp(args.tanb)
dm = args.mrange
precision = args.precision
output = open(args.output+".txt", "w")
output.write("#tanb : mH : mA : sina : sinb : g\n")


for mass in masses:
    for tanb in tanbs:
        mA = mass
        print "Calculating mH for mA = {0}, tanb = {1}".format(mA, tanb)
        f = open("result", "w")
        subprocess.call([Calc, mh, str(mA), str(tanb), "test"], stdout=f)
        f.close()
        l = open("result").readlines()
        try:
            mH = eval([i.split()[1] for i in l if "m_H:" in i][0])
            print "mH = {0}".format(mH)
        except:
            print "Exception detected at mass of {0}".format(str(mH))
            continue
    
        sin_b_a = eval([i.split()[1]
                        for i in l if "sin(b-a):" in i][0])
        beta = math.atan(tanb)
        b_a = math.asin(sin_b_a)
        alpha = beta-b_a
        sina = math.sin(alpha)
        sinb = math.sin(beta)
        out = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(str(tanb), str(
            mH), str(mA), str(sina), str(sinb), str(sina/sinb))
        output.write(out+"\n")
        print "Result for tanb : mH : mA : sina : sinb : g"
        print out

output.close()
