#!/usr/bin/env python

'''
Prints the fit constraint value out of multiple impacts json files 
'''

import os
import pickle
from argparse import ArgumentParser
import shutil
from glob import glob
from pdb import set_trace
import fnmatch
import json

parser = ArgumentParser()
parser.add_argument('srcs', nargs='+')
parser.add_argument('-f', default='*', help='filter content')
parser.add_argument('-s', default='', help='strip from name')
parser.add_argument('--space', type=int, default=1, help='strip from name')
args = parser.parse_args()

values = []
for src in args.srcs:
	jmap = json.loads(open(src).read())
	valmap = {}
	for entry in jmap['params']:
		if fnmatch.fnmatch(entry['name'], args.f):
			name = entry['name']
			if args.s:
				name = name.replace(args.s, '')
			down, _, up = tuple(entry['fit'])
			valmap[name] = abs(up - down)/2.
	values.append(valmap)

#
# printing
#
allkeys = set(sum((i.keys() for i in values), []))
spacing = ' '*args.space
for key in allkeys:
	line = ('%40s' % key)
	for mm in values:
		line += spacing
		if key in mm:
			line += '% 5.2f' % mm[key]
		else:
			line += '  -  '
	print line
