#!/usr/bin/env python

"""Applies dummy smoothing to JME variations in signal templates.

Stores in the output file only templates for the given signal
hypothesis.
"""

import argparse
import itertools
import math
import os
import re

import numpy as np

import matplotlib as mpl
mpl.use('agg')
from matplotlib import pyplot as plt

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from CombineHarvester.Httbar.smoothutils import Smoother
from pdb import set_trace

class Reader:
    """Implements reading of signal templates.
    
    Templates are represented by NumPy arrays, whose axes have the
    following meaning: (0) channel, (1) bin in angle, (2) bin in mass,
    (3) histogram bin content versus squared uncertainty.  Input
    templates are expected to be unrolled into 1D.
    """
    
    def __init__(self, src_file, channels, num_bins_angle=5, example='TT', epsilon=-1):
        
        self.src_file = src_file
        self.channels = channels
        
        # Extract number of bins in mass from an example template
        hist = self.src_file.Get(channels[0] + '/' + example) #FIXME!
        self.num_bins_mass = hist.GetNbinsX() // num_bins_angle
        self.num_bins_angle = num_bins_angle
        self.epsilon = epsilon
    
    
    def read_counts(self, name):
        """Read requested templates for all channels."""
        
        counts = np.empty((len(self.channels), self.num_bins_angle, self.num_bins_mass, 2))
        
        for ichannel, channel in enumerate(self.channels):
            read_name = '{}/{}'.format(channel, name)
            template = self.src_file.Get(read_name)
            
            if not template:
                raise RuntimeError('Failed to read template "{}".'.format(read_name))
            
            counts[ichannel] = self._hist_to_array(template)
        
        return counts
    
    
    def _hist_to_array(self, hist):
        """Convert unrolled ROOT histogram into NumPy representation."""
        
        counts_flat = np.empty((hist.GetNbinsX(), 2))
        if self.epsilon == -1:
            self.epsilon = 1.8*(hist.Integral()/hist.GetEntries())

        for i in range(len(counts_flat)):
            if hist.GetBinError(i + 1) == 0 and hist.GetBinContent(i + 1) != 0:
                raise RuntimeError('This will create problems downstream')
            counts_flat[i, 0] = hist.GetBinContent(i + 1) #\
            #if hist.GetBinContent(i + 1) else self.epsilon/10
            counts_flat[i, 1] = hist.GetBinError(i + 1) ** 2 \
               if hist.GetBinError(i + 1) else self.epsilon**2
        
        return counts_flat.reshape(self.num_bins_angle, self.num_bins_mass, 2)


class DummyRebinner:
    
    def __init__(self):
        pass
    
    def __call__(self, array):
        return array


if __name__ == '__main__':
    ROOT.gROOT.SetBatch(True)
    
    arg_parser = argparse.ArgumentParser(__doc__)
    arg_parser.add_argument('input', help='ROOT file with original templates')
    arg_parser.add_argument('point', help='point code A/H:MASS:WIDTH')
    arg_parser.add_argument('badwidth', help='badwith json/dataframe')
    arg_parser.add_argument(
        '-o', '--output', default='smooth_sgn.root',
        help='Name for output ROOT file with smoothed variations in signal'
    )
    arg_parser.add_argument(
        '--fig-dir', default='', help='Directory for plots, if empty, no plots'
    )
    args = arg_parser.parse_args()
    
    parity, mass, width = tuple(args.point.split(':'))    
    width = float(width)
    width_mapping = {
        .1 : '0p1pc',
        1.0 : '1pc ' ,
        2.5 : '2p5pc',
        5.0 : '5pc'  ,
        10. : '10pc' ,
        25. : '25pc' ,
        50. : '50pc' , 
        }

    h_angle = 5 #FIXME
    h_mass  = 5
    sgn_template = 'gg%s_{}-%s-M%s' % (parity, width_mapping[width], mass)
    sgn_name_regex = re.compile(
        sgn_template.format(
            '(pos|neg)-(sgn|int)'
            )
        )
        
    if args.fig_dir:
        try:
            os.makedirs(args.fig_dir)
        except FileExistsError:
            pass
    
    
    sgn_types = {'pos-sgn': '$R$', 'pos-int': '$I^{+}$', 'neg-int': '$I^{-}$'}
    
    # Define variations to be smoothed.  Other templates will be copied
    # to the output file directly
    syst_names = []
    
    for jec_syst in [
        'AbsoluteStat', 'AbsoluteScale', 'AbsoluteMPFBias', 'Fragmentation',
        'SinglePionECAL', 'SinglePionHCAL', 'FlavorQCD', 'TimePtEta',
        'RelativeJEREC1', 'RelativePtBB', 'RelativePtEC1', 'RelativeBal', 'RelativeFSR',
        'RelativeStatFSR', 'RelativeStatEC',
        'PileUpDataMC', 'PileUpPtRef', 'PileUpPtBB', 'PileUpPtEC1'
    ]:
        syst_names.append(('JEC' + jec_syst, 'CMS_scale_j_13TeV_' + jec_syst))
    
    syst_names.append(('JER', 'CMS_res_j_13TeV'))
    syst_names.append(('METUncl', 'CMS_METunclustered_13TeV'))
    
    channel_labels = {
        'mujets': r'$\mu + \mathrm{jets}$', 
        'ejets': r'$e + \mathrm{jets}$', 
        'll' : r'\ell\ell',
        }
    
    
    src_file = ROOT.TFile(args.input)
    out_file = ROOT.TFile(args.output, 'recreate')
    out_dirs = []
    channels = []
    
    templates_to_keep = []
    
    
    # Copy to the output file nominal signal templates and templates for
    # systematic variations that do not need to be smoothed
    for dir_key in src_file.GetListOfKeys():
        if dir_key.GetClassName() != 'TDirectoryFile':
            continue
        
        src_dir = dir_key.ReadObj()
        out_dir = out_file.mkdir(src_dir.GetName())
        channels.append(src_dir.GetName())
        
        for template_key in src_dir.GetListOfKeys():
            name = template_key.GetName()
            
            if not sgn_name_regex.match(name):
                continue
            
            smoothing_needed = False
            
            for _, syst in syst_names:
                if name.endswith('_{}Up'.format(syst)) or name.endswith('_{}Down'.format(syst)):
                    smoothing_needed = True
                    break
            
            if smoothing_needed:
                continue
            
            template = template_key.ReadObj()
            template.SetDirectory(out_dir)
            templates_to_keep.append(template)
        
        out_dirs.append(out_dir)
    
    
    # Proceed to smoothing of requested variations
    reader = Reader(src_file, channels, example=name)
    templates_nominal = {t: reader.read_counts(sgn_template.format(t)) for t in sgn_types}
    
    for syst_display_name, syst_read_name in syst_names:
        print 'smoothing', syst_display_name
        templates_syst = {}
        templates_syst['up'] = {
            t: reader.read_counts('{}_{}Up'.format(sgn_template.format(t), syst_read_name))
            for t in sgn_types
        }
        templates_syst['down'] = {
            t: reader.read_counts('{}_{}Down'.format(sgn_template.format(t), syst_read_name))
            for t in sgn_types
        }
        
        for sgn_type, sgn_type_display in sgn_types.items():
            # Construct smoothed variations
            templates_smooth = {}
            smoother = Smoother(
                templates_nominal[sgn_type],
                templates_syst['up'][sgn_type], templates_syst['down'][sgn_type],
                DummyRebinner(),
                nominalRebinned=templates_nominal[sgn_type],
                upRebinned=templates_syst['up'][sgn_type],
                downRebinned=templates_syst['down'][sgn_type]
            )
            templates_smooth['up'], templates_smooth['down'] = smoother.smooth(
                (h_angle * reader.num_bins_angle, h_mass * reader.num_bins_mass)
            )
            
            # Add smoothed variations to output directory
            for ichannel, direction in itertools.product(range(len(channels)), ['up', 'down']):
                unrolled_template = np.reshape(templates_smooth[direction][ichannel], (-1, 2))
                hist = ROOT.TH1D(
                    '{}_{}{}'.format(
                        sgn_template.format(sgn_type), syst_read_name, direction.capitalize()
                    ),
                    '', reader.num_bins_angle * reader.num_bins_mass,
                    0., reader.num_bins_angle * reader.num_bins_mass
                )
                
                for i in range(len(unrolled_template)):
                    hist.SetBinContent(i + 1, unrolled_template[i, 0])
                    hist.SetBinError(i + 1, math.sqrt(unrolled_template[i, 1]))
                
                hist.SetDirectory(out_dirs[ichannel])
                templates_to_keep.append(hist)
            
            if not args.fig_dir: continue
            # Plot deviations
            for ichannel, direction in itertools.product(range(len(channels)), ['up', 'down']):
                input_deviation = (templates_syst[direction][sgn_type][ichannel, ..., 0]+10**-7) / \
                    (templates_nominal[sgn_type][ichannel, ..., 0]+10**-7) - 1
                smooth_deviation = (templates_smooth[direction][ichannel, ..., 0]+10**-7) / \
                    (templates_nominal[sgn_type][ichannel, ..., 0]+10**-7) - 1

                input_deviation = np.reshape(input_deviation, -1)
                nominal_zeros = (templates_nominal[sgn_type][ichannel, ..., 0] == 0).ravel()
                shifted_zeros = (templates_syst[direction][sgn_type][ichannel, ..., 0] == 0).ravel()
                zero_over_zero, = np.where((nominal_zeros & shifted_zeros))
                infs, = np.where((nominal_zeros & np.invert(shifted_zeros)))
                clipped, = np.where((input_deviation > 3) & np.invert(nominal_zeros & np.invert(shifted_zeros)))
                #clip and set to zero
                input_deviation[input_deviation > 3] = 0
                smooth_deviation = np.reshape(smooth_deviation, -1)
                
                chi2 = np.sum(
                    (
                        templates_smooth[direction][ichannel, ..., 0] - \
                        templates_syst[direction][sgn_type][ichannel, ..., 0]
                    ) ** 2 / templates_nominal[sgn_type][ichannel, ..., 1]
                )
                
                
                fig = plt.figure()
                fig.patch.set_alpha(0.)
                axes = fig.add_subplot(111)
                
                x = np.array(range(len(input_deviation) + 1))
                axes.step(
                    x, list(input_deviation) + [0], where='post',
                    solid_joinstyle='miter', color='black', label='Original'
                )
                axes.step(
                    x, list(smooth_deviation) + [0], where='post',
                    solid_joinstyle='miter', color='r', label='Smoothed'
                )
                axes.plot(
                    zero_over_zero+0.5, np.ones(zero_over_zero.shape[0])*0.05, 'ro', 
                    markersize=4, markeredgewidth=0.0, label='0/0')
                axes.plot(
                    infs+0.5, np.ones(infs.shape[0])*0.05, 'bo', markersize=4, 
                    markeredgewidth=0.0, label='infs'
                    )
                axes.plot(
                    clipped+0.5, np.ones(clipped.shape[0])*0.05, 'go', markersize=4,
                    markeredgewidth=0.0, label='clipped'
                    )

                axes.axhline(0., color='gray', lw=0.8, ls='dashed')
                
                for i in range(reader.num_bins_angle - 1):
                    axes.axvline(
                        len(input_deviation) / reader.num_bins_angle * (i + 1),
                        color='gray', lw=0.8, ls='dashed'
                    )
                
                axes.margins(x=0.)
                axes.legend()
                
                axes.set_xlabel(
                    r'$m_{t\bar t} \otimes \cos\/\theta^*_{\mathrm{t}_\ell}$ bin index'
                )
                axes.set_ylabel('Relative deviation from nominal')
                axes.text(
                    0., 1.003,
                    '{}, {} ({}), {}, $h = ({:g}, {:g})$, $\\chi^2 = {:.2f}$'.format(
                        sgn_type_display, syst_display_name, direction,
                        channel_labels[channels[ichannel]], h_angle, h_mass,
                        chi2
                    ),
                    ha='left', va='bottom', transform=axes.transAxes
                )
                
                fig.savefig(os.path.join(
                    args.fig_dir, '{}_{}_{}_{}.pdf'.format(
                        sgn_type, syst_display_name, channels[ichannel], direction
                    )
                ))
                plt.close(fig)
    
    
    for out_dir in out_dirs:
        out_dir.Write()
    
    out_file.Close()
    src_file.Close()
