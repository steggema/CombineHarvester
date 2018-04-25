#! /bin/env python

import pickle
from argparse import ArgumentParser
from pdb import set_trace

parser = ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

with open(args.input) as pkl:
	mapping = pickle.load(pkl)

import ROOT
ROOT.gROOT.SetStyle('Plain')
ROOT.gStyle.SetOptTitle(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)

excluded = {
	"exp+1": [],
	"exp+2": [],
	"exp-1": [],
	"exp-2": [],
	"exp0" : [],
}
failed = []

def make_graph(points):
	gr = ROOT.TGraph(len(points))
	for i, xy in enumerate(points):
		gr.SetPoint(i, xy[0], xy[1])
	return gr

for point, vals in mapping.iteritems():
	_, tb = point
	if not vals or (set(excluded.keys()) - set(vals.keys())) : 
		failed.append(point)
		continue
	for key in excluded:
		if vals[key] < 1/tb: excluded[key].append(point)

print 'Excluded %d points, %d failed' % (len(excluded), len(failed))
g_excluded = make_graph(excluded["exp0"])
g_excluded.SetMarkerColor(4)
g_excluded.SetMarkerStyle(20)
g_failed = make_graph(failed)
g_failed.SetMarkerColor(2)
g_failed.SetMarkerStyle(34)

canvas = ROOT.TCanvas('asd', 'asd', 800, 800)
g_excluded.Draw('AP')
g_failed.Draw('P same')

x_min = min(
	g_excluded.GetXaxis().GetXmin(),
	min(x for x, _ in mapping.iterkeys())
	)
x_max = max(
	max(x for x, _ in mapping.iterkeys())+32,
	g_excluded.GetXaxis().GetXmax()
	)
g_excluded.GetXaxis().SetLimits(x_min, x_max)
y_min = min(x for _, x in mapping.iterkeys())
y_max = max(x for _, x in mapping.iterkeys())*1.2
g_excluded.GetYaxis().SetRangeUser(y_min, y_max)
g_excluded.GetXaxis().SetTitle('m(A)')
g_excluded.GetYaxis().SetTitle('tan #beta')

canvas.SaveAs('summary.png')

#
# Get nicer plot
# Everything is almost completely hardcoded, but 
# actually easier to handle this way, making visible 
# all the internals and working from there.
#

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pickle
plt.rc('text', usetex=True)
plt.rcParams['text.latex.preamble']=[
	r"\usepackage{amsmath}",
]
plt.rcParams["mathtext.default"] = 'regular'
plt.rcParams["mathtext.fontset"] = "stix"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
from pdb import set_trace

x_min = min(x for x, _ in mapping.iterkeys())
x_max = 700 #max(x for x, _ in mapping.iterkeys())
y_min = min(x for _, x in mapping.iterkeys())
y_max = max(x for _, x in mapping.iterkeys())

best_points = {}
xs = sorted(list(set([x for x, _ in mapping.keys()])))
for key in excluded:
    points = excluded[key]
    loc_xs = list(set(i for i, _ in points))
    ys = [max(y for x, y in points if x == i) for i in loc_xs]
    current_points = dict(zip(loc_xs, ys))
    for x in xs:
        if x not in current_points:
            current_points[x] = 0. #default value
    best_points[key] = sorted(current_points.items())

x = lambda vv: [i for i, _ in vv]
y = lambda vv: [i for _, i in vv]

import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.patches as patches

fig = plt.figure(figsize=(10, 10), dpi= 80, facecolor='w', edgecolor='k')
ax = fig.add_subplot(111)
handles = []

obs_color = (103./255., 203./255., 123./255., 0.4)
#version bug, the opacity is not handled in mpatches, therefore we make it lighter
alpha = obs_color[3]
patch_color = [i*alpha+1.*(1-alpha) for i in obs_color]
patch_color[3] = 1.
handles.append(
    (mpatches.Patch(facecolor=tuple(patch_color), edgecolor='k'), r'Observed')
    )

canter = plt.plot(x(best_points['exp0']), y(best_points['exp0']), 'k--')
handles.append(
    (mlines.Line2D([], [], color='k', linestyle='--', linewidth=3), 'Expected')
    )
onescol = '#aeaeae'
twoscol = '#c7c7c7'
twosig = plt.fill_between(xs, y(best_points['exp+2']), y(best_points['exp-2']), color=twoscol)
onesig = plt.fill_between(xs, y(best_points['exp+1']), y(best_points['exp-1']), color=onescol)
handles.append(
    (mpatches.Patch(color=onescol), r'$\mathsf{\pm}$1 s.d.\,expected')
    )
handles.append(
    (mpatches.Patch(color=twoscol), r'$\mathsf{\pm}$2 s.d.\,expected')
    )

#Fake observed, just to check it works
plt.fill_between(
	xs, [0]*len(xs), y(best_points['exp0']), 
	facecolor=obs_color, edgecolor='k', linewidth=1
)

plt.xlabel(	
	r'm$_{\mathrm{\mathsf{A}}}$\, (GeV)', fontsize=32, 
	horizontalalignment='right', x=1.0, 
)
#by hand y label, in pyplot 1.4 it aligns properly, here not
plt.ylabel(
    r'tan$\mathsf{\beta}$', fontsize=32, 
    horizontalalignment='right', 
    y=0.94 #shifts the label down just right
)
plt.xlim((x_min, x_max)) 
plt.ylim((y_min, y_max)) 
ax.xaxis.set_major_formatter(
	ticker.FormatStrFormatter("%d")
	)
ax.yaxis.set_major_formatter(
	ticker.FormatStrFormatter("%d")
	)

delta_y = y_max - y_min
# #rectangle around the legend and the CMS label
# ax.add_patch(
#     patches.Rectangle(
#         (x_min, y_max),   # (x,y)
#         (x_max-x_min),          # width
#         1.35*delta_y/10,          # height
#         clip_on=False,
#         facecolor='w'
#     )
# )

#legend
from matplotlib.font_manager import FontProperties
fontP = FontProperties()
fontP.set_size(32)
legend_x = 0.1
plt.legend(
	x(handles), y(handles),
	bbox_to_anchor=(0.58, 0.93),#, .55, .102), 
	loc=1,
	ncol=2, mode="expand", borderaxespad=0.,
	fontsize=29,
	frameon=False,
	# title=r'\textbf{95\% CL exclusion}:'
)


#CMS blurb
# plt.text(
#     x_min+(x_max-x_min)*0.05, y_max+.2*delta_y/10,
#     r'''\textbf{CMS}
# \textit{Preliminary}''',
#     fontsize=32
#     )
plt.text(
	x_min+(x_max-x_min)*0.01, y_max+0.025*delta_y,
	r'''\textbf{CMS} \textit{Preliminary}''',
	fontsize=32
	)
#legend title (again, due to version)
plt.text(
    x_min+(x_max-x_min)*0.02, y_max-0.06*delta_y,
    r'95\% CL exclusion:',
    fontsize=29,
    # horizontalalignment='left',
    )
#lumi stuff
txt = plt.text(
    x_max-(x_max-x_min)*0.01, y_max+0.025*delta_y,
    r'35.9 fb$^{\mathsf{-1}}$ (13 TeV)',
    fontsize=32,
    horizontalalignment='right'
    )

ax.tick_params(axis='both', labelsize=29, which='both')

#plt.show()
plt.savefig(
	'hmssm_exclusion.pdf',
	bbox_extra_artists=(txt,), #ensure that the upper text is drawn
	bbox_inches='tight'
)
plt.savefig(
	'hmssm_exclusion.png',
	bbox_extra_artists=(txt,), #ensure that the upper text is drawn
	bbox_inches='tight'
)

