#!/usr/bin/env python
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('--forchecks', action='store_true')
parser.add_argument('--hyperbolic', action='store_true', help='use hyperbolic interpolation')
args = parser.parse_args()

import ROOT
import shutil
import re
from pdb import set_trace

mapping = {
	'2p5pc' : 2.5,
	'5pc'   : 5.0,
	'10pc'  : 10.,
	'25pc'  : 25.,
	'50pc'  : 50., 
	}

checks = {
	5.0 : 'checks_5pc' ,
	10. : 'checks_10pc',
	25. : 'checks_25pc',	
}

new_points = {
	7.0 : '7pc' ,
	15. : '15pc',
	20. : '20pc',	
	30. : '30pc',	
	40. : '40pc',	
}

if args.forchecks:
	new_points.update(checks)

available = set(mapping.values())
to_make = set(new_points.keys())
intersection = available.intersection(to_make)
if len(intersection) and not args.forchecks:
	raise ValueError('the points: %s are already computed, I will not do them again!' % ','.join(list(intersection)))

interpolation = {}
for point in to_make:
	above = sorted([i for i in available if point < i])
	below = sorted([i for i in available if point > i])
	if not above or not below:
		raise ValueError('I cannot interpolate %s as it is outside the provided range!' % point)
	interpolation[point] = (below[-1], above[0])

def get_info(name):
	try:
		process, sigint, width, mass_sys = tuple(name.split('-'))
	except:
		set_trace()
	key = (process, sigint, mass_sys)
	return key, mapping[width]

def make_name(key, width):
	process, sigint, mass_sys = key
	return '-'.join([process, sigint, new_points[width], mass_sys])

outname = args.inputfile.replace('.root', '_morphed.root')
shutil.copyfile(args.inputfile, outname)
infile = ROOT.TFile(outname, 'UPDATE')

for category in [i.GetName() for i in infile.GetListOfKeys()]:
	tdir = infile.Get(category)
	tdir.cd()
	shapes = [i.GetName() for i in tdir.GetListOfKeys()]
	shapes = [i for i in shapes if i.startswith('ggA_') or i.startswith('ggH_')]
	#there are still a lot of spurious shapes, remove them
	shapes = [i for i in shapes if '_pos-sgn' in i or '-int-' in i]
	shapes_map = {}
	for shape in shapes:
		k, w = get_info(shape)
		if k not in shapes_map:
			shapes_map[k] = {}
		shapes_map[k][w] = tdir.Get(shape)

	#compute new histograms
	for key in shapes_map:
		for width in new_points:
			b, a = interpolation[width]
			factor = (width-b)/(a-b)
			if args.hyperbolic:
				factor = (1./width-1./b)/(1./a-1./b)
			below = shapes_map[key][b]
			above = shapes_map[key][a]
			new_name = make_name(key, width)
			new_hist = below.Clone(new_name)
			new_hist.Scale(1-factor)
			new_hist.Add(above, factor)
			new_hist.Write()
