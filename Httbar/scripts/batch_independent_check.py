#! /bin/env python

import os
import pickle
from argparse import ArgumentParser
import json
from pdb import set_trace
import numpy as np

parser = ArgumentParser()
parser.add_argument('submission_dir')
args = parser.parse_args()

jdl = open('%s/condor.jdl' % args.submission_dir).read()
blocks = jdl.split('\n\n')
header = blocks[0]
block_map = {}
for block in blocks[1:]:
	key = tuple(block.split('Arguments = ')[1].split(' ')[1:4])
	block_map[key] = block

summary = {}
npass = 0
fails = []
mis_runs = 0
produced = None
for key, submit in block_map.iteritems():
	parity, mass, width = key
	width = '%.1f' % float(width)
	name = '_'.join([parity, mass, width])
	jname = '%s/%s.json' % (args.submission_dir, name)
	if not os.path.isfile(jname):
		fails.append(key)
 		print 'Point %s not computed successfully!' % (key,)
		summary[key] = {}
	else:
		jmap = json.loads(open(jname).read())
		_, mass, _ = key		
		mass = '%.1f' % float(mass)
		if len(jmap[mass]) < 5:
			mis_runs += 1
			fails.append(key)
			print 'Point %s not computed successfully!' % (key,)
			summary[key] = {}
			continue
		npass += 1
		summary[key] = jmap[mass]
		if produced is None:
			produced = jmap[mass].keys()

vals_list = []
for key, item in summary.iteritems():
	parity, mass, width = key
	mass = int(mass)
	width = float(width)
	limits = [item.get(i, -1) for i in produced]
	vals_list.append(tuple([parity, mass, width]+limits))

print '''Run Summary:
  Successful jobs: %d
  Failed jobs: %d
  Out of which jobs not properly finished: %d
''' % (npass, len(fails), mis_runs)

if fails:
	print 'dumping rescue job'
	with open('%s/condor.rescue.jdl' % args.submission_dir, 'w') as rescue:
		rescue.write(header)
		rescue.write('\n\n')
		rescue.write(
			'\n\n'.join([block_map[key] for key in fails])
			)

if produced is None:
	print 'All points failed! Exiting!'
	exit(0)

with open('%s/summary.npy' % args.submission_dir, 'wb') as out:
	arr = np.array(
		vals_list,
		dtype = [('parity', 'S1'), ('mass', 'i4'), ('width', 'f4')] + [(str(i), 'f4') for i in produced]
		)
	np.save(out, arr)


