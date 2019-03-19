#! /bin/env python

# pylint: disable=W0312,C0330

import math
from argparse import ArgumentParser
from pdb import set_trace
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)
plt.rcParams['text.latex.preamble']=[
	r"\usepackage{amsmath}",
]
plt.rcParams["mathtext.default"] = 'regular'
# plt.rcParams["mathtext.fontset"] = "stix"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as ticker

print 'Run with matplotlib > 2, e.g. by sourcing CMSSW_10_3_X'

parser = ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

# Stolen from Andrey
def max_g(cp, phi_mass, rel_width):
	"""Compute maximal allowed value of the coupling scale factor.

	Computed value corresponds to a 100% branching ratio of H->tt.

	Arguments:
		cp:  CP state, 'A' or 'H'.
		phi_mass:  Mass of the Higgs boson, GeV.
		width:  Relative width of the Higgs boson.
	"""

	gF = 1.1663787e-5  # GeV^(-2)
	mt = 172.5  # GeV

	if phi_mass <= 2 * mt:
		return 0.

	w = 3 * gF * mt ** 2 * phi_mass / (4 * math.pi * math.sqrt(2))
	beta = math.sqrt(1 - (2 * mt / phi_mass) ** 2)

	if cp == 'A':
		width_g1 = w * beta
	elif cp == 'H':
		width_g1 = w * beta ** 3
	else:
		raise RuntimeError('Cannot recognize CP state "{}".'.format(cp))

	return math.sqrt(rel_width * phi_mass / width_g1)

xlabels = {
	'mass' : r'm$_{\mathrm{\mathsf{%s}}}$\, [GeV]',
	'width': r'width$_{\mathrm{\mathsf{%s}}}$\, [\%%]',
	}

addenda = {
	# 'width': r'\textbf{m}$\boldsymbol{_{\mathrm{\mathsf{%s}}} \mathsf{= %d}}$\textbf{\, GeV }',
	# 'mass' : r'\textbf{width}$\boldsymbol{_{\mathrm{\mathsf{%s}}} \mathsf{= %.1f}}$\textbf{\%% }',
	'width': r'm$_{\mathrm{\mathsf{%s}}}$ = {%d}\,GeV',
	# 'mass' : r'Width$_{\mathrm{\mathsf{%s}} \mathsf{= %.1f}}$\%%',
	'mass' : r'$\Gamma_{\mathrm{\mathsf{%s}}}$/m$_{\mathrm{\mathsf{%s}}}$ = {%.1f}\%%',
	}

vartoadd = {
	'width' : 'mass',
	'mass' : 'width'
}
val2name = lambda x: ('%.1f' % x).replace('.','p').replace('p0','')

def make_plot(subset, xvar, maxg_values=None):
		subset.sort(order=xvar)
		print subset
		print xvar

		parity = list(set(subset['parity']))[0]
		sxvar = subset[xvar]
		x_min = sxvar.min()
		x_max = sxvar.max()	
		y_min = min(subset['exp-2'].min(), subset['obs'].min())*0.8
		y_max = max(subset['exp+2'].max(), subset['obs'].max())/0.68
		y_max = min(y_max, 3./0.7)
		y_leg_cutoff = min( y_min + (y_max - y_min) * 0.68, 3.) # reserve ~30% for legend

		# obs_color = (103./255., 203./255., 123./255., 0.4)
		obs_color = (135./255., 206./255., 250./255., 0.5)
		
		fig = plt.figure(figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
		ax = fig.add_subplot(111)
		ax.xaxis.set_major_formatter(
			ticker.FormatStrFormatter("%d")
			)
		ax.yaxis.set_major_formatter(
			ticker.FormatStrFormatter("%.1f")
			)
		handles = []
		
		# #FIXME: add observed
		# observed = plt.plot(
		# 	sxvar, np.random.normal(scale=0.15, size=len(subset['exp0']))+subset['exp0'], 
		# 	color='k', linestyle='-', markersize=10, marker='.'
		# 	)


		observed = plt.plot(
			sxvar, subset['obs'], 
			color='k', linestyle='None'#, markersize=10, marker='.'
			)

		handles.append(
			(mpatches.Patch(color=obs_color), 'Observed')
			# (mpatches.Patch(color=obs_color), mlines.Line2D([], [], color='k', linestyle='None', markersize=10, marker='.')), 'Observed')
			)
		
		center = plt.plot(sxvar, subset['exp0'], color='blue', linestyle='-')
		handles.append(
			(mlines.Line2D([], [], color='blue', linestyle='-'), 'Expected')
			)
		twosig = plt.fill_between(sxvar, subset['exp-2'], subset['exp+2'], color=twosigma)

		if maxg_values is not None:
			# handles.append((mpatches.Patch(
			# 		color=unphys_region[0].get_facecolor(), alpha=unphys_region[0].get_alpha(),
			# 		lw=0.
			# 	), r'$\Gamma_\mathrm{t\bar t} > \Gamma_\mathrm{tot}$'))
			# handles.append((mpatches.Patch(color='none', hatch='||', edgecolor='gray', linewidth=1.), mlines.Line2D([], [], color='gray', linestyle='-')), r'$\Gamma_\mathrm{t\bar t} > \Gamma_\mathrm{tot}$'))
			handles.append((mpatches.Patch(facecolor='none', hatch='||', edgecolor='gray', linewidth=1.), r'$\Gamma_\mathrm{\mathsf{%s}\rightarrow t\bar t} > \Gamma_\mathrm{\mathsf{%s}}$'%(parity, parity)))

		handles.append(
			# (mpatches.Patch(color=twosigma), r'$\mathsf{\pm}$2\,s.d.\ expected')
			# )
			(mpatches.Patch(color=twosigma), r'95\% expected')
			)
		onesig = plt.fill_between(sxvar, subset['exp+1'], subset['exp-1'], color=onesigma)
		handles.append(
			# (mpatches.Patch(color=onesigma), r'$\mathsf{\pm}$1\,s.d.\ expected')
			# )
			(mpatches.Patch(color=onesigma), r'68\% expected')
			)


		#version bug, the opacity is not handled in mpatches, therefore we make it lighter
		# alpha = obs_color[3]
		# patch_color = [i*alpha+1.*(1-alpha) for i in obs_color]
		# patch_color[3] = 1.
		lower_contour =  np.array([val if val < y_leg_cutoff else y_leg_cutoff for val in subset['obslower']])
		upper_contour =  np.array([val if val < y_leg_cutoff else y_leg_cutoff for val in subset['obsupper']])

		observed_contour = plt.fill_between(sxvar, subset['obs'], lower_contour, color=obs_color, linewidth=0)


		observed_contour = plt.fill_between(sxvar, upper_contour, [y_leg_cutoff for n in xrange(len(subset['obsupper']))], color=obs_color, linewidth=0)
		# observed_contour = plt.fill_between(sxvar, subset['obslower'], subset['obsupper'], color=obs_color)
		lower_to_draw =  np.array([val if val < 3. else np.nan for val in subset['obslower']])
		# observed_lower = plt.plot(
		# 	sxvar, lower_to_draw, 
		# 	color='k', linestyle='None'#, markersize=10, marker='.'
		# 	)
		# observed_upper = plt.plot(
		# 	sxvar, subset['obsupper'], 
		# 	color='k', linestyle='None'#, markersize=10, marker='.'
		# 	)

		legend_border = plt.plot([x_min, x_max], [y_leg_cutoff, y_leg_cutoff], color='k', linestyle='-', linewidth=2)

		if maxg_values is not None:
			# maxg_values_todraw = [val if val < y_leg_cutoff else y_leg_cutoff for val in maxg_values]
			# unphys_region = ax.fill(
			# 	list(sxvar) + [sxvar[-1], sxvar[0]],
			# 	list(maxg_values_todraw)+[y_leg_cutoff, y_leg_cutoff],
			# 	color='gray', alpha=0.2, lw=0, zorder=1.5
			# 	)
			maxg_xvalues_todraw = [val[0]for val in maxg_values if val[1] < y_leg_cutoff]
			maxg_values_todraw = [val[1] for val in maxg_values  if val[1] < y_leg_cutoff]
			unphys_region = plt.plot(maxg_xvalues_todraw, maxg_values_todraw, color='gray', linestyle='-')
			matplotlib.rcParams['hatch.linewidth'] = 1.2
			plt.fill_between(maxg_xvalues_todraw, maxg_values_todraw, [min(val+0.02*(y_max-y_min), y_leg_cutoff) for val in maxg_values_todraw], facecolor='none', hatch='||', edgecolor='gray', linewidth=0.)

		debug_lines = False
		if debug_lines and any(the_y < y_leg_cutoff for the_y in upper_contour):
			for x_, y_min_, y_max_, width_ in zip(sxvar, subset['obs'], lower_contour, subset['width']):
				if width_ < subset['width'][0]: continue
				plt.plot([x_, x_], [y_min_, y_max_], color='k', linestyle='-', linewidth=2)
			for x_, y_min_, y_max_, width_ in zip(sxvar, upper_contour, [y_leg_cutoff for _ in xrange(len(subset['obsupper']))], subset['width']):
				if width_ < subset['width'][0]: continue
				plt.plot([x_, x_], [y_min_, y_max_], color='k', linestyle='-', linewidth=2)

		#Fake observed, just to check it works
		## plt.fill_between(
		## 	xs, [0]*len(xs), [8, 6, 5, 4.3, 3.5, 3, 2, 1.5], 
		## 	facecolor=obs_color, edgecolor='k', linewidth=1
		## )
		plt.xlabel(	
			xlabels[xvar] % parity, fontsize=32, 
			horizontalalignment='right', x=1.0, 
		)
		#by hand y label, in pyplot 1.4 it aligns properly, here not
		plt.ylabel(
			r'Coupling modifier', fontsize=32, 
			horizontalalignment='right', 
			y=0.95 #shifts the label down just right
		)
		plt.xlim((x_min, x_max)) 
		plt.ylim((y_min, y_max)) 
		
		delta_y = y_max - y_min
		#rectangle around the legend and the CMS label
		# ax.add_patch(
		#	 patches.Rectangle(
		#		 (x_min, y_max),   # (x,y)
		#		 (x_max-x_min),		  # width
		#		 1.35*delta_y/10,		  # height
		#		 clip_on=False,
		#		 facecolor='w'
		#	 )
		# )
		
		ret = []
		#legend
		
		legend_x = 0.43
		legend = plt.legend(
			x(handles), y(handles),
			# bbox_to_anchor=(legend_x, 1., .55, .102), 
			loc=1,
			ncol=2, mode="expand", borderaxespad=0.,
			fontsize=29,
			frameon=False
		)
		fontP = matplotlib.font_manager.FontProperties()
		fontP.set_size(29)
		legend.set_title(title='95\% CL limits', prop=fontP)
		#legend title (again, due to version)
		other_var = list(set(subset[vartoadd[xvar]]))[0]
		ret.append(
			plt.text(
			# x_min+(x_max-x_min)*0.50, y_max-delta_y*.27,
			x_min+(x_max-x_min)*0.50, y_max-delta_y*.286,
				addenda[xvar] % ((parity, other_var) if xvar == 'width' else (parity, parity, other_var) ),
				 # +r'\textbf{95\% CL Excluded}:',
			fontsize=29,
			horizontalalignment='left'
			)
			)
		
		#CMS blurb
		plt.text(
			x_min+(x_max-x_min)*0.00, y_max+0.025*delta_y,
			r'''\textbf{CMS} \textit{Preliminary}''',
			# r'''\textbf{CMS}''',
			fontsize=32
			)
		
		#lumi stuff
		ret.append(
			plt.text(
			x_max-(x_max-x_min)*0.01, y_max+0.025*delta_y,
			r'35.9 fb$^{\mathrm{\mathsf{-1}}}$ (13 TeV)',
			fontsize=32,
			horizontalalignment='right'
			)
			)
		
		ax.tick_params(axis='both', labelsize=29, which='both')
		return ret

with open(args.input) as pkl:
	limits = np.load(pkl)


x = lambda vv: [i for i, _ in vv]
y = lambda vv: [i for _, i in vv]

masses = sorted(list(set(limits['mass'])))
widths = sorted(list(set(limits['width'])))
onesigma = '#00f847'
twosigma = '#fffc4d'
line = '#ff1521'

for parity in ['A', 'H']:
	for width in widths:
		subset = limits[
			(limits['parity'] == parity) & \
				(limits['width'] == width)
			]

		if not subset.size:
			print 'No subset', parity, width, 'continuing'

		# if parity == 'A' and width in [7.5, 10., 15., 20., 25.]:
		subset.sort(order='mass')
		for subsubset in subset:
			# Crazy hack, FIXME
			# For values of width < 10, the observed upper limits rather coincide
			# with the 2nd upper limits for higher masses, so we align them
			# here explicitly
			if (width == 7.5 and subsubset[1] <= 725):
				subsubset[3+12] = np.nan
				subsubset[3+6] = np.nan
			if subsubset[3+6] < 3. and subsubset[3+12] < 3.:
			# if (width == 10. and subsubset[1] ==735) or (width == 15. and subsubset[1] ==735) or (width == 20. and subsubset[1] ==725): # or (width == 15. and subsubset[1] <= 735) or (width == 15. and subsubset[1] <= 735) or (width == 20. and subsubset[1] <= 730) or (width == 25. and subsubset[1] <= 745):
				subset = np.hstack([subset, subsubset])
				# subsubset[3+12] = subsubset[3]
				# subset[0][1] = subset[0][1]-0.0000001 # for sorting
				subset[-1][2] = subset[0][2]-0.00001 # for sorting
				subset[-1][3+6] = 3.
				subset[-1][3+12] = 3.
				break
				# subsubset[3] = np.nan


		# maxg_values = np.empty_like(masses, dtype=float)
		
		# for i in range(len(masses)):
		# 	maxg_values[i] = max_g(parity, masses[i], width/100.)

		maxg_values = [(mass, max_g(parity, mass, width/100.)) for mass in np.arange(min(masses), max(masses)+5., 5.)]


		ensure_drawn = make_plot(subset, 'mass', maxg_values)
	
		wname = val2name(width)
		plt.savefig(
			'limit_%s_%s.pdf' % (parity, wname),
			bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
			bbox_inches='tight'
		)
		plt.savefig(
			'limit_%s_%s.png' % (parity, wname),
			bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
			bbox_inches='tight'
		)
		plt.clf()
	
	for mass in masses:
		subset = limits[
			(limits['parity'] == parity) & \
				(limits['mass'] == mass)
			]
		if not subset.size:
			print 'No subset', parity, mass, 'continuing'
			continue
		# if mass == 735 and parity=='H':
		# 	set_trace()

		if mass == 750:
			for subsubset in subset:
				# Crazy hack, FIXME
				# For values of width < 10, the observed upper limits rather coincide
				# with the 2nd upper limits for higher masses, so we align them
				# here explicitly
				if subsubset[2] < 10.:
					subsubset[3+12] = subsubset[3]
					subsubset[3+6] = np.nan
					subsubset[3] = np.nan
				if (width == 7.5 and subsubset[1] <= 725):
					subsubset[3+12] = np.nan
					subsubset[3+6] = np.nan
		if mass == 725:
			for subsubset in subset:
				if subsubset[2] == 7.5:
					subsubset[3+12] = np.nan
					subsubset[3+6] = np.nan
		# maxg_values = np.empty_like(widths)
		
		# for i in range(len(widths)):
		# 	maxg_values[i] = max_g(parity, mass, widths[i]/100.)
		maxg_values = [(width, max_g(parity, mass, width/100.)) for width in np.arange(min(widths), max(widths)+0.05, 0.05)]

		ensure_drawn = make_plot(subset, 'width', maxg_values)
	
		plt.savefig(
			'limit_%s_M%s.pdf' % (parity, mass),
			bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
			bbox_inches='tight'
		)
		plt.savefig(
			'limit_%s_M%s.png' % (parity, mass),
			bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
			bbox_inches='tight'
		)
		plt.clf()
	
	# for style in 'obs', 'exp0':
	# 	#
	# 	#  2D color plots	
	# 	#
	# 	subset = limits[limits['parity'] == parity]
	# 	subset.sort(order=('width', 'mass'))
		
	# 	x_min = subset['mass'].min() - 25.
	# 	x_max = subset['mass'].max() + 25.
	# 	y_min = subset['width'].min() #FIXME: add observed
	# 	y_max = subset['width'].max()
		
	# 	fig = plt.figure(figsize=(10, 10), dpi= 80, facecolor='w', edgecolor='k')
	# 	ax = fig.add_subplot(111)
	# 	ax.xaxis.set_major_formatter(
	# 		ticker.FormatStrFormatter("%d")
	# 		)
	# 	#hardcoded
	# 	all_masses = np.array(masses+[800.])-25.#/2
	# 	all_widths = [0.075]+[(widths[i]+widths[i-1])/2 for i in range(1, len(widths))]+[100]
	# 	X,Y = np.meshgrid(all_masses, all_widths)
		

	# 	import pdb; pdb.set_trace()
	# 	Z = subset[style].reshape((len(widths), len(masses)))
	# 	#add one row/column
	# 	Z = np.hstack((
	# 			np.vstack((
	# 					Z, 100*np.ones((1, Z.shape[1]))
	# 					)), 
	# 			100*np.ones((X.shape[0], 1))
	# 			))
		
	# 	heatmap = plt.pcolormesh(
	# 		X, Y, Z,
	# 		# cmap=plt.cm.Greens,
	# 		cmap=plt.cm.YlGnBu,
	# 		vmin=subset[style].min()*0.2, 
	# 		vmax=subset[style].max()*1.2
	# 		)
	# 	#plt.xticks(masses)
	# 	ax.set_yscale('log')
	# 	ax.set_yticks(widths)
	# 	ax.yaxis.set_major_formatter(
	# 		ticker.FormatStrFormatter("%.1f")
	# 		)

	# 	cbar = plt.colorbar(heatmap, format=ticker.FormatStrFormatter("%.1f"))
	# 	# cbar.ax.set_ylabel('95\% CL limit on coupling modifier')
	# 	cbar.set_label('95\% CL limit on coupling modifier', size=29)
	# 	cbar.ax.tick_params(labelsize=29)

	# 	plt.xlabel(	
	# 		xlabels['mass'] % parity, fontsize=32, 
	# 		horizontalalignment='right', x=1.0, 
	# 	)
	# 	#by hand y label, in pyplot 1.4 it aligns properly, here not
	# 	plt.ylabel(
	# 		xlabels['width'] % parity, fontsize=32, 
	# 		horizontalalignment='right', 
	# 		y=0.85 #shifts the label down just right
	# 	)
	# 	plt.xlim((x_min, x_max)) 
	# 	plt.ylim((y_min, y_max)) 
		
	# 	delta_y = y_max - y_min
	# 	# #rectangle around the legend and the CMS label
	# 	# ax.add_patch(
	# 	#	 patches.Rectangle(
	# 	#		 (x_min, y_max),   # (x,y)
	# 	#		 (x_max-x_min),		  # width
	# 	#		 60,		  # height
	# 	#		 clip_on=False,
	# 	#		 facecolor='w'
	# 	#	 )
	# 	# )
		
	# 	# #legend title (again, due to version)
	# 	# legend_x = 0.45
	# 	# text = plt.text(
	# 	# 	x_min+(x_max-x_min)*(legend_x+0.01), y_max+40,
	# 	# 	r'\textbf{95\% CL Excluded}',
	# 	# 	fontsize=32,
	# 	# 	horizontalalignment='left'
	# 	# 	)
		
	# 	#CMS blurb
	# 	plt.text(
	# 		x_min+(x_max-x_min)*0.01, y_max+3,
	# 		r'''\textbf{CMS} \textit{Preliminary}''',
	# 		fontsize=29
	# 		)
		
	# 	#lumi stuff
	# 	txt = plt.text(
	# 		x_max+(x_max-x_min)*0.07, y_max+3,
	# 		r'35.9 fb$^{\mathsf{-1}}$ (13 TeV)',
	# 		fontsize=29,
	# 		horizontalalignment='right'
	# 		)
		
	# 	ax.tick_params(axis='both', labelsize=29, which='both')
	# 	plt.savefig(
	# 		'limit_%s_2D_%s.pdf' % (parity, style),
	# 		bbox_extra_artists=(txt,), #ensure that the upper text is drawn
	# 		bbox_inches='tight'
	# 	)
	# 	plt.savefig(
	# 		'limit_%s_2D_%s.png' % (parity, style),
	# 		bbox_extra_artists=(txt,), #ensure that the upper text is drawn
	# 		bbox_inches='tight'
	# 	)
	# 	plt.clf()
