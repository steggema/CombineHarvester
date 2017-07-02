#!/usr/bin/env python
from timeit import default_timer as timer

from os import path
from argparse import ArgumentParser
from numpy import array

import ROOT

from ROOT import TVectorD
from ROOT import RooDataHist, RooArgSet, RooArgList, RooMomentMorph, RooHistPdf
from pdb import set_trace

ROOT.TH1.AddDirectory(False)

ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('--hyperbolic', action='store_true',
                    help='use hyperbolic interpolation')
parser.add_argument('--algo', default='NonLinearPosFractions',
                    help="Choose morphing algo from 'Linear', 'NonLinear', 'NonLinearPosFractions', 'NonLinearLinFractions', 'SineLinear'")
parser.add_argument('--input_masses', default='400,500,600,750',
                    help='comma separated list of masses')
parser.add_argument('--widths', default='2p5,5,10,25,50',
                    help='comma separated list of widths')
parser.add_argument('--stepsize', default='50')
parser.add_argument('--interpolate', default='True')

args = parser.parse_args()

# ALL THE DANGEROUS CONSTANTS IN ONE PLACE
OUTPUT_BINNING = [300.0, 340.0, 360.0, 380.0, 400.0, 420.0, 440.0, 460.0, 480.0, 500.0, 520.0, 540.0, 560.0, 580.0, 600.0, 625.0, 650.0, 675.0, 700.0, 730.0, 760.0, 800.0, 850.0, 900.0, 1000.0, 1200.0]
N_REGIONS = 5
MIN_MASS = 300.0
MAX_MASS = 1200.0

# Yield interpolation by hand (true) or via RooMorph (false)
do_interpolate = False if not args.interpolate or args.interpolate=='False' else True

available = sorted([int(m) for m in args.input_masses.split(',')])
stepsize = int(args.stepsize)
to_make = [min(available) + (i + 1) *
           stepsize for i in xrange((max(available) - min(available)) / stepsize)]
to_make = [m for m in to_make if m not in available]
print 'Output masses:', to_make

widths = args.widths.split(',')
# widths = ['5', '10', '25', '50']

outname = args.inputfile.replace('.root', '_morphed_mass.root')
# shutil.copyfile(args.inputfile, outname)
infile = ROOT.TFile(args.inputfile)
outfile = ROOT.TFile(outname, 'RECREATE')

m_ttbar = ROOT.RooRealVar('mass', 'mass', MIN_MASS, MAX_MASS)
m_A = ROOT.RooRealVar('m_A', 'm_A', float(
    min(available)), float(max(available)))

# Get mass interpolation from Viola's file
file_int = ROOT.TFile(path.expandvars(
    '$CMSSW_BASE/src/CombineHarvester/Httbar/data/Spin0_xsecs_vs_mass.root'))
file_int_int = ROOT.TFile(path.expandvars(
    '$CMSSW_BASE/src/CombineHarvester/Httbar/data/Spin0_SEweight_and_NegEvtsFrac_vs_mass.root'))
# pattern_translator = {'pos-sgn':'res', 'pos-int':'int'}


def interpolate(masses, yields, test_mass, linear=True):
    if not linear:
        g = ROOT.TGraph(len(masses), array(
            [float(m) for m in masses]), array(yields))
        # import pdb; pdb.set_trace()
        return g.Eval(float(test_mass), 0)

    from bisect import bisect_left, bisect_right

    i_low = bisect_left(masses, test_mass) - 1
    i_high = bisect_right(masses, test_mass)
    m_below = masses[i_low]
    m_above = masses[i_high]
    y_below = yields[i_low]
    y_above = yields[i_high]
    if i_low == i_high:
        import pdb
        pdb.set_trace()

    delta_m = float(m_above - m_below)
    f_low = (test_mass - m_below) / delta_m
    f_high = (m_above - test_mass) / delta_m
    return f_low * y_below + f_high * y_above


for channel in [i.GetName() for i in infile.GetListOfKeys()]:
    tdir = infile.Get(channel)
    tdir.cd()
    outfile.mkdir(channel)
    h_names = set([key.GetName().replace('400', '{MASS}').replace('500', '{MASS}').replace('600', '{MASS}').replace('750', '{MASS}') for key in tdir.GetListOfKeys()])		
    #h_names = [i for i in h_names if not (i.endswith('Up') or i.endswith('Down'))] #FIXME
    print 'Processing', len(h_names), 'different signal templates'
    for h_name in h_names: # it's not very nice - somehow need to make sure we extract all the histogram name but the mass
        start = timer()
        pattern = h_name[4:11]
        width = [w for w in widths if w+'pc' in h_name]
        width = max(width, key=len) # e.g. for '2p5pc' and '5pc'
        if not width:
            print 'Did not find width in histogram name', h_name
            import pdb; pdb.set_trace()
            continue

        if 'ggH' in h_name:
            # print 'FIXME - no ggH for the moment in the other signal files, continue'
            continue

        g_int = None
        g_int_neg_frac = None
        if pattern == 'pos-sgn':
            g_int = file_int.Get('A_res_semilep_w{}_toterr'.format(width))

        if pattern in ['pos-int', 'neg-int']:
            g_int = file_int_int.Get('A_int_semilep_w{}_SEweight'.format(width))
            g_int_neg_frac = file_int_int.Get('A_int_semilep_w{}_NegEvts_Frac'.format(width))
            # print pattern
            # for m in [400., 450., 500., 600., 700.]:
            #     print m, g_int.Eval(m) * g_int_neg_frac.Eval(m)
            #     print m, g_int.Eval(m) * (1. - g_int_neg_frac.Eval(m))

        if not g_int:
            import pdb; pdb.set_trace()

        mass_hists = {}
        mass_scales = {}
        # First get the histograms for all masses

        print '\n Processing:', h_name

        tmp_file = ROOT.TFile('_tmp.root', 'RECREATE')

        for mass in available:
            # print 'MASS', mass
            #print '{channel}/{h_name}'.format(
            #    channel=channel, h_name=h_name).format(MASS=mass)
            h_ori = infile.Get('{channel}/{h_name}'.format(
                channel=channel, h_name=h_name).format(MASS=mass)).Clone(
							h_name.format(MASS=mass)
							)
            #print 'MASS', mass, h_ori.GetName()

            scale = 1. / g_int.Eval(mass)
            h_ori.Scale(1. / g_int.Eval(mass))

            if pattern == 'pos-int':
                scale *= 1. / (1. - g_int_neg_frac.Eval(mass))
                h_ori.Scale(1. / (1. - g_int_neg_frac.Eval(mass)))

            if pattern == 'neg-int':
                scale *= 1. / g_int_neg_frac.Eval(mass)
                h_ori.Scale(1. / g_int_neg_frac.Eval(mass))
            # yields.append(h_ori.Integral())

            mass_scales[mass] = scale
            mass_hists[mass] = h_ori

        d_hists_region = {}

        eval_time = 0.
        create_time = 0.

        #set_trace()
        # Split input histogram
        # I DONT WANT TO DO THAT BUT OK
        if mass_hists[available[0]].GetNbinsY() != N_REGIONS:
            raise RuntimeError(
							'the histogram %s has only %d y bins instead of %d expected' % \
								(h_ori.GetName(), h_ori.GetNbinsY(), N_REGIONS)
							)
        for i_costheta in xrange(N_REGIONS):
            d_hists_region[i_costheta] = {}
            pdfs = RooArgList()
            keeper = []
            vd = TVectorD(len(available))
            yields = []
            for i_m, mass in enumerate(available):
                h_all = mass_hists[mass]
                tmp_file.cd()
                h_region = h_all.ProjectionX(
									channel+h_all.GetName()+str(i_costheta)+"_finebinning",
									i_costheta+1, i_costheta+1
									)
                d_hists_region[i_costheta][mass] = h_region.Rebin(
									len(OUTPUT_BINNING) - 1, 
									h_region.GetName().replace('_finebinning', ''), 
									array(OUTPUT_BINNING)
									)
                d_hists_region[i_costheta][mass].Scale(1./mass_scales[mass])
                yields.append(h_region.Integral())

                # if pattern == 'neg-int':
                # 	h_ori.Scale(-1.)
                #set_trace()
                data_hist = RooDataHist(
                    'm' + h_region.GetName().replace('_finebinning', ''), 
										'', RooArgList(m_ttbar), h_region, 1.
										)
                pdf = RooHistPdf(
									'pdf_m' + h_region.GetName().replace('_finebinning', ''),
									'', RooArgSet(m_ttbar), data_hist
									)
                pdfs.add(pdf)
                vd[i_m] = float(mass)
                keeper.append(pdf)
                keeper.append(data_hist)
                keeper.append(h_region)

            setting = getattr(ROOT.RooMomentMorph, args.algo)
            morph = RooMomentMorph(
                'morph' + channel + h_name.format(MASS='000'), '', m_A, RooArgList(m_ttbar), pdfs, vd, setting)
            # morph.Print('v')

            # print 'Yields', i_costheta, pattern, yields
            for test_mass in to_make:
                m_A.setVal(float(test_mass))
                tmp_file.cd()
                #set_trace()
                h_morph_region = h_region.Clone(
                    'MORPH' + h_region.GetName().replace('_finebinning', '').replace(str(available[-1]), str(test_mass)))

                for i_bin in xrange(h_morph_region.GetNbinsX()):

                    x = h_morph_region.GetBinCenter(i_bin + 1)
                    # print 'mttbar = ', x
                    m_ttbar.setVal(x)

                    # for i_pdf in xrange(len(pdfs)):
                    # 	print pdfs[i_pdf].getVal()
                    # print 'Morphed val:', morph.getVal()

                    h_morph_region.SetBinContent(
                        i_bin + 1, morph.getVal() * h_morph_region.GetBinWidth(i_bin + 1))
                
                h_morph_region_rebin = h_morph_region.Rebin(len(
                    OUTPUT_BINNING) - 1, h_morph_region.GetName().replace('MORPH', ''), array(OUTPUT_BINNING))

                if do_interpolate:
                    scale = interpolate(available, yields, test_mass)
                    if scale == 0.:
                        import pdb; pdb.set_trace()

                    h_morph_region_rebin.Scale(
                        scale / h_morph_region_rebin.Integral())
                
                h_morph_region_rebin.Scale(g_int.Eval(test_mass))
                if pattern == 'pos-int':
                    h_morph_region_rebin.Scale(1. - g_int_neg_frac.Eval(test_mass))
                if pattern == 'neg-int':
                    h_morph_region_rebin.Scale(g_int_neg_frac.Eval(test_mass))

                d_hists_region[i_costheta][test_mass] = h_morph_region_rebin
                del h_morph_region # Save execution time (->ROOT)
            # Delete items as execution time grows extremely otherwise
            for item in keeper:
                del item
        
        # Now collate the hists from the different regions for all masses, including the available
        for test_mass in to_make+available:
            n_bins_out = N_REGIONS*(len(OUTPUT_BINNING) - 1)
            outfile.cd()
            outdir = outfile.Get(channel)
            outdir.cd()
            h_out = ROOT.TH1D(d_hists_region[0][test_mass].GetName()[:-1].replace(channel, ''), '', n_bins_out, 0., float(n_bins_out))

            for i_costheta in xrange(N_REGIONS):
                h_part = d_hists_region[i_costheta][test_mass]
                n_bins_part = h_part.GetNbinsX()
                for i_bin in xrange(n_bins_part):
                    h_out.SetBinContent(i_bin+1 + i_costheta*n_bins_part, h_part.GetBinContent(i_bin+1))
                    h_out.SetBinError(i_bin+1, 0.)
            h_out.Write()
            # print 'Writing', test_mass, h_out.Integral()

        tmp_file.Close()
        print 'Time elapsed:', timer() - start
    outfile.Write()
