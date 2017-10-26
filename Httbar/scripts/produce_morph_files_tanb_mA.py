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

with open(args.input_sushi) as sushi_pkl:
    mapping = pickle.load(sushi_pkl)
    values = [d for d in mapping.values() if d['m_A'] == mA and d['tan(beta)'] == tanb]
    if len(values) == 0:
    	raise RuntimeError('No entry found for mA and tan(beta)', mA, tanb)
    if len(values) > 1:
    	print 'Multiple entries found for mA and tan(beta)', mA, tanb, 'picking first'

    values = values[0]
    