#!/usr/bin/env python
from argparse import ArgumentParser
import numpy as np
parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('--forchecks', action='store_true')
#parser.add_argument('--hyperbolic', action='store_true', help='use hyperbolic interpolation')
args = parser.parse_args()

import ROOT
import shutil
import re
from pdb import set_trace

mapping = {
	'1pc' : 1.0,
'2p5pc' : 2.5,
'3pc' : 3.0,
'3p5pc' : 3.5,
'4pc' : 4.0,
'4p5pc' : 4.5,
'5pc' : 5.0,
'5p5pc' : 5.5,
'6pc' : 6.0,
'6p5pc' : 6.5,
'7pc' : 7.0,
'7p5pc' : 7.5,
'8pc' : 8.0,
'8p5pc' : 8.5,
'9pc' : 9.0,
'9p5pc' : 9.5,
'10pc' : 10.0,
'10p5pc' : 10.5,
'11pc' : 11.0,
'11p5pc' : 11.5,
'12pc' : 12.0,
'12p5pc' : 12.5,
'13pc' : 13.0,
'13p5pc' : 13.5,
'14pc' : 14.0,
'14p5pc' : 14.5,
'15pc' : 15.0,
'15p5pc' : 15.5,
'16pc' : 16.0,
'16p5pc' : 16.5,
'17pc' : 17.0,
'17p5pc' : 17.5,
'18pc' : 18.0,
'18p5pc' : 18.5,
'19pc' : 19.0,
'19p5pc' : 19.5,
'20pc' : 20.0,
'20p5pc' : 20.5,
'21pc' : 21.0,
'21p5pc' : 21.5,
'22pc' : 22.0,
'22p5pc' : 22.5,
'23pc' : 23.0,
'23p5pc' : 23.5,
'24pc' : 24.0,
'24p5pc' : 24.5,
'25pc' : 25.0,
'25p5pc' : 25.5,
'26pc' : 26.0,
'26p5pc' : 26.5,
'27pc' : 27.0,
'27p5pc' : 27.5,
'28pc' : 28.0,
'28p5pc' : 28.5,
'29pc' : 29.0,
'29p5pc' : 29.5,
'30pc' : 30.0,
'30p5pc' : 30.5,
'31pc' : 31.0,
'31p5pc' : 31.5,
'32pc' : 32.0,
'32p5pc' : 32.5,
'33pc' : 33.0,
'33p5pc' : 33.5,
'34pc' : 34.0,
'34p5pc' : 34.5,
'35pc' : 35.0,
'35p5pc' : 35.5,
'36pc' : 36.0,
'36p5pc' : 36.5,
'37pc' : 37.0,
'37p5pc' : 37.5,
'38pc' : 38.0,
'38p5pc' : 38.5,
'39pc' : 39.0,
'39p5pc' : 39.5,
'40pc' : 40.0,
'40p5pc' : 40.5,
'41pc' : 41.0,
'41p5pc' : 41.5,
'42pc' : 42.0,
'42p5pc' : 42.5,
'43pc' : 43.0,
'43p5pc' : 43.5,
'44pc' : 44.0,
'44p5pc' : 44.5,
'45pc' : 45.0,
'45p5pc' : 45.5,
'46pc' : 46.0,
'46p5pc' : 46.5,
'47pc' : 47.0,
'47p5pc' : 47.5,
'48pc' : 48.0,
'48p5pc' : 48.5,
'49pc' : 49.0,
'49p5pc' : 49.5,
'50pc' : 50.0
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
new_points = dictionary = dict(zip(list(np.arange(1.5,2.5,0.5)),list("%s%s" % (str(x).replace('.','p').replace('p0',''),"pc") for x in np.arange(1.5,2.5,0.5))))
for key in mapping.values():
 new_points.pop(key,None)
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
		process, sigint, width, mass_sys = tuple(name.split('-',3))
	except:
		set_trace()
	key = (process, sigint, mass_sys)
	try:
	 return key, mapping[width]
	except:
	 set_trace()

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
	nMorph = len(shapes)*len(new_points)
	shapes = { "sgn" : [i for i in shapes if '_pos-sgn' in i], "int" : [i for i in shapes if '-int-' in i]}
	#there are still a lot of spurious shapes, remove them
	shapes_map = { "sgn": {}, "int": {}}
	hyperbolic = { "sgn": True, "int": False}
	for _type in shapes:
	 for shape in shapes[_type]:
	  k, w = get_info(shape)
	  if k not in shapes_map[_type]:
	   shapes_map[_type][k] = {}
	  shapes_map[_type][k][w] = tdir.Get(shape)
	#compute new histograms
	counter = 0
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
	   counter +=1
	   print counter