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
		raise RuntimeError('Command: %s failed!' % cmd)

parser = ArgumentParser()
parser.add_argument('jobid')
parser.add_argument('parity')
parser.add_argument('mass', type=int)
parser.add_argument('width', type=float)
parser.add_argument('ignore', help='ignore systematics')
parser.add_argument('extern', help='externalize systematic')
parser.add_argument('externval', type=int)
parser.add_argument('--norm', action='store_true')
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

print '\n\ncreating asimov\n'

syscall((
		'setup_common.py POINT --parity={} --indir=./ --limitdir=./'
		' --masses="{}" --widths="{}"').format(
		args.parity, args.mass, val2name(args.width),
		))
syscall((
		'combineTool.py -M T2W -i {}_{}/* -o workspace.root -P CombineHarvester'
		'.CombineTools.InterferenceModel:interferenceModel').format(
		args.parity, val2name(args.width)
		))

syscall((
		'combineTool.py -M GenerateOnly -d */*/workspace.root'
		' -n .limit --parallel 1 -t -1 --saveToys'))

shutil.rmtree(
    '{}_{}'.format(
      args.parity, val2name(args.width)
      )
    )

print '\n\ncreating workspace\n\n'
opts = ''
opts += " --ignore='%s' " % args.ignore
if args.extern:
	opts += ' --add_sys=%s ' % args.extern
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

shutil.copyfile(
	'higgsCombine.limit.GenerateOnly.mH%s.123456.root' % args.mass,
	'{}_{}/{}/asimov.root'.format(args.parity, val2name(args.width), args.mass)
	)

print '\n\nRunning LIMIT\n\n'
opts = ''
if args.extern:
	opts += '--setPhysicsModelParameters={sys}={val} --freezeNuisances={sys}'.format(
		sys = args.extern,
		val = args.externval,
		)
syscall((
		'combineTool.py -M AsymptoticLimits -d */*/workspace.root --there -n .limit'
		' --parallel 1 --rMin=0 --rMax=3'
		' -t -1 {opts} --toysFile=asimov.root').format(
		mass = args.mass,
		opts = opts
		))
syscall((
		'combineTool.py -M CollectLimits */*/higgsCombine.limit.AsymptoticLimits'
		'.mH[0-9][0-9][0-9].root'
		))

fname = '%s_%d_%.1f.json' % (args.parity, args.mass, args.width)
if args.extern:
	fname = fname.replace('.json', '_%s%s.json' % (args.extern, args.externval))
shutil.move('limits.json', fname)
if not args.norm:
	shutil.rmtree(
		'{}_{}'.format(
			args.parity, val2name(args.width)
			)
		)
	for fname in glob('*.root'):
		os.remove(fname)
else:
	syscall((
			'tar -cvf {parity}_{mass}_{width}_{extern}{val}.tar'
			' *.root {parity}_{width}/').format(
			parity = args.parity,
			mass = args.mass,
			width = val2name(args.width),
			extern = args.extern,
			val = args.externval,
			))
