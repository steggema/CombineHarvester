#! /bin/env python

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

parser = ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

xlabels = {
	'mass' : r'm$_{\mathrm{\mathsf{%s}}}$\, (GeV)',
	'width': r'width$_{\mathrm{\mathsf{%s}}}$\, (\%%)',
	}

addenda = {
	# 'width': r'\textbf{m}$\boldsymbol{_{\mathrm{\mathsf{%s}}} \mathsf{= %d}}$\textbf{\, GeV }',
	# 'mass' : r'\textbf{width}$\boldsymbol{_{\mathrm{\mathsf{%s}}} \mathsf{= %.1f}}$\textbf{\%% }',
	'width': r'm$_{\mathrm{\mathsf{%s}}}$ = {%d}\,GeV',
	# 'mass' : r'Width$_{\mathrm{\mathsf{%s}} \mathsf{= %.1f}}$\%%',
	'mass' : r'$\Gamma$/m$_{\mathrm\mathsf{{%s}}}$ = {%.1f}\%%',
	}

vartoadd = {
	'width' : 'mass',
	'mass' : 'width'
}
val2name = lambda x: ('%.1f' % x).replace('.','p').replace('p0','')

def make_plot(subset, xvar):
		subset.sort(order=xvar)
		print subset
		print xvar
		x_min = subset[xvar].min()
		x_max = subset[xvar].max()	
		y_min = subset['exp-2'].min()*0.8 #FIXME: add observed
		y_max = subset['exp+2'].max()*1.2
		
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
		# 	subset[xvar], np.random.normal(scale=0.15, size=len(subset['exp0']))+subset['exp0'], 
		# 	color='k', linestyle='-', markersize=10, marker='.'
		# 	)
		observed = plt.plot(
			subset[xvar], subset['obs'], 
			color='k', linestyle='-', markersize=10, marker='.'
			)

		handles.append(
		    (mlines.Line2D([], [], color='k', linestyle='-', markersize=10, marker='.'), 'Observed')
		    )
		
		center = plt.plot(subset[xvar], subset['exp0'], color=line, linestyle='-')
		handles.append(
		    (mlines.Line2D([], [], color=line, linestyle='-'), 'Expected')
		    )
		
		twosig = plt.fill_between(subset[xvar], subset['exp-2'], subset['exp+2'], color=twosigma)
		handles.append(
		    (mpatches.Patch(color=twosigma), r'$\mathsf{\pm}$2\,s.d.\ expected')
		    )
		onesig = plt.fill_between(subset[xvar], subset['exp+1'], subset['exp-1'], color=onesigma)
		handles.append(
		    (mpatches.Patch(color=onesigma), r'$\mathsf{\pm}$1\,s.d.\ expected')
		    )
		
		#Fake observed, just to check it works
		## plt.fill_between(
		## 	xs, [0]*len(xs), [8, 6, 5, 4.3, 3.5, 3, 2, 1.5], 
		## 	facecolor=obs_color, edgecolor='k', linewidth=1
		## )
		parity = list(set(subset['parity']))[0]
		plt.xlabel(	
			xlabels[xvar] % parity, fontsize=32, 
			horizontalalignment='right', x=1.0, 
		)
		#by hand y label, in pyplot 1.4 it aligns properly, here not
		plt.ylabel(
		    r'95\% C.L. limit on coupling modifier', fontsize=32, 
		    horizontalalignment='right', 
		    y=0.9 #shifts the label down just right
		)
		plt.xlim((x_min, x_max)) 
		plt.ylim((y_min, y_max)) 
		
		delta_y = y_max - y_min
		#rectangle around the legend and the CMS label
		# ax.add_patch(
		#     patches.Rectangle(
		#         (x_min, y_max),   # (x,y)
		#         (x_max-x_min),          # width
		#         1.35*delta_y/10,          # height
		#         clip_on=False,
		#         facecolor='w'
		#     )
		# )
		
		ret = []
		#legend
		# fontP = FontProperties()
		# fontP.set_size('x-large')
		legend_x = 0.43
		plt.legend(
			x(handles), y(handles),
			# bbox_to_anchor=(legend_x, 1., .55, .102), 
			loc=1,
			ncol=2, mode="expand", borderaxespad=0.,
			fontsize=29,
			frameon=False,
		)
		#legend title (again, due to version)
		other_var = list(set(subset[vartoadd[xvar]]))[0]
		ret.append(
			plt.text(
		    x_min+(x_max-x_min)*0.03, y_max-delta_y*.23,
				addenda[xvar] % (parity, other_var),
				 # +r'\textbf{95\% CL Excluded}:',
		    fontsize=32,
		    horizontalalignment='left'
		    )
			)
		
		#CMS blurb
		plt.text(
		    x_min+(x_max-x_min)*0.03, y_max+0.025*delta_y,
		    r'''\textbf{CMS} \textit{Preliminary}''',
		    fontsize=32
		    )
		
		#lumi stuff
		ret.append(
			plt.text(
		    x_max-(x_max-x_min)*0.01, y_max+0.025*delta_y,
		    r'35.9 fb$^{\mathsf{-1}}$ (13 TeV)',
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

		ensure_drawn = make_plot(subset, 'mass')
	
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

		ensure_drawn = make_plot(subset, 'width')
	
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
	
	#
	#  2D color plots	
	#
	subset = limits[limits['parity'] == parity]
	subset.sort(order=('width', 'mass'))
	
	x_min = subset['mass'].min() - 25.
	x_max = subset['mass'].max() + 25.
	y_min = subset['width'].min() #FIXME: add observed
	y_max = subset['width'].max()
	
	fig = plt.figure(figsize=(10, 10), dpi= 80, facecolor='w', edgecolor='k')
	ax = fig.add_subplot(111)
	ax.xaxis.set_major_formatter(
		ticker.FormatStrFormatter("%d")
		)
	#hardcoded
	all_masses = np.array(masses+[800.])-25.#/2
	all_widths = [0.075]+[(widths[i]+widths[i-1])/2 for i in range(1, len(widths))]+[100]
	X,Y = np.meshgrid(all_masses, all_widths)
	
	Z = subset['exp0'].reshape((len(widths), len(masses)))
	#add one row/column
	Z = np.hstack((
			np.vstack((
					Z, 100*np.ones((1, Z.shape[1]))
					)), 
			100*np.ones((X.shape[0], 1))
			))
	
	heatmap = plt.pcolormesh(
		X, Y, Z,
		# cmap=plt.cm.Greens,
		cmap=plt.cm.YlGnBu,
		vmin=subset['exp0'].min()*0.2, 
		vmax=subset['exp0'].max()*1.2
		)
	#plt.xticks(masses)
	ax.set_yscale('log')
	ax.set_yticks(widths)
	ax.yaxis.set_major_formatter(
		ticker.FormatStrFormatter("%.1f")
		)

	cbar = plt.colorbar(heatmap, format=ticker.FormatStrFormatter("%.1f"))
	# cbar.ax.set_ylabel('95\% CL limit on coupling modifier')
	cbar.set_label('95\% CL limit on coupling modifier', size=29)
	cbar.ax.tick_params(labelsize=29)

	plt.xlabel(	
		xlabels['mass'] % parity, fontsize=32, 
		horizontalalignment='right', x=1.0, 
	)
	#by hand y label, in pyplot 1.4 it aligns properly, here not
	plt.ylabel(
		xlabels['width'] % parity, fontsize=32, 
		horizontalalignment='right', 
		y=0.85 #shifts the label down just right
	)
	plt.xlim((x_min, x_max)) 
	plt.ylim((y_min, y_max)) 
	
	delta_y = y_max - y_min
	# #rectangle around the legend and the CMS label
	# ax.add_patch(
	#     patches.Rectangle(
	#         (x_min, y_max),   # (x,y)
	#         (x_max-x_min),          # width
	#         60,          # height
	#         clip_on=False,
	#         facecolor='w'
	#     )
	# )
	
	# #legend title (again, due to version)
	# legend_x = 0.45
	# text = plt.text(
	# 	x_min+(x_max-x_min)*(legend_x+0.01), y_max+40,
	# 	r'\textbf{95\% CL Excluded}',
	# 	fontsize=32,
	# 	horizontalalignment='left'
	# 	)
	
	#CMS blurb
	plt.text(
		x_min+(x_max-x_min)*0.01, y_max+3,
		r'''\textbf{CMS} \textit{Preliminary}''',
		fontsize=29
		)
	
	#lumi stuff
	txt = plt.text(
		x_max+(x_max-x_min)*0.07, y_max+3,
		r'35.9 fb$^{\mathsf{-1}}$ (13 TeV)',
		fontsize=29,
		horizontalalignment='right'
		)
	
	ax.tick_params(axis='both', labelsize=29, which='both')
	plt.savefig(
		'limit_%s_2D.pdf' % (parity,),
		bbox_extra_artists=(txt,), #ensure that the upper text is drawn
		bbox_inches='tight'
	)
	plt.savefig(
		'limit_%s_2D.png' % (parity,),
		bbox_extra_artists=(txt,), #ensure that the upper text is drawn
		bbox_inches='tight'
	)
	plt.clf()

