#!/usr/bin/env python

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
parser.add_argument('infile')
parser.add_argument('replacements')
parser.add_argument('outfile')
args = parser.parse_args()

import ROOT as R
from pdb import set_trace

infile = R.TFile(args.infile)
replace = R.TFile(args.replacements)
outfile = R.TFile(args.outfile, 'recreate')

for dname in infile.GetListOfKeys():
	idir = dname.ReadObj()
	rdir = replace.Get(dname.GetName())
	odir = outfile.mkdir(dname.GetName())
	to_rep = {i.GetName() for i in rdir.GetListOfKeys()} if rdir else set()
	for key in idir.GetListOfKeys():
		name = key.GetName()
		if name in to_rep:
			print 'replacing', name
			odir.WriteTObject(
				rdir.Get(name), name
				)
		else:
			odir.WriteTObject(
				key.ReadObj(), name
				)
