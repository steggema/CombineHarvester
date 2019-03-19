#! /bin/env python

# pylint: disable=W0312,C0330

from argparse import ArgumentParser
from pdb import set_trace
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as ticker


matplotlib.use('Agg')
plt.rc('text', usetex=True)
plt.rcParams['text.latex.preamble']=[
    r"\usepackage{amsmath}",
]
plt.rcParams["mathtext.default"] = 'regular'
# plt.rcParams["mathtext.fontset"] = "stix"
plt.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

print 'Run with matplotlib > 2, e.g. by sourcing CMSSW_10_3_X'

parser = ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

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


val2name = lambda x: ('%.1f' % x).replace('.', 'p').replace('p0', '')

def make_plot(subset, xvar):
    subset.sort(order=xvar)
    print subset
    print xvar

    parity = list(set(subset['parity']))[0]

    x_min = subset[xvar].min()
    x_max = subset[xvar].max()    
    y_min = 0.
    y_max = 5.

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
    #     subset[xvar], np.random.normal(scale=0.15, size=len(subset['exp0']))+subset['exp0'], 
    #     color='k', linestyle='-', markersize=10, marker='.'
    #     )


    observed = plt.plot(
        subset[xvar], subset['sig_g'],
        color='black', linestyle='-', linewidth=3#, markersize=10, marker='.'
        )

    handles.append(
        (mlines.Line2D([], [], color='red', linestyle='-'), 'Observed')
        # (mpatches.Patch(color=obs_color), 'Observed')
        # (mpatches.Patch(color=obs_color), mlines.Line2D([], [], color='k', linestyle='None', markersize=10, marker='.')), 'Observed')
        )
    
    # center = plt.plot(subset[xvar], subset['exp0'], color='blue', linestyle='-')
    # handles.append(
    #     (mlines.Line2D([], [], color='blue', linestyle='-'), 'Expected')
    #     )
    # twosig = plt.fill_between(subset[xvar], subset['exp-2'], subset['exp+2'], color=twosigma)

    # handles.append(
    #     # (mpatches.Patch(color=twosigma), r'$\mathsf{\pm}$2\,s.d.\ expected')
    #     # )
    #     (mpatches.Patch(color=twosigma), r'95\% expected')
    #     )
    # onesig = plt.fill_between(subset[xvar], subset['exp+1'], subset['exp-1'], color=onesigma)
    # handles.append(
    #     # (mpatches.Patch(color=onesigma), r'$\mathsf{\pm}$1\,s.d.\ expected')
    #     # )
    #     (mpatches.Patch(color=onesigma), r'68\% expected')
    #     )


    #version bug, the opacity is not handled in mpatches, therefore we make it lighter
    # alpha = obs_color[3]
    # patch_color = [i*alpha+1.*(1-alpha) for i in obs_color]
    # patch_color[3] = 1.
    # upper_contour =  np.array([val if val < 3. else y_leg_cutoff for val in subset['obslower']])
    # observed_contour = plt.fill_between(subset[xvar], subset['obs'], upper_contour, color=obs_color)
    # observed_contour = plt.fill_between(subset[xvar], subset['obsupper'], [y_leg_cutoff for n in xrange(len(subset['obsupper']))], color=obs_color)
    # # observed_contour = plt.fill_between(subset[xvar], subset['obslower'], subset['obsupper'], color=obs_color)
    # lower_to_draw =  np.array([val if val < 3. else np.nan for val in subset['obslower']])
    # observed_lower = plt.plot(
    #     subset[xvar], lower_to_draw, 
    #     color='k', linestyle='None'#, markersize=10, marker='.'
    #     )
    # observed_upper = plt.plot(
    #     subset[xvar], subset['obsupper'], 
    #     color='k', linestyle='None'#, markersize=10, marker='.'
    #     )
    
    legend_border = plt.plot([x_min, x_max], [3., 3.], color='k', linestyle='dotted', linewidth=2)

    plt.xlabel(    
        xlabels[xvar] % parity, fontsize=32, 
        horizontalalignment='right', x=1.0, 
    )
    #by hand y label, in pyplot 1.4 it aligns properly, here not
    plt.ylabel(
        r'Local significance', fontsize=32, 
        horizontalalignment='right', 
        y=0.95 #shifts the label down just right
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
    # legend.set_title(title='Significances', prop=fontP)
    #legend title (again, due to version)
    other_var = list(set(subset[vartoadd[xvar]]))[0]
    ret.append(
        plt.text(
        # x_min+(x_max-x_min)*0.50, y_max-delta_y*.27,
        x_min+(x_max-x_min)*0.50, y_max-delta_y*.05,
            addenda[xvar] % ((parity, other_var) if xvar == 'width' else (parity, parity, other_var) ),
             # +r'\textbf{95\% CL Excluded}:',
        fontsize=29,
        horizontalalignment='left'
        )
        )
    
    #CMS blurb
    plt.text(
        x_min+(x_max-x_min)*0.00, y_max+0.025*delta_y,
        # r'''\textbf{CMS} \textit{Preliminary}''',
        r'''\textbf{CMS}''',
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

        ensure_drawn = make_plot(subset, 'mass')

        wname = val2name(width)
        plt.savefig(
            'sig_%s_%s.pdf' % (parity, wname),
            bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
            bbox_inches='tight'
        )
        plt.savefig(
            'sig_%s_%s.png' % (parity, wname),
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

        ensure_drawn = make_plot(subset, 'width')

        plt.savefig(
            'sig_%s_M%s.pdf' % (parity, mass),
            # bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
            bbox_inches='tight'
        )
        plt.savefig(
            'sig_%s_M%s.png' % (parity, mass),
            # bbox_extra_artists=ensure_drawn, #ensure that the upper text is drawn
            bbox_inches='tight'
        )
        plt.clf()

    for style in ['sig_g']:
        #
        #  2D color plots    
        #
        subset = limits[limits['parity'] == parity]
        subset.sort(order=('width', 'mass'))
        
        x_min = subset['mass'].min() - 12.5
        x_max = subset['mass'].max() + 12.5
        y_min = subset['width'].min() #FIXME: add observed
        y_max = subset['width'].max()
        
        fig = plt.figure(figsize=(10, 10), dpi= 80, facecolor='w', edgecolor='k')
        ax = fig.add_subplot(111)
        ax.xaxis.set_major_formatter(
            ticker.FormatStrFormatter("%d")
            )
        #hardcoded
        all_masses = np.array(masses+[775.])-12.5#/2
        all_widths = [0.075]+[(widths[i]+widths[i-1])/2 for i in range(1, len(widths))]+[100]
        X,Y = np.meshgrid(all_masses, all_widths)

        Z = subset[style].reshape((len(widths), len(masses)))
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
            vmin=subset[style].min()*0.2, 
            vmax=subset[style].max()*1.2
            )
        #plt.xticks(masses)
        ax.set_yscale('log')
        ax.set_yticks(widths)
        ax.yaxis.set_major_formatter(
            ticker.FormatStrFormatter("%.1f")
            )

        cbar = plt.colorbar(heatmap, format=ticker.FormatStrFormatter("%.1f"))
        # cbar.ax.set_ylabel('95\% CL limit on coupling modifier')
        cbar.set_label('Local significance (in s.d.)', size=29)
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
        #     x_min+(x_max-x_min)*(legend_x+0.01), y_max+40,
        #     r'\textbf{95\% CL Excluded}',
        #     fontsize=32,
        #     horizontalalignment='left'
        #     )
        
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
            'sig_%s_2D_%s.pdf' % (parity, style),
            bbox_extra_artists=(txt,), #ensure that the upper text is drawn
            bbox_inches='tight'
        )
        plt.savefig(
            'sig_%s_2D_%s.png' % (parity, style),
            bbox_extra_artists=(txt,), #ensure that the upper text is drawn
            bbox_inches='tight'
        )
        plt.clf()
