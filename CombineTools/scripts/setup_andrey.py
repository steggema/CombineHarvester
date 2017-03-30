#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('limit', choices=['electrons', 'muons', 'cmb'], help='choose leptonic decay type')
args = parser.parse_args()

cb = ch.CombineHarvester()

auxiliaries  = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/CombineTools/scripts/'
aux_shapes   = auxiliaries 

addBBB = False

masses = ['400', '500', '600', '750']
widths = ['5', '10', '25', '50']

# for mode in ['scalar']:#, 'pseudoscalar']:
for parity in ['pseudoscalar']:#, 'pseudoscalar']:
	for width in widths:
		mode='{mode}_{width}pc'.format(mode=parity, width=width)
		patterns = [i % width for i in ['ggA_pos-int-%spc-M', 'ggA_neg-int-%spc-M', 'ggA_pos-sgn-%spc-M']]
		procs = {
			# 'sig'  : ['S0_{mode}_M'.format(mode=mode), 'S0_neg_{mode}_M'.format(mode=mode)],
			'sig'   : patterns,
			# 'sim'  : ['WZ', 'ZZ', 'ttW', 'ttZ', 'ttH'],
			'bkg'  : ['TT', 'VV', 'TTV',	'tChannel', 'tWChannel', 'WJets', 'ZJets']
		}
		if args.limit == 'electrons' or args.limit == 'cmb':
			procs['bkg'].append('QCDejets')
		if args.limit == 'muons' or args.limit == 'cmb':
			procs['bkg'].append('QCDmujets')
	
		cats = []
		if args.limit == 'muons' or args.limit == 'cmb':
			cats.append((len(cats), 'mujets'))
		if args.limit == 'electrons' or args.limit == 'cmb':
			cats.append((len(cats), 'ejets'))

		cb.AddObservations(['*'], ['mauro'], ["13TeV"], ['htt'], cats)
		cb.AddProcesses(['*'], ['mauro'], ["13TeV"], ['htt'], procs['bkg'], cats, False)
		cb.AddProcesses(masses, ['mauro'], ["13TeV"], ['htt'], procs['sig'], cats, True)
		# cb.AddProcesses(['*'], ['mauro'], ["13TeV"], ['htt'], procs['sig'], cats, True)

		print '>> Adding systematic uncertainties...'
		#
		# Normalization uncertainty
		#
		cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
				cb, 'lumi_13TeV', 'lnN', ch.SystMap()(1.026))
	
		cb.cp().process(['VV']).AddSyst(
				cb, 'CMS_httbar_vvXsec_13TeV', 'lnN', ch.SystMap()(1.3))
	
		cb.cp().process(['TT']).AddSyst(
				cb, 'ttbar_rate', 'lnN', ch.SystMap()(1.05))
	
		cb.cp().process(['tChannel']).AddSyst(
				cb, 'st_rate', 'lnN', ch.SystMap()(1.05))

		cb.cp().process(['tWChannel']).AddSyst(
				cb, 'st_rate', 'lnN', ch.SystMap()(1.05))
	
		cb.cp().process(['WJets']).AddSyst(
				cb, 'w_rate', 'lnN', ch.SystMap()(1.03))
		cb.cp().process(['ZJets']).AddSyst(
				cb, 'w_rate', 'lnN', ch.SystMap()(1.03))
		cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
				cb, 'trigger', 'lnN', ch.SystMap()(1.0115))

		#
		# Shape uncetainties
		#
		#on everything
		for name in [
			'CMS_scale_j_13TeV',
			'CMS_eff_b_13TeV',
			'CMS_fake_b_13TeV',
			'CMS_pileup',
			'CMS_METunclustered_13TeV'
			]:
			cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
				cb, name, 'shape', ch.SystMap()(1.))

		#on TT only
		for name in [
			'QCDscaleMERenorm_TT',
			'QCDscaleMEFactor_TT',
			'QCDscaleMERenormFactor_TT',
			'QCDscalePS_TT',
			'TMass',
			'pdf'
			]:
			cb.cp().process(['TT']).AddSyst(
				cb, name, 'shape', ch.SystMap()(1.))

		if args.limit == 'muons' or args.limit == 'cmb':
			cb.cp().process(['QCDmujets']).AddSyst(
				cb, 'QCD_mu_norm', 'lnN', ch.SystMap()(2.))
		if args.limit == 'electrons' or args.limit == 'cmb':
			cb.cp().process(['QCDejets']).AddSyst(
				cb, 'QCD_el_norm', 'lnN', ch.SystMap()(2.))
			

		print '>> Extracting histograms from input root files...'
		in_file = args.inputfile
		cb.cp().backgrounds().ExtractShapes(
				in_file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
		cb.cp().signals().ExtractShapes(
				in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')
			# in_file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')

		if addBBB:
			bbb = ch.BinByBinFactory().SetAddThreshold(0.).SetFixNorm(False)
			bbb.MergeBinErrors(cb.cp().backgrounds())
			bbb.AddBinByBin(cb.cp().backgrounds(), cb)

		print '>> Setting standardised bin names...'
		ch.SetStandardBinNames(cb)
		cb.PrintAll()

		writer = ch.CardWriter(
			'$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID.txt',
			'$TAG/$ANALYSIS_$CHANNEL.input.root')
		# writer.SetVerbosity(100)
		writer.WriteCards('output/{mode}'.format(mode=mode), cb)
		print 'Try writing cards...'
		# import ROOT
		# f_out = ROOT.TFile('andrey_out.root', 'RECREATE')
		# cb.WriteDatacard("andrey_out.txt", 'andrey_out.root')
		# writer.WriteCards('output/andrey_cards/', cb)

print '>> Done!'

# Post instructions:
'''
combineTool.py -M T2W -i {scalar,pseudoscalar}/* -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel
combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --parallel 4
combineTool.py -M CollectLimits */*/*.limit.* --use-dirs -o limits.json
plotLimits.py --y-title="Coupling modifier" --x-title="M_{A} (GeV)" limits_default.json 

combineTool.py -M Impacts -d workspace.root -m 600 --doInitialFit --robustFit 1
combineTool.py -M Impacts -d workspace.root -m 600 --robustFit 1 --doFits
# combineTool.py -M ImpactsFromScans -d workspace.root -m 600 --robustFit 1 --doFits  --robustFit on
combineTool.py -M Impacts -d workspace.root -m 600  -o impacts.json
plotImpacts.py -i impacts.json -o impacts
'''


