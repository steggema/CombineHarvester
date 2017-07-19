#!/usr/bin/env python
import os
import argparse

from collections import namedtuple

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import RooWorkspace, TFile, RooRealVar

import CombineHarvester.CombineTools.ch as ch
from CombineHarvester.CombinePdfs.morphing import BuildRooMorphing
from pdb import set_trace

#
# ALL Systematic values in only one place
#

#lnN
LnNUnc = namedtuple('log_n_unc', 'procs name value')

common_theory_uncs = [
	LnNUnc(['VV'], 'CMS_httbar_VVNorm_13TeV', 1.5),
	LnNUnc(['TT'], 'TTXsec', 1.06), #FIXME?
	LnNUnc(['tWChannel'], 'CMS_httbar_tWChannelNorm_13TeV', 1.15),
	LnNUnc(['WJets'], 'CMS_httbar_WNorm_13TeV', 1.5),
	LnNUnc(['ZJets'], 'CMS_httbar_ZNorm_13TeV', 1.5),
]

ll_theory_uncs = [
	LnNUnc(['TTW'], 'CMS_httbar_TTVNorm_13TeV', 1.3),
	LnNUnc(['TTZ'], 'CMS_httbar_TTVNorm_13TeV', 1.3),
	]

lj_theory_uncs = [
	LnNUnc(['tChannel'], 'CMS_httbar_tChannelNorm_13TeV', 1.20),
	LnNUnc(['sChannel'], 'CMS_httbar_sChannelNorm_13TeV', 1.20),
	LnNUnc(['TTV'], 'CMS_httbar_TTVNorm_13TeV', 1.2),
	LnNUnc(['QCDmujets'], 'CMS_httbar_QCDmujetsNorm', 2.0),
	LnNUnc(['QCDejets'], 'CMS_httbar_QCDejetsNorm', 2.0),
	]

lumi_unc = 1.025

#shape
common_shape_uncs = ['CMS_pileup', 'CMS_eff_b_13TeV', 'CMS_fake_b_13TeV', 'CMS_scale_j_13TeV', 'CMS_res_j_13TeV']
lj_by_lepton_uncs = {
	'mu' : ['CMS_eff_m'],
	'el' : ['CMS_eff_e']
}
lj_shape_uncs = ['CMS_METunclustered_13TeV'] #trigger is missing!
ll_shape_uncs = ['CMS_eff_trigger_l']#, 'CMS_eff_e', 'CMS_eff_m']

#tt shapes
common_tt_shape_uncs = [
		'pdf', 'QCDscaleFSR_TT', 'QCDscaleISR_TT', 'Hdamp_TT', 
		'TMass', 'QCDscaleMERenorm_TT', 'QCDscaleMEFactor_TT'
		]
ll_shape_uncertainties_tt = ['TopPt1_TT', 'TopPt2_TT']
lj_shape_uncertainties_tt = [] #missing top pt!
#ll/TT_QCDscaleMEFactor_ggH-sgnDown
#ll/TT_QCDscaleMERenorm_ggH-sgnDown

#signal shape uncertainties
signal_shape_uncertainties = [
	'QCDscaleMERenorm_ggA-int',
	'QCDscaleMEFactor_ggA-int',
	'QCDscaleMERenorm_ggA-sgn',
	'QCDscaleMEFactor_ggA-sgn',
	
	'QCDscaleMERenorm_ggH-int',
	'QCDscaleMEFactor_ggH-int',
	'QCDscaleMERenorm_ggH-sgn',
	'QCDscaleMEFactor_ggH-sgn',
]

#Bin by bin template
ll_bbb_template = 'TT_CMS_httbar_%s_MCstatBin'
lj_bbb_template = 'TT_CMS_httbar_%s_MCstatBin'

def createProcessNames(widths=['5', '10', '25', '50'], modes=['A'], chan='cmb'):
	patterns = ['gg{mode}_pos-sgn-{width}pc-M', 'gg{mode}_pos-int-{width}pc-M',  'gg{mode}_neg-int-{width}pc-M']

	procs = {
		'sig': [pattern.format(mode=mode, width=width) for width in widths for pattern in patterns for mode in modes],
		'bkg': ['WJets', 'tWChannel', 'tChannel', 'sChannel', 'VV', 'ZJets', 'TT', 'TTV'],
		# 'bkg_mu':['QCDmujets'], # Ignore QCD for now because of extreme bbb uncertainties
		'bkg_mu':['QCDmujets'],
		'bkg_e':['QCDejets']
	}
	
	procs_ll = {
		'sig': [pattern.format(mode=mode, width=width) for width in widths for pattern in patterns for mode in modes],
		'bkg': ['WJets', 'tWChannel', 'VV', 'ZJets', 'TT', 'TTW', 'TTZ'],
	}

	return procs if chan == 'lj' else procs_ll

def prepareDiLepton(cb, cat_mapping, procs, in_file, masses=['400', '500', '600', '750']):
	print '\n\n------------   LL LIMIT SETTING   ------------'
	cat_ids = [cat_mapping[i] for i in ['ll']]
	cats = [(cat_mapping[i], i) for i in ['ll']]

	cb.AddProcesses(['*'],  ['httbar'], ['13TeV'], [''], procs['bkg'], cats, False)
	cb.AddProcesses(masses, ['httbar'], ['13TeV'], [''], procs['sig'], cats, True)

	bbb_systematics = {}
	tf = ROOT.TFile(in_file)
	for category in ['ll']:
		cat_dir = tf.Get(category)
		histos = [i.GetName() for i in cat_dir.GetListOfKeys()]
		sys_name = ll_bbb_template % category
		bbbs = [i[3:-2] for i in histos if i.startswith(sys_name) and i.endswith('Up')] #strip tt_...Up
		bbb_systematics[cat_mapping[category]] = bbbs
		print 'found %d bin-by-bin uncertainties for %s' % (len(bbbs), category)
	tf.Close()

	print '>> Adding systematic uncertainties...'

	### RATE UNCERTAINTIES

	# THEORY
	for unc in common_theory_uncs+ll_theory_uncs:
		cb.cp().process(unc.procs).AddSyst(
		cb, unc.name, 'lnN', ch.SystMap('bin_id')(cat_ids, unc.value))

	# EXPERIMENT
	cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
		cb, 'lumi', 'lnN', ch.SystMap('bin_id')(cat_ids, lumi_unc))

	# GENERIC SHAPE UNCERTAINTIES
	for shape_uncertainty in common_shape_uncs+ll_shape_uncs:
		cb.cp().process(
			procs['bkg'] + procs['sig']# FIXME! 
			).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')(cat_ids, 1.))

	# SPECIFIC SHAPE UNCERTAINTIES
	for shape_uncertainty in common_tt_shape_uncs+ll_shape_uncertainties_tt:
		cb.cp().process(['TT']).AddSyst(
			cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')(cat_ids, 0.166667 if shape_uncertainty=='TMass' else 1.))

	#BIN BY BIN
	for category, bbbs in bbb_systematics.iteritems():
		for bbb in bbbs:
			cb.cp().process(['TT']).AddSyst(
				cb, bbb, 'shape', ch.SystMap('bin_id')([category], 1.))

	#SIGNAL SHAPE UNCERTAINTIES
	for unc_name in signal_shape_uncertainties:
		info = unc_name.split('_')[1]
		parity, proctype = tuple(info.split('-'))
		cb.cp().process(
			[i for i in procs['sig'] if i.startswith(parity) and ('-%s-' % proctype) in i]
			).AddSyst(
			cb, unc_name, 'shape',
			ch.SystMap('bin_id')(cat_ids, 1.)
			)

def prepareLeptonPlusJets(cb, cat_mapping, procs, in_file, channel='cmb', masses=['400', '500', '600', '750']):
	print '\n\n------------   L+J LIMIT SETTING   ------------'
	cat_ids = [cat_mapping[i] for i in ['mujets', 'ejets']]

	bbb_systematics = {}
	tf = ROOT.TFile(in_file)
	for category in ['mujets', 'ejets']:
		cat_dir = tf.Get(category)
		histos = [i.GetName() for i in cat_dir.GetListOfKeys()]
		sys_name = lj_bbb_template % category
		bbbs = [i[3:-2] for i in histos if i.startswith(sys_name) and i.endswith('Up')]
		bbb_systematics[cat_mapping[category]] = bbbs
		print 'found %d bin-by-bin uncertainties for %s' % (len(bbbs), category)
	tf.Close()

	if channel in ['cmb', 'ej', 'lj']:
		ecat = [(cat_mapping['ejets'], 'ejets')]
		cb.AddProcesses(['*'], ['httbar'], ['13TeV'], [''], procs['bkg'] + procs['bkg_e'], ecat, False)
		cb.AddProcesses(masses, ['httbar'], ['13TeV'], [''], procs['sig'], ecat, True)

	if channel in ['cmb', 'mj', 'lj']:
		mucat = [(cat_mapping['mujets'], 'mujets')]
		cb.AddProcesses(['*'], ['httbar'], ['13TeV'], [''], procs['bkg'] + procs['bkg_mu'], mucat, False)
		cb.AddProcesses(masses, ['httbar'], ['13TeV'], [''], procs['sig'], mucat, True)

	print '>> Adding systematic uncertainties...'

	### RATE UNCERTAINTIES

	# THEORY
	for unc in common_theory_uncs+lj_theory_uncs:
		cb.cp().process(unc.procs).AddSyst(
		cb, unc.name, 'lnN', ch.SystMap('bin_id')(cat_ids, unc.value)
		)

	# EXPERIMENT
	cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
		cb, 'lumi', 'lnN', ch.SystMap('bin_id')(cat_ids, lumi_unc))

	# GENERIC SHAPE UNCERTAINTIES
	for shape_uncertainty in common_shape_uncs+lj_shape_uncs:
		cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')(cat_ids, 1.))

	if channel in ['cmb', 'mj', 'lj']:
		for shape_uncertainty in lj_by_lepton_uncs['mu']:
			cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')([cat_mapping['mujets']], 1.))

	if channel in ['cmb', 'ej', 'lj']:
		for shape_uncertainty in lj_by_lepton_uncs['el']:
			cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')([cat_mapping['ejets']], 1.))

	# SPECIFIC SHAPE UNCERTAINTIES
	for shape_uncertainty in common_tt_shape_uncs+lj_shape_uncertainties_tt:
		cb.cp().process(['TT']).AddSyst(
			cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')(cat_ids, 0.166667 if shape_uncertainty=='TMass' else 1.))

	#BIN BY BIN
	for category, bbbs in bbb_systematics.iteritems():
		for bbb in bbbs:
			cb.cp().process(['TT']).AddSyst(
				cb, bbb, 'shape', ch.SystMap('bin_id')([category], 1.))

	#SIGNAL SHAPE UNCERTAINTIES
	for unc_name in signal_shape_uncertainties:
		info = unc_name.split('_')[1]
		parity, proctype = tuple(info.split('-'))
		cb.cp().process(
			[i for i in procs['sig'] if i.startswith(parity) and ('-%s-' % proctype) in i]
			).AddSyst(
			cb, unc_name, 'shape',
			ch.SystMap('bin_id')(cat_ids, 1.)
			)

def addBinByBin(cb):
	bbb = ch.BinByBinFactory().SetAddThreshold(0.).SetFixNorm(False).SetMergeThreshold(0.5)
	bbb.MergeAndAdd(cb.cp().backgrounds(), cb)


def performMorphing(cb, procs, m_min=400., m_max=750., mass_debug=False):
	mA = RooRealVar('MH', 'MH', m_min, m_max) # it's most convenient to call it MH
	mA.setConstant(True)
	
	if mass_debug:
		f_debug = TFile('morph_debug.root', 'RECREATE')

	print 'Try to morph between masses'
	cb.ws = RooWorkspace('httbar', 'httbar') # Add to cb so it doesn't go out of scope
	bins = cb.bin_set()
	for bin in bins:
		for proc in procs['sig']:
			BuildRooMorphing(cb.ws, cb, bin, proc, mA, "norm", True, True, False, f_debug if mass_debug else None)

	if mass_debug:
		f_debug.Close()

	cb.AddWorkspace(cb.ws, False)
	cb.cp().process(procs['sig']).ExtractPdfs(cb, "httbar", "$BIN_$PROCESS_morph", "")

	# void BuildRooMorphing(RooWorkspace& ws, CombineHarvester& cb,
	#			   std::string const& bin, std::string const& process,
	#			   RooAbsReal& mass_var, std::string norm_postfix,
	#			   bool allow_morph, bool verbose, bool force_template_limit, TFile * file)

def writeCards(cb, jobid='dummy', mode='A', width='5', doMorph=False, verbose=True):
	print '>> Setting standardised bin names...'
	ch.SetStandardBinNames(cb)
	
	if verbose:
		cb.PrintAll()

	if not doMorph:
		writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID.txt',
							   # writer = ch.CardWriter('$TAG/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
							   '$TAG/$ANALYSIS_$CHANNEL.input.root')
	else:
		writer = ch.CardWriter('$TAG/MORPH/$ANALYSIS_$CHANNEL_$BINID.txt',
							   '$TAG/$ANALYSIS_$CHANNEL.input.root')
		writer.SetWildcardMasses([])
	
	writer.SetVerbosity(1 if verbose else 0)
	writer.WriteCards('output{jobid}/{mode}_{width}'.format(jobid=jobid, mode=mode, width=width), cb)
	# writer.WriteCards('output_comb/', cb)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('jobid')
	parser.add_argument('--channels' , choices=['ej', 'mj', 'll', 'lj', 'cmb'], help='choose leptonic decay type', default='cmb')
	parser.add_argument('--masses', default='400,500,600,750', help='comma separated list of masses')
	parser.add_argument('--parity', default='A', help='comma separated list of parity (A,H only)')
	parser.add_argument('--widths', default='2p5,5,10,25,50', help='comma separated list of widths')
	parser.add_argument(
		'--noBBB', action='store_false', dest='addBBB', help='add bin-by-bin uncertainties', default=True)
	parser.add_argument(
		'--doMorph', action='store_true', dest='doMorph', help='apply mass morphing', default=False)
	parser.add_argument(
		'--silent', action='store_true', dest='silent', default=False)

	args = parser.parse_args()
	addBBB = args.addBBB
	doMorph = args.doMorph

	aux_shapes = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/Httbar/data/'
	in_file = aux_shapes + 'templates_ALL_%s.root' % args.jobid
	in_file_lj = aux_shapes + 'templates_lj_%s.root' % args.jobid
	in_file_ll = aux_shapes + 'templates_ll_%s.root' % args.jobid

	masses = args.masses.split(',')
	widths = args.widths.split(',')#['5', '10', '25', '50'] # in percent
	modes = args.parity.split(',')
	
	#define categories
	categories_map = {
		'ej' : ['ejets'],
		'mj' : ['mujets'],
		'll' : ['ll'],
		'lj' : ['mujets', 'ejets'], 
		'cmb' : ['mujets', 'ejets', 'll'],
		}
	categories = [i for i in enumerate(categories_map[args.channels])]
	category_to_id = {a:b for b, a in categories}

	print masses, widths, modes

	for mode in modes:
		for width in widths:
			cb = ch.CombineHarvester()
			cb.AddObservations(['*'], ['httbar'], ['13TeV'], [''], categories)

			if args.channels != 'll':
				procs = createProcessNames([width], [mode], 'lj')
				prepareLeptonPlusJets(cb, category_to_id, procs, in_file_lj, args.channels, masses)

			if args.channels in ['ll', 'cmb']:
				procs = createProcessNames([width], [mode], 'll')
				prepareDiLepton(cb, category_to_id, procs, in_file_ll, masses)

			print '>> Extracting histograms from input root files...'
			cb.cp().backgrounds().ExtractShapes(
				in_file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC'
				)
			cb.cp().signals().ExtractShapes(
				in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC'
				)

			## if addBBB:
			## 	addBinByBin(cb)
			
			if doMorph:
				f_masses = [float(m) for m in masses]
				performMorphing(cb, procs, min(f_masses), max(f_masses))

			writeCards(cb, '_%s_%s' % (args.channels, args.jobid), mode, width, doMorph, verbose=not args.silent)

	print '>> Done!'

