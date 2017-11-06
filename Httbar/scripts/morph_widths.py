#!/usr/bin/env python
from argparse import ArgumentParser
import numpy as np
parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('--forchecks', action='store_true')
parser.add_argument('--nocopy', action='store_true', help='does not copy the file to add the points, but just create the new points')
parser.add_argument('--out', help='forces output name')
parser.add_argument('--kfactors')
parser.add_argument('--single', type=float)
parser.add_argument('--filter', default='*')
#parser.add_argument('--hyperbolic', action='store_true', help='use hyperbolic interpolation')
args = parser.parse_args()

import ROOT
import shutil
import re
from pdb import set_trace
from fnmatch import fnmatch
import json
import os

kfactors = None
if args.kfactors:
	if not os.path.isfile(args.kfactors):
		raise IOError('File: %s does not exist' % args.kfactors)
	kfactors = json.loads(open(args.kfactors).read())

mapping = {
  '1pc' : 1.0,
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
'''
new_points = {
	7.0 : '7pc' ,
	15. : '15pc',
	20. : '20pc',	
	30. : '30pc',	
	40. : '40pc',	
}
'''
widths = np.arange(2.5,50,0.5)
val2name = lambda x: "%s%s" % (str(x).replace('.','p').replace('p0',''),"pc")
if args.single:
	widths = [args.single]
new_points = dictionary = dict((i, val2name(i)) for i in widths)
for key in mapping.values():
 new_points.pop(key,None)
if args.forchecks:
	new_points = checks

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
		process, sigint, width, mass_sys = tuple(name.split('-',3))
	except:
		set_trace()
	key = (process, sigint, mass_sys)
	return key, mapping[width]

def make_name(key, width):
	process, sigint, mass_sys = key
	return '-'.join([process, sigint, new_points[width], mass_sys])

outname = args.inputfile.replace('.root', '_width_morphed.root')
if args.out:
	outname = args.out
if args.nocopy:
	infile = ROOT.TFile(args.inputfile)
	outfile = ROOT.TFile(outname, 'recreate')
	outfile.cd()
else:
	shutil.copyfile(args.inputfile, outname)
	infile = ROOT.TFile(outname, 'UPDATE')
	outfile = None

for category in [i.GetName() for i in infile.GetListOfKeys()]:
	counter = 0
	indir = infile.Get(category)
	indir.cd()
	shapes = [i.GetName() for i in indir.GetListOfKeys()]
	if outfile:
		odir = outfile.mkdir(indir.GetName())
		odir.cd()
	else:
		odir = indir
	if args.forchecks:
		shapes = [i for i in shapes if not (i.endswith('Up') or i.endswith('Down'))]
	shapes = [i for i in shapes if (i.startswith('ggA_') or i.startswith('ggH_')) and not i.endswith('_')]
	nMorph = len(shapes)*len(new_points)
	shapes = [i for i in shapes if fnmatch(i, args.filter)]
	counter = 0
	shapes = { "sgn" : (i for i in shapes if '_pos-sgn' in i), "int" : (i for i in shapes if '-int-' in i)}
	#there are still a lot of spurious shapes, remove them
	shapes_map = { "sgn": {}, "int": {}}
	hyperbolic = { "sgn": True, "int": False}
	for _type in shapes:
	 for shape in shapes[_type]:
	  k, w = get_info(shape)
	  if k not in shapes_map[_type]:
	   shapes_map[_type][k] = {}
	  shapes_map[_type][k][w] = indir.Get(shape)
	  
	  key = '_'.join([
			k[0].split('_')[0]+'_'+k[1],
			k[2][:4], #remove everything after the mass
			'%.1f' % w
	  ])
	  
	  if kfactors:
	   if key not in kfactors:
	    print 'skipping key %s as not found in json' % key
	    continue
	   shapes_map[_type][k][w].Scale(kfactors[key])
	#compute new histograms
	for _type in shapes_map:
	 for key in shapes_map[_type]:
	  for width in new_points:
	   b, a = interpolation[width]
	   if hyperbolic[_type]:
	    factor = (1./width-1./b)/(1./a-1./b)
	   else:
	    factor = (width-b)/(a-b)
	   below = shapes_map[_type][key][b]
	   above = shapes_map[_type][key][a]
	   new_name = make_name(key, width)
	   new_hist = below.Clone(new_name)
	   new_hist.Scale(1-factor)
	   new_hist.Add(above, factor)
	   new_hist.Write()
	   counter += 1
	   print "Category-{} done: {}/{}".format(category,counter,nMorph)
