#!/usr/bin/env python

"""Plots post-fit nuisances using file with their impacts."""

import json
import os

import numpy as np

import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.offsetbox import TextArea


if __name__ == '__main__':
    
    mpl.rc('axes', labelsize='large')
    mpl.rc('xtick', direction='in') #top=True, 
    mpl.rc('ytick', direction='in')# right=True,
    mpl.rc('xtick.minor') #, visible=True
    mpl.rc('ytick.minor')#, visible=False
    
    figDir = 'fig'
    
    if not os.path.exists(figDir):
        os.makedirs(figDir)
    
    
    # Read fitted nuisances
    fitsLjets, fitsDilep, fitsComb = {}, {}, {}
    
    for fits, fileName in [
        (fitsLjets, 'impacts_ljets.json'),
        (fitsDilep, 'impacts_dilep.json'),
        (fitsComb, 'impacts_comb.json')
    ]:
        fileImpacts = open(fileName)
        
        for p in json.load(fileImpacts)['params']:
            fits[p['name']] = p['fit']
        
        fileImpacts.close()
    
    
    # Define the order and display names for nuisances to be plotted
    names = [
        ('QCDscaleMERenorm_ggA-sgn', '$\\Phi$ (res.) $\\mu_R$'),
        ('QCDscaleMEFactor_ggA-sgn', '$\\Phi$ (res.) $\\mu_F$'),
        ('QCDscaleMERenorm_ggA-int', '$\\Phi$ (int.) $\\mu_R$'),
        ('QCDscaleMEFactor_ggA-int', '$\\Phi$ (int.) $\\mu_F$'),
        ('TTXsec', '$t\\bar{t}$ norm.'),
        ('QCDscaleMERenorm_TT', '$t\\bar{t}$ $\\mu_R$'),
        ('QCDscaleMEFactor_TT', '$t\\bar{t}$ $\\mu_F$'),
        ('QCDscaleFSR_TT', '$t\\bar{t}$ FSR'),
        ('Hdamp_TT', '$t\\bar{t}$ $h_\\mathrm{damp}$'),
        ('CMS_httbar_PDF_1', '$t\\bar{t}$ PDF (1)'),
        ('CMS_httbar_PDF_2', '$t\\bar{t}$ PDF (2)'),
        ('CMS_httbar_PDF_alphaS', '$t\\bar{t}$ PDF $\\alpha_s$'),
        ('CMS_TopPt1_TT', 'top $p_T$ reweighting (1)'),
        ('CMS_TopPt2_TT', 'top $p_T$ reweighting (2)'),
        ('TMass', '$m_t$'),
        ('CMS_httbar_tChannelNorm_13TeV', '$t$, $t$-chan. norm.'),
        ('CMS_httbar_tWChannelNorm_13TeV', '$tW$ norm.'),
        ('CMS_httbar_sChannelNorm_13TeV', '$t$, $s$-chan. norm.'),
        ('CMS_httbar_WNorm_13TeV', '$W$ norm.'),
        ('CMS_httbar_ZNorm_13TeV', 'Drell-Yan norm.'),
        ('CMS_httbar_VVNorm_13TeV', '$VV$ norm.'),
        ('CMS_httbar_TTVNorm_13TeV', '$t\\bar{t}V$ norm.'),
        ('CMS_httbar_QCDmujetsNorm', 'QCD norm. ($\\mu$)'),
        ('CMS_httbar_QCDejetsNorm', 'QCD norm. ($e$)'),
        ('CMS_eff_b_13TeV', '$b$ tag eff.'),
        ('CMS_fake_b_13TeV', '$b$ mistag eff.')
    ]
    
    for jecSyst in [
        'AbsoluteStat', 'AbsoluteScale', 'AbsoluteMPFBias', 'Fragmentation',
        'SinglePionECAL', 'SinglePionHCAL', 'FlavorQCD', 'TimePtEta',
        'RelativeJEREC1', 'RelativePtBB', 'RelativePtEC1', 'RelativeBal', 'RelativeFSR',
        'RelativeStatFSR', 'RelativeStatEC',
        'PileUpDataMC', 'PileUpPtRef', 'PileUpPtBB', 'PileUpPtEC1'
    ]:
        names.append(('CMS_scale_j_13TeV_{}'.format(jecSyst), 'JEC, {}'.format(jecSyst)))
    
    names.extend([
        ('CMS_res_j_13TeV', 'JER'),
        ('CMS_METunclustered_13TeV', 'uncl. missing $p_T$'),
        ('CMS_eff_trigger_m', '$\\mu$ trigger'),
        ('CMS_eff_trigger_e', '$e$ trigger'),
        ('CMS_eff_trigger_l', '$\ell\ell$ triggers'),
        ('CMS_eff_m', '$\\mu$ ID'),
        ('CMS_eff_e', '$e$ ID'),
        ('CMS_pileup', 'pileup'),
        ('lumi', 'luminosity')
    ])
    
    
    fig = plt.figure(figsize=(6, 8))
    axes = fig.add_subplot(111)
    
    labelPadding = 0.30
    axes.set_position([0.05 + labelPadding, 0.05, 0.90 - labelPadding, 0.90])
    
    for i in range(0, len(names), 2):
        axes.axhspan(
            -i - 0.5, -i + 0.5, fc='gray', alpha=0.25
        )
    
    for x in [-1., 0., 1.]:
        axes.axvline(x, ls='dotted', color='gray')
    
    yLabels = [n[1] for n in names]
    
    
    for fits, colour, shift in [
        (fitsLjets, 'green', -0.2), (fitsDilep, 'red', 0.), (fitsComb, 'black', 0.2)
    ]:
        nConstraints = sum(1 for n in names if n[0] in fits.keys())
        
        x, y = np.zeros(nConstraints), np.zeros(nConstraints)
        xErr = np.zeros((2, nConstraints))
        
        i = 0
        
        for iConstraint, n in enumerate(names):
            if n[0] not in fits.keys():
                continue
            
            fit = fits[n[0]]
            
            y[i] = -iConstraint - shift
            x[i] = fit[1]
            xErr[0, i] = fit[1] - fit[0]
            xErr[1, i] = fit[2] - fit[1]
            
            i += 1
        
        axes.errorbar(
            x, y, xerr=xErr,
            ls='none', elinewidth=1, marker='o', ms=1.5, capsize=1.5, color=colour
        )
    
    axes.set_yticks([-i for i in range(len(yLabels))])
    axes.set_yticklabels(yLabels)
    axes.set_ylim(-len(names), 1.)
    
    axes.set_xlabel('Value of nuisance parameter')
    
    legendBoxes = [
        TextArea('$\\ell + \\mathrm{jets}$', textprops={'color': 'green'}),
        TextArea('$\\ell\\ell$', textprops={'color': 'red'}),
        TextArea('comb.', textprops={'color': 'black'})
    ]
    legendPacker = mpl.offsetbox.HPacker(children=legendBoxes, pad=0., sep=10.)
    legendBox = mpl.offsetbox.AnchoredOffsetbox(
            child=legendPacker, frameon=False,
            loc=4, # Means 'lower right'. Strings not supported here.
            bbox_to_anchor=(1., 1.), bbox_transform=axes.transAxes,
            pad=0., borderpad=0.
        )
    axes.add_artist(legendBox)
    
    fig.savefig(os.path.join(figDir, 'constraints.pdf'))
