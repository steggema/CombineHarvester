#!/usr/bin/env python

'''Given tan beta and mA values, produces combined datacard with morphed masses
and widths, using SusHi/2HDMC results as input.
'''

import os
import pickle
from argparse import ArgumentParser
import shutil
from glob import glob
from pdb import set_trace

def syscall(cmd):
	print 'Executing: %s' % cmd
	retval = os.system(cmd)
	if retval != 0:
		raise RuntimeError('Command failed!')

parser = ArgumentParser()
parser.add_argument('jobid')
parser.add_argument('parity')
parser.add_argument('mass', type=int)
parser.add_argument('width', type=float)
parser.add_argument('--noblind', action='store_true')
parser.add_argument('--norm', action='store_true')
parser.add_argument('--mergeLJ', action='store_true')
parser.add_argument('--ignore', default='', help='ignore systematics')
parser.add_argument('--extern', default='', help='externalize systematic')
args = parser.parse_args()

val2name = lambda x: str(x).replace('.','p').replace('p0','')

syscall('make_point.sh {} TESTME {}:{}:{} ""'.format(
		args.jobid, args.parity, args.mass, args.width
		))
syscall(
	'hadd -f templates_ALL_POINT.root TESTME.root '
	'%s/src/CombineHarvester/Httbar/data/templates_l?_bkg_%s.root' % (
		os.environ['CMSSW_BASE'],
		args.jobid
		))

if args.extern:
	syscall('externalize.py templates_ALL_POINT.root %s' % args.extern)

print '\n\ncreating workspace\n\n'
opts = ''
if args.mergeLJ:
	opts += "--channels=cmbLJ "
if args.ignore:
	opts += "--ignore='%s'" % args.ignore
syscall((
		'setup_common.py POINT --parity={} --indir=./ --limitdir=./'
		' --masses="{}" --widths="{}" {}').format(
		args.parity, args.mass, val2name(args.width),
		opts
		))

syscall((
		'combineTool.py -M T2W -i {}_{}/* -o workspace.root -P CombineHarvester'
		'.CombineTools.InterferenceModel:interferenceModel').format(
		args.parity, val2name(args.width)
		))

print '\n\nRunning LIMIT\n\n'
syscall((
		'combineTool.py -M Asymptotic -d */*/workspace.root --there'
		' -n .limit --minimizerTolerance=0.1 --minimizerStrategy=1'
		' --rMin=0 --rMax=3 --parallel 1 {}').format(
		'' if args.noblind else '--run blind -t -1'
		))

syscall((
		'combineTool.py -M CollectLimits */*/higgsCombine.limit.Asymptotic'
		'.mH[0-9][0-9][0-9].root'
		))

fname = '%s_%d_%.1f.json' % (args.parity, args.mass, args.width)
if args.extern:
	fname = fname.replace('.json', '_%s.json' % args.extern)
shutil.move('limits.json', fname)
if not args.norm:
	shutil.rmtree(
		'{}_{}'.format(
			args.parity, args.mass, val2name(args.width)
			)
		)
	for fname in glob('*.root'):
		os.remove(fname)
else:
	syscall((
			'tar -cvf {parity}_{mass}_{width}.tar'
			' *.root {parity}_{width}/').format(
			parity = args.parity,
			mass = args.mass,
			width = val2name(args.width)
			))
