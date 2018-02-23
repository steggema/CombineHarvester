#! /bin/env python

import ROOT
import argparse
import math
from pdb import set_trace

parser = argparse.ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('sys_name')
args = parser.parse_args()

if 'scale_j' not in args.sys_name:
	raise ValueError('Error: this script works only for JEC uncertainties, given how it computes the BBB uncertainties for the ll category. \n\nIf you want to extend it you need to fix it first.')

tfile = ROOT.TFile.Open(args.inputfile, 'update')

categories = [i.GetName() for i in tfile.GetListOfKeys()]
bbb_unc = 'TT_CMS_httbar_%s_MCstatBin%d%s'
for category in categories:
	bbb_vals = []
	central_vals = []
	new_vals = []
	tdir = tfile.Get(category)
	shapes = [i.GetName() for i in tdir.GetListOfKeys() if i.GetName().endswith(args.sys_name)]
	for shape in shapes:
		#get base name
		base = shape.split(args.sys_name)[0][:-1] #remove trailing _
		hshift = tdir.Get(shape)
		hbase = tdir.Get(base)		
		if not bbb_vals:
			bbb_vals = [0]*(hbase.GetNbinsX()+2)
			central_vals = [0]*(hbase.GetNbinsX()+2)
			new_vals = [0]*(hbase.GetNbinsX()+2)

		if base.startswith('ggA') or base.startswith('ggH'): continue
		for idx in range(1, hbase.GetNbinsX()+1): #FIXME check range
			toadd = hshift.GetBinError(idx)**2 if category == 'll' else \
				 hshift.GetBinError(idx)**2 - hbase.GetBinError(idx)**2
			bbb_vals[idx] += toadd
			if base == 'TT':
				central_vals[idx] = hbase.GetBinContent(idx)
				new_vals[idx] = hshift.GetBinContent(idx)
			hbase.SetBinContent(idx, hshift.GetBinContent(idx))

	#reset BBBs
	for idx in range(1, hbase.GetNbinsX()+1):
		herr_up = tdir.Get(bbb_unc % (category, idx, 'Up'))
		herr_dw = tdir.Get(bbb_unc % (category, idx, 'Down'))
		for jdx in range(1, hbase.GetNbinsX()+1):
			if idx != jdx:
				herr_up.SetBinContent(jdx, new_vals[jdx])
				herr_dw.SetBinContent(jdx, new_vals[jdx])
			else:
				err = herr_up.GetBinContent(jdx) - central_vals[jdx]
				new_err = math.sqrt(bbb_vals[jdx]) if category == 'll' else \
					 math.sqrt(err**2 + bbb_vals[jdx])
				herr_up.SetBinContent(jdx, new_vals[jdx]+new_err)
				herr_dw.SetBinContent(jdx, new_vals[jdx]-new_err)

tfile.Write()
