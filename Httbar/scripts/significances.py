#!/usr/bin/env python
import os
import numpy as np
from argparse import ArgumentParser
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

def get_sig_from_scan_file(f_name, par='r'):
    f = TFile.Open(f_name)
    sig_tree = f.Get('limit')
    for entry in sig_tree:
        if getattr(entry, par) == 0.:
            return np.sqrt(2*entry.deltaNLL)
    return -1.

parser = ArgumentParser()
parser.add_argument('filename', help='location of combine workspace file')
parser.add_argument('out', help='name of npy file to be written containing the results')
parser.add_argument('parity')
parser.add_argument('mass')
parser.add_argument('width')


args = parser.parse_args()
filename = args.filename

syscall('combine {} -M Significance --rMax=3. --cminPreScan --setParameters r=1.0 --freezeParameters r --redefineSignalPOIs g --X-rtd MINIMIZER_analytic -n g_floating'.format(filename))
sig_g = get_sig_from_file('higgsCombineg_floating.Significance.mH120.root')

syscall('combine {} -M Significance --rMax=3. --cminPreScan --setParameters g=1.0 --freezeParameters g --redefineSignalPOIs r --X-rtd MINIMIZER_analytic -n r_floating'.format(filename))
sig_r = get_sig_from_file('higgsCombiner_floating.Significance.mH120.root')

syscall('combine -M MultiDimFit {} --algo=grid -P g --points=61 --robustFit=1 --rMax=3. --alignEdges 1 --setParameterRanges g=0.,3. --freezeParameters r --X-rtd MINIMIZER_analytic --setParameters r=1.0 -n grid_g_floating'.format(filename))

sig_g_scan = get_sig_from_scan_file('higgsCombinegrid_g_floating.MultiDimFit.mH120.root', 'g')

syscall('combine -M MultiDimFit {} --algo=grid -P r --points=61 --robustFit=1 --rMax=3. --alignEdges 1 --setParameterRanges r=0.,3. --freezeParameters g --X-rtd MINIMIZER_analytic --setParameters g=1.0 -n grid_r_floating'.format(filename))

sig_r_scan = get_sig_from_scan_file('higgsCombinegrid_r_floating.MultiDimFit.mH120.root', 'r')


vals_list = [tuple([args.parity, int(args.mass), float(args.width.replace('p', '.')), sig_g, sig_r, sig_g_scan, sig_r_scan])]

with open(args.out, 'wb') as out:
    arr = np.array(
        vals_list,
        dtype=[('parity', 'S1'), ('mass', 'i4'), ('width', 'f4'), ('sig_g', 'f4'), ('sig_r', 'f4'), ('sig_g_scan', 'f4'), ('sig_r_scan', 'f4')]
        )
    np.save(out, arr)
