#!/usr/bin/env python
from argparse import ArgumentParser
import os
parser = ArgumentParser()
parser.add_argument('standard')
parser.add_argument('morphed')
parser.add_argument('width_morphed')
parser.add_argument('doublemorphed')
parser.add_argument('output_dir')
parser.add_argument('--mass', default='500')
args = parser.parse_args()

output_dir = args.output_dir
if not os.path.isdir(output_dir):
	os.makedirs(output_dir)

if not os.path.isfile(args.standard):
	raise IOError('File %s does not exist!' % args.standard)
if not os.path.isfile(args.morphed):
	raise IOError('File %s does not exist!' % args.morphed)

import ROOT

ROOT.gROOT.SetStyle('Plain')
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

standard = ROOT.TFile.Open(args.standard)
morphed = ROOT.TFile.Open(args.morphed)
width_morphed = ROOT.TFile.Open(args.width_morphed)
doublem = ROOT.TFile.Open(args.doublemorphed)
from pdb import set_trace
categories = [i.GetName() for i in doublem.GetListOfKeys()]
procs = [i.GetName() for i in doublem.Get(categories[0]).GetListOfKeys()]
procs = [i for i in procs 
	 if i.startswith('ggA') or i.startswith('ggH')
	 if not (i.endswith('Up') or i.endswith('Down'))
	 if ('M%s' % args.mass) in i
	 ]

for category in categories:
	for process in procs:
		canvas = ROOT.TCanvas('as', 'sad', 800, 600)
		hname = '%s/%s' % (category, process)
		std = standard.Get(hname)
		if not std: raise RuntimeError('Could not find %s' % hname)
		std.SetFillStyle(0)
		std.SetLineColor(ROOT.kBlack)
		std.SetLineWidth(2)
		std.GetXaxis().SetTitleOffset(1.15)
		std.GetXaxis().SetTitle('m(t#bar{t}) [GeV] #otimes cos #theta*_{t_{lep}}')
		std.GetYaxis().SetTitle('Events')
		morph = morphed.Get(hname)
		if not morph: raise RuntimeError('Could not find %s' % hname)
		morph.SetFillStyle(0)
		morph.SetLineColor(ROOT.kBlue)
		morph.SetLineWidth(2)
		morph.SetLineStyle(2)
		wmorph = width_morphed.Get(hname)
		if not wmorph: raise RuntimeError('Could not find %s' % hname)
		wmorph.SetFillStyle(0)
		wmorph.SetLineColor(ROOT.kGreen+2)
		wmorph.SetLineWidth(2)
		wmorph.SetLineStyle(2)
		dmorph = doublem.Get(hname)
		if not dmorph: raise RuntimeError('Could not find %s' % hname)
		dmorph.SetFillStyle(0)
		dmorph.SetLineColor(ROOT.kRed)
		dmorph.SetLineWidth(2)
		dmorph.SetLineStyle(2)
		std.Draw('hist')
		morph.Draw( 'same hist')
		wmorph.Draw('same hist')
		dmorph.Draw('same hist')
		if category == 'll':
			legend = ROOT.TLegend(0.1, 0.7, 0.35, 0.9)
		else:
			legend = ROOT.TLegend(0.65, 0.7, 0.9, 0.9)
		legend.AddEntry(std, "Full simulation", "l")
		legend.AddEntry(morph, "Mass interpolation", "l")
		legend.AddEntry(wmorph, "Width interpolation", "l")
		legend.AddEntry(dmorph, "Width and mass interpolation", "l")
		legend.Draw()
		pngname = '%s/mass_morph_%s_%s.png' % (output_dir, category, process)
		canvas.SaveAs(pngname)
		canvas.SaveAs(pngname.replace('.png', '.pdf'))
		
