#!/usr/bin/env python
import os
from argparse import ArgumentParser
import numpy as np
from ROOT import TFile


def syscall(cmd):
    print 'Executing: %s' % cmd
    retval = os.system(cmd)
    if retval != 0:
        raise RuntimeError('Command failed!')

def get_sig_from_file(f_name):
    f = TFile.Open(f_name)
    sig_tree = f.Get('limit')
    for entry in sig_tree:
        return entry.limit

def get_g_from_file(f_name):
    f = TFile.Open(f_name)
    sig_tree = f.Get('limit')
    for entry in sig_tree:
        return entry.g

def get_g(f_name, toy_dir, i_t, max_g_val=3.):
    syscall('combine -M MultiDimFit {} --robustFit=1 --alignEdges 1 --setParameterRanges g=0.,{} --freezeParameters r --X-rtd MINIMIZER_analytic --setParameters r=1.0 -D {}/higgsCombineTest.GenerateOnly.mH120.{}.root:toys/toy_1 --cminPreScan'.format(f_name, max_g_val, toy_dir, i_t))

    return get_g_from_file('higgsCombineTest.MultiDimFit.mH120.root')


parser = ArgumentParser()
parser.add_argument('filename', help='location of combine workspace file')
parser.add_argument('toy_dir', help='location of directory with toy files')
parser.add_argument('bunch', type=int, help='toy bunch (0-9)')
parser.add_argument('out', help='name of npy file to be written containing the results')
parser.add_argument('parity')
parser.add_argument('mass')
parser.add_argument('width')


args = parser.parse_args()
filename = args.filename

vals_list = []

bunches = [(i*1000, (i+1)*1000) for i in xrange(10)]

for i_toy in xrange(bunches[args.bunch][0], bunches[args.bunch][1]):

    fitted_g = np.nan
    for max_g in [3., 2.5, 2., 1.5, 1., 10.]:
        fitted_g = get_g(filename, args.toy_dir, i_toy, max_g_val=3.)
        try:
            if not np.isnan(fitted_g):
                break
        except TypeError:
            print 'TypeError encountered'
            print 'Fitted g', fitted_g, type(fitted_g)

    syscall('combine {} -M Significance --setParameterRanges g=0.,3. --rMax=3. --cminPreScan --setParameters r=1,g=0 --freezeParameters r --redefineSignalPOIs g --X-rtd MINIMIZER_analytic -n g_floating -D {}/higgsCombineTest.GenerateOnly.mH120.{}.root:toys/toy_1'.format(filename, args.toy_dir, i_toy))

    significance_g = get_sig_from_file('higgsCombineg_floating.Significance.mH120.root')

    syscall('combine {} -M Significance --setParameterRanges g=0.,2.5 --cminPreScan --setParameters r=1,g=0 --freezeParameters r --redefineSignalPOIs g --X-rtd MINIMIZER_analytic -n g_floating -D {}/higgsCombineTest.GenerateOnly.mH120.{}.root:toys/toy_1'.format(filename, args.toy_dir, i_toy))

    significance_g_2p5 = get_sig_from_file('higgsCombineg_floating.Significance.mH120.root')

    syscall('combine {} -M Significance --rMax=3. --cminPreScan --setParameters g={},r=0 --freezeParameters g --redefineSignalPOIs r --X-rtd MINIMIZER_analytic -n r_floating -D {}/higgsCombineTest.GenerateOnly.mH120.{}.root:toys/toy_1'.format(filename, fitted_g, args.toy_dir, i_toy))

    significance_r = get_sig_from_file('higgsCombiner_floating.Significance.mH120.root')

    syscall('combine {} -M Significance --rMax=3. --cminPreScan --setParameters g=1,r=0 --freezeParameters g --redefineSignalPOIs r --X-rtd MINIMIZER_analytic -n r_floating -D {}/higgsCombineTest.GenerateOnly.mH120.{}.root:toys/toy_1'.format(filename, args.toy_dir, i_toy))

    significance_r_gfixed = get_sig_from_file('higgsCombiner_floating.Significance.mH120.root')

    vals_list += [tuple([args.parity, int(args.mass), float(args.width.replace('p', '.')), fitted_g, significance_g, significance_g_2p5, significance_r, significance_r_gfixed, i_toy])]
    # print vals_list[-1]

with open(args.out, 'wb') as out:
    arr = np.array(
        vals_list,
        dtype=[('parity', 'S1'), ('mass', 'i4'), ('width', 'f4'), ('fitted_g', 'f4'), ('sig_g', 'f4'), ('sig_g_2p5', 'f4'), ('sig_r', 'f4'), ('sig_r_g1', 'f4'), ('i_toy', 'i4')]
        )
    np.save(out, arr)
