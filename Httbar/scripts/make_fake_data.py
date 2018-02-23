#! /bin/env python

import ROOT
import argparse
import math
from pdb import set_trace

parser = argparse.ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('sys_name')
args = parser.parse_args()

tfile = ROOT.TFile.Open(args.inputfile, 'update')

categories = [i.GetName() for i in tfile.GetListOfKeys()]
for category in categories:
	bbb_vals = []
	central_vals = []
	new_vals = []
	tdir = tfile.Get(category)
	shapes = set([i.GetName() for i in tdir.GetListOfKeys()])
	nosys  = [
		i for i in shapes 
		if not i.endswith('Up') 
		if not i.endswith('Down') 
		if i != 'data_obs' 
		if not i.startswith('ggH') 
		if not i.startswith('ggA')
		]
	if args.sys_name:
		to_be_added = [
			(i if ('%s_%s' % (i, args.sys_name)) not in shapes else '%s_%s' % (i, args.sys_name)) 
			for i in nosys
			]
	else:
		to_be_added = nosys
	fake_data = tdir.Get('data_obs')
	fake_data.Reset()
	
	for name in to_be_added:
		fake_data.Add(tdir.Get(name))

	#make integers
	for idx in range(fake_data.GetNbinsX()+2):
		fake_data.SetBinContent(
			idx,
			round(
				fake_data.GetBinContent(idx)
				)
			)

	if not args.sys_name: continue
	sgns = [
		i for i in shapes 
		if i.startswith('ggA') or i.startswith('ggH') 
		if i.endswith(args.sys_name)
		]
	for sgn in sgns:
		shifted = tdir.Get(sgn)
		base = sgn.split(args.sys_name)[0][:-1]
		hbase = tdir.Get(base)
		hbase.Reset()
		hbase.Add(shifted)

tfile.Write()
