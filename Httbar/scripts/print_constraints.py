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
args = parser.parse_args()

values = []
for src in args.srcs:
	jmap = json.loads(open(src).read())
	valmap = {}
	for entry in jmap['params']:
		if fnmatch.fnmatch(entry['name'], args.f):
			down, _, up = tuple(entry['fit'])
			valmap[entry['name']] = abs(up - down)/2.
	values.append(valmap)

#
# printing
#
allkeys = set(sum((i.keys() for i in values), []))
for key in allkeys:
	line = '%40s  \t' % key
	for mm in values:
		if key in mm:
			line += '% 5.2f\t' % mm[key]
		else:
			line += '%5s\t' % '-'
	print line
