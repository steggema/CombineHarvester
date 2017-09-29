import ROOT
from ROOT import TFile, TCanvas, TVectorD

from ROOT import RooFit
from ROOT import RooDataHist, RooArgSet, RooArgList, RooMomentMorph, RooHistPdf

f_ori = TFile('../data/templates2D_240317.root')

width = '5'

# m_ttbar = ROOT.RooRealVar('mass', 'mass', 250., 1200.)
m_ttbar = ROOT.RooRealVar('mass', 'mass', 0., 100.)
m_A = ROOT.RooRealVar('m_A', 'm_A', 400., 750.)

test_mass = '500'
other_masses = ['400', '600', '750']

# test_mass = '600'
# other_masses = ['400', '500', '750']

cv = TCanvas()
for channel in ['ejets', 'mujets']:
	for pattern in ['neg-int', 'pos-int', 'pos-sgn']:
		for algo in ['Linear', 'NonLinear', 'NonLinearPosFractions', 'NonLinearLinFractions', 'SineLinear']:

			pdfs = RooArgList()
			keeper = []
			vd = TVectorD(len(other_masses))
			for i_m, mass in enumerate(other_masses):
				h_ori = f_ori.Get('{channel}/ggA_{pattern}-{width}pc-M{mass}'.format(channel=channel, pattern=pattern, width=width, mass=mass))
				# h_ori.Scale(1./h_ori.Integral())
				data_hist = RooDataHist('m'+h_ori.GetName(), '', RooArgList(m_ttbar), h_ori, 1.)
				pdf = RooHistPdf('pdf_m'+h_ori.GetName(), '', RooArgSet(m_ttbar), data_hist)
				pdfs.add(pdf)
				vd[i_m] = float(mass)
				keeper.append(pdf)
				keeper.append(data_hist)


			#  { Linear, NonLinear, NonLinearPosFractions, NonLinearLinFractions, SineLinear } ;
			setting = getattr(ROOT.RooMomentMorph, algo)
			morph = RooMomentMorph('morph'+channel+pattern, '', m_A, RooArgList(m_ttbar), pdfs, vd, setting)
			morph.Print('v')


			m_A.setVal(float(test_mass))


			h_morph = h_ori.Clone('Morph'+h_ori.GetName().replace(other_masses[-1], test_mass))
			h_ori = f_ori.Get('{channel}/ggA_{pattern}-{width}pc-M{mass}'.format(channel=channel, pattern=pattern, width=width, mass=test_mass))

			h_ori_down = f_ori.Get('{channel}/ggA_{pattern}-{width}pc-M{mass}'.format(channel=channel, pattern=pattern, width=width, mass=other_masses[0]))
			h_ori_up = f_ori.Get('{channel}/ggA_{pattern}-{width}pc-M{mass}'.format(channel=channel, pattern=pattern, width=width, mass=other_masses[1]))

			# h_ori.Scale(1./h_ori.Integral())

			# h_ori_down.Scale(1./h_ori_down.Integral())
			# h_ori_up.Scale(1./h_ori_up.Integral())

			for i_bin in xrange(h_ori.GetNbinsX()):
				x = h_ori.GetBinCenter(i_bin+1)
				# print 'mttbar = ', x
				m_ttbar.setVal(x)

				# for i_pdf in xrange(len(pdfs)):
				# 	print pdfs[i_pdf].getVal()

				h_morph.SetBinContent(i_bin+1, morph.getVal()*h_ori.GetBinWidth(i_bin+1))
			
			h_ori.Draw('HIST E')
			h_ori.GetYaxis().SetRangeUser(0., 1.3*max(h_ori.GetMaximum(), h_morph.GetMaximum(), h_ori_up.GetMaximum(), h_ori_down.GetMaximum()))
			h_ori.SetLineColor(1)
			h_ori.SetLineWidth(3)
			h_ori.SetLineStyle(2)

			h_morph.SetLineColor(2)
			h_morph.SetLineStyle(1)
			h_morph.SetLineWidth(3)
			h_morph.Draw('SAME HIST E')

			h_ori_up.SetLineColor(3)
			h_ori_up.SetLineStyle(3)
			h_ori_up.Draw('SAME HIST')

			h_ori_down.SetLineColor(4)
			h_ori_down.SetLineStyle(4)
			h_ori_down.Draw('SAME HIST')

			import os
			def ensureDir(directory):
			    if not os.path.exists(directory):
			        os.makedirs(directory)

			ensureDir('roomorph_plots_'+algo)
			cv.Print('roomorph_plots_{algo}/{channel}_{pattern}_{width}_{test_mass}.pdf'.format(algo=algo, channel=channel, pattern=pattern, width=width, test_mass=test_mass))



# test_mass = '500'
# other_masses = ['400', '600', '750']
# width = '5'

# f_ori = TFile('../data/templates1D_240317.root')

# cv = TCanvas()

# 		h_morph = f_debug.Get('{channel}_ggA_{pattern}-{width}pc-M_morph/morph_point_{test_mass}'.format(channel=channel, pattern=pattern, width=width, test_mass=test_mass))
		
# 		# h_morph.Scale(h_ori.Integral())
# 		h_morph.Scale(f_debug.Get("interp_rate_{channel}_ggA_{pattern}-{width}pc-M".format(channel=channel, pattern=pattern, width=width)).Eval(float(test_mass)))
		

# 		print 'Integral original', h_ori.Integral()
# 		print 'Integral linear  ', f_debug.Get("interp_rate_{channel}_ggA_{pattern}-{width}pc-M".format(channel=channel, pattern=pattern, width=width)).Eval(float(test_mass))
		
# 		h_ori.Draw('HIST E')
# 		h_ori.SetLineWidth(3)
# 		h_ori.SetLineStyle(2)

# 		h_morph.SetLineColor(2)
# 		h_morph.SetLineWidth(2)
# 		h_morph.Draw('SAME HIST E')

# 		cv.Print('morph_plots/{channel}_{pattern}_{width}_{test_mass}.pdf'.format(channel=channel, pattern=pattern, width=width, test_mass=test_mass))
