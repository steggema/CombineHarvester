#!/usr/bin/env python

''' Runs 2HDMC in hMSSM mode to produce a mapping mA, tan(beta) -> mH and other
parameters.
'''

import math
import pickle
import subprocess
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    'thdmc_command', default="./CalcHMSSM", help="""Path to the 2HDMC Calculator""")
parser.add_argument(
    'sushi_command', default="./sushi.2HDMC ", help="""Path to the SusHi programme""")
parser.add_argument(
    '--mass', '-m', default="400-750:50", help="""Input pseudoscalar mass (mA). Example 1. from 400 to 750 GeV with 50 GeV interval: 400-750:50 ; Example 2. individual masses: 400,450,500,550,600,650,700,750""")
parser.add_argument(
    '--tanb', default="0.4-50:0.1", help="""Input tanb. Example 1. from 0.6 to 50 with 0.1 interval: 0.6-50:0.1 ; Example 2. individual values: 0.8,1,1.2""")
parser.add_argument(
    '--sushi_card', default="2HDMC_physicalbasis.in", help="""SusHi template parameter card""")
parser.add_argument(
    '--model', default = "2",help="""model: 0 = SM, 1 = MSSM, 2 = 2HDM, 3 = NMSSM; default = 2""")
parser.add_argument(
    '--gghlo', default = "2",help="""0 = LO 1 = NLO 2 = NNLO 3 = NNNLO; default = 2""")
parser.add_argument(
    '--gghscale','-s', default = "0.5",help="""Renormalization and factorization scale for muR | muF  /mh""")
parser.add_argument(
    '--output', '-o', default="./the_output_OMG", help="""Name of the output file without extension""")
args = parser.parse_args()


def interp(src):
    if ":" in src:
        temp = [s.split("-") for s in src.split(":")]
        result = np.arange(eval(temp[0][0]), eval(
            temp[0][1])+eval(temp[1][0]), eval(temp[1][0]))
    else:
        result = [eval(s) for s in src.split(",")]
    return result

def getValFrom2HDMC(line, par, pos=1):
    return float([i.split()[pos] for i in line if par+":" in i][0])

def getValFromSusHi(line, par, pos=1):
    return float([i.split()[pos] for i in line if par+":" in i][-1])

mh = "125"
thdmc_command = args.thdmc_command
sushi_command = args.sushi_command
masses = interp(args.mass)
tanbs = interp(args.tanb)

thdmc_to_sushi = {
    'sin(b-a)':'sinba', 
    'm_H+':'mC', 
    'lambda_6':'lambda6', 
    'lambda_7':'lambda7', 
    'm12^2':'m12',
    'tan(beta)':'tanb',
    'm_h':'mh',
    'm_H':'mH',
    'm_A':'mA'
}

pars = {}

# Loop over mA/tan(beta) and get 2HDMC parameters

for mA in masses:
    for tanb in tanbs:
        d_mtb = pars[(mA, tanb)] = {}
        print "Calculating hMSSM parameters for mA = {0}, tanb = {1}".format(mA, tanb)
        proc = subprocess.Popen([thdmc_command, mh, str(mA), str(tanb), "full2hdmc.out"], stdout=subprocess.PIPE)
        l = proc.stdout.readlines()
        try:
            mH = getValFrom2HDMC(l, 'm_H')
            print "mH = {0}".format(mH)
        except:
            print "Exception detected at mass of {0}".format(str(mH))
            continue
        
        for par in thdmc_to_sushi:
            d_mtb[par] = getValFrom2HDMC(l, par)

        with open('full2hdmc.out') as full_out:
            for line in full_out:
                if line.startswith('DECAY  35'):
                    d_mtb['H_width'] = line.split()[2]
                if line.startswith('DECAY  36'):
                    d_mtb['A_width'] = line.split()[2]

        # SusHi wants m12, not m12**2
        d_mtb['m12^2'] = math.sqrt(d_mtb['m12^2'])

        # create dict for card formatting
        d_format = {}
        for i_from, i_to in thdmc_to_sushi.items():
            d_format[i_to] = d_mtb[i_from]

        d_format['model'] = args.model
        
        d_format['gghlo'] = args.gghlo

        print 'Calculate Sushi cross sections for A and H'

        for higgs in ['H', 'A']:
            d_format['higgs'] = '12' if higgs == 'H' else '21'

            # Now do the SusHi calculation
            with open(args.sushi_card) as sushi_card:
                card = sushi_card.read()
                card = card.format(**d_format)
                
                with open('card_tmp.in', 'w') as sushi_in:
                    sushi_in.write(card)

                output = subprocess.check_output([sushi_command, 'card_tmp.in', 'card_tmp.out'])
                
                output = output.split('\n')
                d_mtb[higgs+'_nnlo'] = getValFromSusHi(output, 'xsec')
                d_mtb[higgs+'_nlo'] = getValFromSusHi(output, 'NLO')
                d_mtb[higgs+'_lo'] = getValFromSusHi(output, 'LO')
                d_mtb[higgs+'_nnlo_unc_down'] = getValFromSusHi(output, ' muR unc.', pos=3)
                d_mtb[higgs+'_nnlo_unc_up'] = getValFromSusHi(output, ' muR unc.', pos=5)
                
                with open('card_tmp.out') as full_out:
                    for line in full_out:
                        if 'H width in GeV' in line:
                            d_mtb['H_width_SusHi'] = line.split()[1]
                        if 'A width in GeV' in line:
                            d_mtb['A_width_SusHi'] = line.split()[1]

        for i, j in d_mtb.items(): print i, j

with open('sushi_out.pkl', 'wb') as sushi_out:
    pickle.dump(pars, sushi_out, protocol=pickle.HIGHEST_PROTOCOL)
