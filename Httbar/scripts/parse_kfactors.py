#! /bin/env python

from argparse import ArgumentParser
from numpy import array
import gc
from pdb import set_trace

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('output')
args = parser.parse_args()

infile = open(args.inputfile).read().replace('\r', '')
blocks = infile.split('\n\n')
#remove header
blocks[0] = '\n'.join(blocks[0].split('\n')[3:])

name_conversion = {
	'PScalar res' : 'ggA_sgn',
	'Scalar res' : 'ggH_sgn',
	'PScalar Int' : 'ggA_int',
	'Scalar Int' : 'ggH_int',
}
retval = {}
for block in blocks:
	if not block.strip(): continue
	lines = block.split('\n')
	title = lines[0].strip()
	header = lines[1]
	masses = ['M'+i[9:-1] for i in header.split()[1:]]

	lines = lines[2:]
	for line in lines:
		if not line.strip(): continue
		values = [float(i) for i in line.split()]
		width = values[0]
		factors = values[1:]
		assert(len(masses) == len(factors))
		for mass, kfactor in zip(masses, factors):
			key = '_'.join([
					name_conversion[title],
					mass,
					'%.1f' % width
					])
			retval[key] = kfactor

import json
with open(args.output, 'w') as out:
	out.write(json.dumps(retval))
