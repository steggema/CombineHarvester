#!/usr/bin/env python

'''Given tan beta and mA values, produces combined datacard with morphed masses
and widths, using SusHi/2HDMC results as input.
'''

import os
import pickle
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('mA')
parser.add_argument('tanb')
parser.add_argument('input_sushi')
parser.add_argument('inputs_sig', help='comma separated list of signal input files')
parser.add_argument('inputs_bkg', help='comma separated list of bkg input files. Same order required as for signal files')
parser.add_argument('outfile')
args = parser.parse_args()

mA = args.mA
tanb = args.tanb
inputs_sig = args.inputs_sig.split(',')
inputs_bkg = args.inputs_bkg.split(',')

mH = mA
widthH = 0.
widthA = 0.

with open(args.input_sushi) as sushi_pkl:
    mapping = pickle.load(sushi_pkl)
    values = [d for d in mapping.values() if d['m_A'] == eval(mA) and d['tan(beta)'] == eval(tanb)]

    if len(values) == 0:
    	raise RuntimeError('No entry found for mA and tan(beta)', mA, tanb)
    if len(values) > 1:
    	print 'Multiple entries found for mA and tan(beta)', mA, tanb, 'picking first'

    values = values[0]
    widthA = round(float(values['A_width']), 2)
    widthH = round(float(values['H_width']), 2)
    mH = int(round(float(values['m_H'])))
    print 'For mA =', mA, 'tan(beta) =', tanb, 'obtain:'
    print '  widthA =', widthA
    print '  widthH =', widthH
    print '  mH =', mH
    
    for input_sig, input_bkg in zip(inputs_sig, inputs_bkg):
        print 'morph_mass.py {} {} A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single_mass {mA}'.format(input_sig, input_bkg, mA=mA)
        os.system('morph_mass.py {} {} A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single_mass {mA}'.format(input_sig, input_bkg, mA=mA))
        os.system('morph_mass.py {} {} H --algo NonLinearPosFractions --input_masses 400,500,600,750 --single_mass {mH}'.format(input_sig, input_bkg, mH=mH))

    import pdb; pdb.set_trace()
