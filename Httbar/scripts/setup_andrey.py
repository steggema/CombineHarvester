#!/usr/bin/env python
from argparse import ArgumentParser
from pdb import set_trace

parser = ArgumentParser()
parser.add_argument('jobid')
parser.add_argument('--limit' , choices=['electrons', 'muons', 'cmb'], help='choose leptonic decay type', default='cmb')
parser.add_argument('--masses', default='400,500,600,750', help='coma separated list of masses')
parser.add_argument('--widths', default='5,10,25,50', help='coma separated list of widths')
parser.add_argument('--parity', default='A,H', help='coma separated list of parity (A,H only)')
parser.add_argument('--noBBB', action='store_true')
parser.add_argument('--noMorph', action='store_true')
args = parser.parse_args()

import os

from ROOT import RooWorkspace, TFile, RooRealVar

import CombineHarvester.CombineTools.ch as ch
from CombineHarvester.CombinePdfs.morphing import BuildRooMorphing

auxiliaries = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/Httbar/data/'
aux_shapes = auxiliaries

addBBB = not args.noBBB

masses = args.masses.split(',')
widths = args.widths.split(',')#['5', '10', '25', '50']
modes  = args.parity.split(',')

doMorph = not args.noMorph

for mode in modes:
	for width in widths:
		cb = ch.CombineHarvester()
		patterns = ['gg{mode}_pos-sgn-{width}pc-M', 'gg{mode}_pos-int-{width}pc-M',  'gg{mode}_neg-int-{width}pc-M']
		
		procs = {
			'sig': [pattern.format(mode=mode, width=width) for pattern in patterns],
			'bkg': ['WJets', 'tWChannel', 'tChannel', 'VV', 'ZJets', 'TT','TTV'],
			'bkg_mu':['QCDmujets'],
			'bkg_e' :['QCDejets' ]
		}		

		cats = []
		if args.limit == 'muons' or args.limit == 'cmb':
			cats.append((len(cats), 'mujets'))
		if args.limit == 'electrons' or args.limit == 'cmb':
			cats.append((len(cats), 'ejets'))
		cats = [(0, 'mujets'), (1, 'ejets')]
		cat_to_id = {a:b for b, a in cats}
		
		cb.AddObservations(['*'], ['httbar'], ["8TeV"], [''], cats)
		cb.AddProcesses(['*'], ['httbar'], ["8TeV"], [''], procs['bkg'], cats, False)
		cb.AddProcesses(masses, ['httbar'], ["8TeV"], [''], procs['sig'], cats, True)
		if args.limit == 'muons' or args.limit == 'cmb':
			cb.AddProcesses(
				['*'], ['httbar'], ["8TeV"], 
				[''], procs['bkg_mu'], 
				[(cat_to_id['mujets'], 'mujets')], False)
		if args.limit == 'electrons' or args.limit == 'cmb':
			cb.AddProcesses(
				['*'], ['httbar'], ["8TeV"], 
				[''], procs['bkg_e'], 
				[(cat_to_id['ejets'], 'ejets')], False)
		
		print '>> Adding systematic uncertainties...'
		
		### RATE UNCERTAINTIES
		
		# THEORY
		cb.cp().process(['VV']).AddSyst(
			cb, 'CMS_httbar_vvNorm_13TeV', 'lnN', ch.SystMap()(1.5))
		
		cb.cp().process(['TT']).AddSyst(
			cb, 'CMS_httbar_ttbarNorm_13TeV', 'lnN', ch.SystMap()(1.059))
		
		cb.cp().process(['tWChannel']).AddSyst(
			cb, 'CMS_httbar_tWChannelNorm_13TeV', 'lnN', ch.SystMap()(1.15))
		
		cb.cp().process(['tChannel']).AddSyst(
			cb, 'CMS_httbar_tChannelNorm_13TeV', 'lnN', ch.SystMap()(1.20))
		
		cb.cp().process(['WJets']).AddSyst(
			cb, 'CMS_httbar_WNorm_13TeV', 'lnN', ch.SystMap()(1.5))
		
		cb.cp().process(['ZJets']).AddSyst(
			cb, 'CMS_httbar_ZNorm_13TeV', 'lnN', ch.SystMap()(1.5))
		
		cb.cp().process(['TTV']).AddSyst(
			cb, 'CMS_httbar_TTVNorm_13TeV', 'lnN', ch.SystMap()(1.2))
		
		# Experiment
		cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
			cb, 'lumi', 'lnN', ch.SystMap()(1.058))
		
		cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
			cb, 'CMS_eff_trigger_m', 'lnN', ch.SystMap('bin_id')([cat_to_id['mujets']], 1.02))
		
		cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
			cb, 'CMS_eff_trigger_e', 'lnN', ch.SystMap('bin_id')([cat_to_id['ejets']], 1.02))
		
		if args.limit == 'muons' or args.limit == 'cmb':
			cb.cp().process(['QCDmujets']).AddSyst(
				cb, 'CMS_httbar_mujets_QCDNorm', 'lnN', ch.SystMap('bin_id')([cat_to_id['mujets']], 2.0))
		if args.limit == 'electrons' or args.limit == 'cmb':
			cb.cp().process(['QCDejets']).AddSyst(
				cb, 'CMS_httbar_ejets_QCDNorm', 'lnN', ch.SystMap('bin_id')([cat_to_id['ejets']], 2.0))

		# GENERIC SHAPE UNCERTAINTIES
		shape_uncertainties = [
			'CMS_pileup', 'CMS_eff_b_13TeV', 'CMS_fake_b_13TeV', 
			'CMS_scale_j_13TeV', 'CMS_res_j_13TeV', 'CMS_METunclustered_13TeV']
		
		for shape_uncertainty in shape_uncertainties:
			cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap()(1.))
		
		shape_uncertainties_mu = ['CMS_eff_m']
		for shape_uncertainty in shape_uncertainties_mu:
			cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')([cat_to_id['mujets']], 1.))
		
		# SPECIFIC SHAPE UNCERTAINTIES
		
		shape_uncertainties_tt = [
			'QCDscaleMERenorm_TT', 'QCDscaleMEFactor_TT',
			'QCDscaleISR_TT', 'QCDscaleFSR_TT',
			'Hdamp_TT', 'TMass', 'pdf']
		
		for shape_uncertainty in shape_uncertainties_tt:
			cb.cp().process(['TT']).AddSyst(
				cb, shape_uncertainty, 'shape', ch.SystMap()(1.))
		
		print '>> Extracting histograms from input root files...'
		in_file = aux_shapes + 'templates_%s.root' % args.jobid #1D_161110
		
		cb.cp().backgrounds().ExtractShapes(
			in_file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
		cb.cp().signals().ExtractShapes(
			in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')
		
		if addBBB:
			bbb = ch.BinByBinFactory().SetAddThreshold(0.).SetFixNorm(False).SetMergeThreshold(0.5)
			bbb.MergeAndAdd(cb.cp().process(['TT']), cb)
		
		if doMorph:
			mA = RooRealVar('MH', 'MH', 400., 750.);
			mA.setConstant(True)
		
			mass_debug = False
			if mass_debug:
				f_debug = TFile('morph_debug.root', 'RECREATE')
			print 'Try to morph between masses'
			ws = RooWorkspace('httbar', 'httbar')
			bins = cb.bin_set()
			for bin in bins:
				for proc in procs['sig']:
					BuildRooMorphing(ws, cb, bin, proc, mA, "norm", True, True, False, f_debug if mass_debug else None)
		
			if mass_debug:
				f_debug.Close()
			cb.AddWorkspace(ws, False)
			cb.cp().process(procs['sig']).ExtractPdfs(cb, "httbar", "$BIN_$PROCESS_morph", "")
				
		print '>> Setting standardised bin names...'
		ch.SetStandardBinNames(cb)
		#cb.PrintAll()
		
		if not doMorph:
			writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID.txt',
								   '$TAG/$ANALYSIS_$CHANNEL.input.root')
		else:
			writer = ch.CardWriter('$TAG/000/$ANALYSIS_$CHANNEL_$BINID.txt',
								   '$TAG/$ANALYSIS_$CHANNEL.input.root')
		writer.SetWildcardMasses([])
		writer.SetVerbosity(100)
		print 'Writing cards...'
		writer.WriteCards('output{jobid}/{mode}_{width}'.format(jobid=args.jobid, mode=mode, width=width), cb)

print '>> Done!'

# Post instructions:
'''
### Create datacards
cd output
combineTool.py -M T2W -i A_5/ -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel
# Use {A,H} instead of directory A to run both with one command

### Expected limits for range of masses


combineTool.py -M Asymptotic -d A_5/MORPH/workspace.root --there -n .limit --parallel 4 -m "400:750:25" -t -1 --minimizerTolerance=0.0001 --minimizerStrategy=2
combineTool.py -M CollectLimits A_5/MORPH/*.limit.* --use-dirs -o limits.json
plotLimits.py --y-title="Coupling modifier" --x-title="M_{A} (GeV)" limits_MORPH.json


### Pulls

# Asimov pulls
combine -M MaxLikelihoodFit A/400/workspace.root -t -1 --expectSignal 0.
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -A -f text -g nuisances_bonly.root mlfit.root > nuisances_bonly.txt
combine -M MaxLikelihoodFit A/400/workspace.root -t -1 --expectSignal 2.
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -A -f text -g nuisances_2splusb.root mlfit.root > nuisances_2splusb.txt

# B-only pulls, avoiding unblinding

# Measure ttbar cross section and make pulls
combine -M MaxLikelihoodFit A/400/workspace.root --redefineSignalPOIs QCDscale_ttbar 
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -A -f text -g nuisances.root mlfit.root

# Expected likelihood scan
combine A/400/workspace.root -M MultiDimFit --rMin 0 --rMax 2 --robustFit on --points 200 --algo=grid -t -1 --expectSignal=1.


combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --parallel 4
combineTool.py -M CollectLimits */*/*.limit.* --use-dirs -o limits.json
plotLimits.py --y-title="Coupling modifier" --x-title="M_{A} (GeV)" limits_A.json 

combineTool.py -M Impacts -d A/400/workspace.root -m 400 --doInitialFit --robustFit 1
combineTool.py -M Impacts -d A/400/workspace.root -m 400 --robustFit 1 --doFits
# combineTool.py -M ImpactsFromScans -d workspace.root -m 400 --robustFit 1 --doFits  --robustFit on
combineTool.py -M Impacts -d A/400/workspace.root -m 400  -o impacts.json
plotImpacts.py -i impacts.json -o impacts
'''
