#! /bin/env python

import os
import pickle
from argparse import ArgumentParser
from distutils import spawn
from numpy import arange

parser = ArgumentParser()
parser.add_argument('jobid')
parser.add_argument('outdir')
parser.add_argument('parities')
parser.add_argument('masses')
parser.add_argument('widths')
parser.add_argument('--doNotRemove')
parser.add_argument('--noblind', action='store_true')
parser.add_argument('--nokfactors', action='store_true')
parser.add_argument('--runScan', action='store_true')
parser.add_argument('--twoPars', action='store_true')
parser.add_argument('--barlowBeeston', action='store_true')
parser.add_argument('--channels', default='', help='leptonic decay type')
parser.add_argument('--significance', action='store_true')
parser.add_argument('--significance_toys', action='store_true', help='calculate significances based on pre-saved toys')
parser.add_argument('--significance_toys_bunch', default=0, help='bunch for toy significance calculation')
parser.add_argument('--skip_limit', action='store_true', help='skip limit calculation')

args = parser.parse_args()

if not os.path.isdir(args.outdir):
	os.makedirs(args.outdir)

do_not_remove = set(args.doNotRemove.split(',')) if args.doNotRemove else set()

masses = [str(j) for j in arange(*[int(i) for i in args.masses.split(':')])] \
	if ':' in args.masses else args.masses.split(',')

with open('%s/condor.jdl' % args.outdir, 'w') as jdl:
	jdl.write('''
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
getenv = True
executable = %s
+MaxRuntime = 86400
+AccountingGroup = "group_u_CMST3.all"

''' % spawn.find_executable('single_point_limit.py'))
	idx = 0
	for parity in args.parities.split(','):
		for mass in masses:
			for width in args.widths.split(','):
				jdl.write('''
Output = con_{idx}.out
Error = con_{idx}.err
Log = con_{idx}.log
Arguments = {jobid} {parity} {mass} {width} {blind} {keep} {kfactor} {scan} {twoPars} {bb} {ch} {sg} {st} {stb} {sl}
Queue
'''.format(
				idx=idx,
				jobid=args.jobid,
				parity=parity,
				mass=mass,
				width=width,
				blind='--noblind' if args.noblind else '',
				keep='--keep' if ':'.join([parity, mass, width]) in do_not_remove else '',
				kfactor='--kfactor None' if args.nokfactors else '',
				scan='--runScan' if args.runScan else '',
				twoPars='--twoPars' if args.twoPars else '',
				bb='--barlowBeeston' if args.barlowBeeston else '',
				ch='--channels={}'.format(args.channels) if args.channels else '',
				sg='--significance' if args.significance else '',
				st='--significance_toys' if args.significance_toys else '',
				stb='--significance_toys_bunch={}'.format(args.significance_toys_bunch) if args.significance_toys else '',
				sl='--skip_limit' if args.skip_limit else '',
				))
				idx += 1
