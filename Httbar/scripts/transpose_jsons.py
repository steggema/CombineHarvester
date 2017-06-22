#!/usr/bin/env python
from argparse import ArgumentParser
import json
import os
from pdb import set_trace

parser = ArgumentParser()
parser.add_argument('jsons', nargs='+')
args = parser.parse_args()

jmap = {}
widths = set()
masses = set()
wmap = lambda x: x.replace('p','.')
mmap = lambda x: int(float(x))
parity = None

for jname in args.jsons:
	base = os.path.basename(jname).replace('.json','')
	pp = ('_A_' if '_A_' in base else '_H_')
	if parity and pp != parity:
		raise ValueError('You cannot mix A and H samples!')
	parity = pp
	width = wmap(base.split(parity)[1])
	widths.add(width)
	vals = json.loads(open(jname).read())
	masses.update(vals.keys())
	jmap[width] = vals

for mass in masses:
	mjson = {}
	for width in widths:
		mjson[width] = jmap[width][mass]
	with open('limits%sM%d.json' % (parity, mmap(mass)), 'w') as out:
		out.write(json.dumps(mjson))
	
	
	
