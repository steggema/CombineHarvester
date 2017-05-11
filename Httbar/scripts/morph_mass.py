#!/usr/bin/env python
from argparse import ArgumentParser
from numpy import array

import ROOT

from ROOT import RooFit, TVectorD
from ROOT import RooDataHist, RooArgSet, RooArgList, RooMomentMorph, RooHistPdf

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('--hyperbolic', action='store_true', help='use hyperbolic interpolation')
parser.add_argument('--algo', default='Linear', help="Choose morphing algo from 'Linear', 'NonLinear', 'NonLinearPosFractions', 'NonLinearLinFractions', 'SineLinear'")
parser.add_argument('--input_masses', default='400,500,600,750', help='comma separated list of masses')
parser.add_argument('--widths', default='2p5,5,10,25,50', help='comma separated list of widths')
parser.add_argument('--stepsize', default='50')

# FIXME - get these from some clever algorithm, not by hand...
unc_names_mu = ['', '_CMS_eff_mUp', '_CMS_eff_mDown', '_CMS_pileupUp', '_CMS_pileupDown', '_CMS_eff_b_13TeVUp', '_CMS_eff_b_13TeVDown', '_CMS_fake_b_13TeVUp', '_CMS_fake_b_13TeVDown', '_CMS_scale_j_13TeVUp', '_CMS_scale_j_13TeVDown', '_CMS_res_j_13TeVUp', '_CMS_res_j_13TeVDown', '_CMS_METunclustered_13TeVUp', '_CMS_METunclustered_13TeVDown']
unc_names_ele = ['', '_CMS_eff_eUp', '_CMS_eff_eDown', '_CMS_pileupUp', '_CMS_pileupDown', '_CMS_eff_b_13TeVUp', '_CMS_eff_b_13TeVDown', '_CMS_fake_b_13TeVUp', '_CMS_fake_b_13TeVDown', '_CMS_scale_j_13TeVUp', '_CMS_scale_j_13TeVDown', '_CMS_res_j_13TeVUp', '_CMS_res_j_13TeVDown', '_CMS_METunclustered_13TeVUp', '_CMS_METunclustered_13TeVDown']

args = parser.parse_args()

output_binning = [250.0, 360.0, 380.0, 400.0, 420.0, 440.0, 460.0, 480.0, 500.0, 520.0, 540.0, 560.0, 580.0, 610.0, 640.0, 680.0, 730.0, 800.0, 920.0, 1200.0]

available = sorted([int(m) for m in args.input_masses.split(',')])
stepsize = int(args.stepsize)
to_make = [min(available) + (i + 1)*stepsize for i in xrange((max(available)-min(available))/stepsize)]
to_make = [m for m in to_make if m not in available]
print 'Output masses:', to_make

widths = args.widths.split(',')

outname = args.inputfile.replace('.root', '_morphed_mass.root')
# shutil.copyfile(args.inputfile, outname)
infile = ROOT.TFile(args.inputfile)
outfile = ROOT.TFile(outname, 'RECREATE')

# m_ttbar = ROOT.RooRealVar('mass', 'mass', 0., 100.)
m_ttbar = ROOT.RooRealVar('mass', 'mass', 250., 1200.) # FIXME - get these from the input histograms
m_A = ROOT.RooRealVar('m_A', 'm_A', float(min(available)), float(max(available)))

def interpolate(masses, yields, test_mass, linear=True):
	if not linear:
		g = ROOT.TGraph(len(masses), array([float(m) for m in masses]), array(yields))
		# import pdb; pdb.set_trace()
		return g.Eval(float(test_mass), 0)

	from bisect import bisect_left, bisect_right
	try:
		i_low = bisect_left(masses, test_mass) - 1
		i_high = bisect_right(masses, test_mass)
		m_below = masses[i_low]
		m_above = masses[i_high]
		y_below = yields[i_low]
		y_above = yields[i_high]
		if i_low == i_high:
			import pdb; pdb.set_trace()
	except:
		import pdb; pdb.set_trace()

	delta_m = float(m_above - m_below)
	f_low = (test_mass - m_below)/delta_m
	f_high = (m_above - test_mass)/delta_m
	return f_low*y_below + f_high*y_above
	


for channel in [i.GetName() for i in infile.GetListOfKeys()]:
	tdir = infile.Get(channel)
	tdir.cd()
	outfile.mkdir(channel)
	for pattern in ['neg-int', 'pos-int', 'pos-sgn']:
		for width in widths:
			unc_names = unc_names_ele if channel == 'ejets' else unc_names_mu
			for unc_name in unc_names:

				pdfs = RooArgList()
				keeper = []
				vd = TVectorD(len(available))
				yields = []
				for i_m, mass in enumerate(available):
					h_ori = infile.Get('{channel}/ggA_{pattern}-{width}pc-M{mass}{unc_name}'.format(channel=channel, pattern=pattern, width=width, mass=mass, unc_name=unc_name))
					yields.append(h_ori.Integral())
					# print '{channel}/ggA_{pattern}-{width}pc-M{mass}{unc_name}'.format(channel=channel, pattern=pattern, width=width, mass=mass, unc_name=unc_name)
					h_ori.Scale(1./h_ori.Integral())
					data_hist = RooDataHist('m'+h_ori.GetName(), '', RooArgList(m_ttbar), h_ori, 1.)
					pdf = RooHistPdf('pdf_m'+h_ori.GetName(), '', RooArgSet(m_ttbar), data_hist)
					pdfs.add(pdf)
					vd[i_m] = float(mass)
					keeper.append(pdf)
					keeper.append(data_hist)

				setting = getattr(ROOT.RooMomentMorph, args.algo)
				morph = RooMomentMorph('morph'+channel+pattern, '', m_A, RooArgList(m_ttbar), pdfs, vd, setting)
				# morph.Print('v')
				
				for test_mass in to_make:
					m_A.setVal(float(test_mass))

					h_morph = h_ori.Clone('MORPH'+h_ori.GetName().replace(str(available[-1]), str(test_mass)))

					for i_bin in xrange(h_ori.GetNbinsX()):
						x = h_ori.GetBinCenter(i_bin+1)
						# print 'mttbar = ', x
						m_ttbar.setVal(x)

						# for i_pdf in xrange(len(pdfs)):
						# 	print pdfs[i_pdf].getVal()

						h_morph.SetBinContent(i_bin+1, morph.getVal()*h_ori.GetBinWidth(i_bin+1))
					h_morph_rebin = h_morph.Rebin(len(output_binning)-1, h_morph.GetName().replace('MORPH', ''), array(output_binning))
					outfile.cd()
					outdir = outfile.Get(channel)
					outdir.cd()

					scale = interpolate(available, yields, test_mass)
					h_morph_rebin.Scale(scale/h_morph_rebin.Integral())
					h_morph_rebin.Write()
