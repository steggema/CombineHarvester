#!/usr/bin/env python

'''Given tan beta and mA values, produces combined datacard with morphed masses
and widths, using SusHi/2HDMC results as input.
'''

import os
import pickle
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('mA', type=int)
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
    values = [d for d in mapping.values() if d['m_A'] == mA and d['tan(beta)'] == eval(tanb)]

    if len(values) == 0:
    	raise RuntimeError('No entry found for mA and tan(beta)', mA, tanb)
    if len(values) > 1:
    	print 'Multiple entries found for mA and tan(beta)', mA, tanb, 'picking first'

    values = values[0]
    mH = int(round(float(values['m_H'])))
    # Widths are relative and in per cent
    widthA = round(float(values['A_width'])/mA*100., 1)
    widthH = round(float(values['H_width'])/mH*100., 1)
    
    print 'For mA =', mA, 'tan(beta) =', tanb, 'obtain:'
    print '  widthA =', widthA
    print '  widthH =', widthH
    print '  mH =', mH
    
    out_file_names = inputs_bkg

    for i, (input_sig, input_bkg) in enumerate(zip(inputs_sig, inputs_bkg)):
        # print 'morph_mass.py {} {} A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single_mass {mA}'.format(input_sig, input_bkg, mA=mA)
        out_A = args.outfile.replace('.root', 'A{}_{}.root'.format(mA, i))
        out_H = args.outfile.replace('.root', 'H{}_{}.root'.format(mH, i))
        out_file_names += [out_A, out_H]

        tmp_A = out_A.replace('.root', '_tmp.root')
        tmp_H = out_H.replace('.root', '_tmp.root')

        os.system('morph_mass.py {} {} A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single_mass {} --out {}'.format(input_sig, input_bkg, mA, tmp_A))

        if widthA < 2.5:
            print 'Need width extrapolation; will create 1pc point and use this for subsequent morphing'
            os.system('morph_width_extrapolate.py {} --out {}'.format(tmp_A, tmp_A.replace('.root', '_extr.root')))
            tmp_A = tmp_A.replace('.root', '_extr.root')

        os.system('morph_widths.py {} --nocopy --single_width {} --out {}'.format(tmp_A, widthA, out_A))

        os.system('morph_mass.py {} {} H --algo NonLinearPosFractions --input_masses 400,500,600,750 --single_mass {} --out {}'.format(input_sig, input_bkg, mH, tmp_H))

        if widthH < 2.5:
            print 'Need width extrapolation; will create 1pc point and use this for subsequent morphing'
            os.system('morph_width_extrapolate.py {} --out {}'.format(tmp_H, tmp_H.replace('.root', '_extr.root')))
            tmp_H = tmp_H.replace('.root', '_extr.root')

        os.system('morph_widths.py {} --nocopy --single_width {} --out {}'.format(tmp_H, widthH, out_H))
    
    hadd_cmd = 'hadd -f {} {}'.format(args.outfile, ' '.join(out_file_names))
    
    print 'Running CMD:', hadd_cmd
    print 'NOTE: outfile will be overwritten'
    os.system(hadd_cmd)


