#!/usr/bin/env python
import os
import argparse

from collections import namedtuple

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from ROOT import RooWorkspace, TFile, RooRealVar

import CombineHarvester.CombineTools.ch as ch
from CombineHarvester.CombinePdfs.morphing import BuildRooMorphing

def createProcessNames(widths=['5', '10', '25', '50'], modes=['A']):
    patterns = ['gg{mode}_pos-sgn-{width}pc-M', 'gg{mode}_pos-int-{width}pc-M',  'gg{mode}_neg-int-{width}pc-M']

    procs = {
        'sig': [pattern.format(mode=mode, width=width) for width in widths for pattern in patterns for mode in modes],
        'bkg': ['WJets', 'tWChannel', 'tChannel', 'sChannel', 'VV', 'ZJets', 'TT', 'TTV'],
        # 'bkg_mu':['QCDmujets'], # Ignore QCD for now because of extreme bbb uncertainties
        'bkg_mu':['QCDmujets'],
        'bkg_e':['QCDejets']
    }

    return procs


def prepareLeptonPlusJets(cb, procs, in_file, masses=['400', '500', '600', '750']):

    cats = [(0, 'mujets'), (1, 'ejets')]
    cat_to_id = {a:b for b, a in cats}

    cb.AddObservations(['*'], ['httbar'], ['13TeV'], [''], cats)
    cb.AddProcesses(['*'], ['httbar'], ['13TeV'], [''], procs['bkg'], cats, False)
    cb.AddProcesses(['*'], ['httbar'], ['13TeV'], [''], procs['bkg_e'], [(1, 'ejets')], False)
    cb.AddProcesses(['*'], ['httbar'], ['13TeV'], [''], procs['bkg_mu'], [(0, 'mujets')], False)
    cb.AddProcesses(masses, ['httbar'], ['13TeV'], [''], procs['sig'], cats, True)

    print '>> Adding systematic uncertainties...'

    ### RATE UNCERTAINTIES

    # THEORY

    LnNUnc = namedtuple('log_n_unc', 'procs name value')

    # lnN uncertainties
    theory_uncs = [
        LnNUnc(['VV'], 'CMS_httbar_VVNorm_13TeV', 1.5),
        LnNUnc(['TT'], 'QCDscale_ttbar', 1.059),
        LnNUnc(['tWChannel'], 'CMS_httbar_tWChannelNorm_13TeV', 1.15),
        LnNUnc(['tChannel'], 'CMS_httbar_tChannelNorm_13TeV', 1.20),
        LnNUnc(['sChannel'], 'CMS_httbar_sChannelNorm_13TeV', 1.20),
        LnNUnc(['WJets'], 'CMS_httbar_WNorm_13TeV', 1.5),
        LnNUnc(['ZJets'], 'CMS_httbar_ZNorm_13TeV', 1.5),
        LnNUnc(['TTV'], 'CMS_httbar_TTVNorm_13TeV', 1.2),
        LnNUnc(['QCDmujets'], 'CMS_httbar_QCDmujetsNorm', 2.0),
        LnNUnc(['QCDejets'], 'CMS_httbar_QCDejetsNorm', 2.0),
    ]

    for unc in theory_uncs:
        cb.cp().process(unc.procs).AddSyst(
        cb, unc.name, 'lnN', ch.SystMap()(unc.value))


    # EXPERIMENT
    cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
        cb, 'lumi', 'lnN', ch.SystMap()(1.026))


    ### SHAPE UNCERTAINTIES

    # GENERIC SHAPE UNCERTAINTIES

    shape_uncertainties = ['CMS_pileup', 'CMS_eff_b_13TeV', 'CMS_fake_b_13TeV', 'CMS_scale_j_13TeV', 'CMS_res_j_13TeV', 'CMS_METunclustered_13TeV']

    for shape_uncertainty in shape_uncertainties:
        cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap()(1.))

    shape_uncertainties_mu = ['CMS_eff_m']
    for shape_uncertainty in shape_uncertainties_mu:
        cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')([cat_to_id['mujets']], 1.))

    shape_uncertainties_e = ['CMS_eff_e']
    for shape_uncertainty in shape_uncertainties_e:
        cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')([cat_to_id['ejets']], 1.))

    # SPECIFIC SHAPE UNCERTAINTIES
    
    shape_uncertainties_tt = ['QCDscaleFSR_TT', 'QCDscaleISR_TT', 'Hdamp_TT', 'TMass', 'QCDscaleMERenorm_TT', 'QCDscaleMEFactor_TT']

    for shape_uncertainty in shape_uncertainties_tt:
        cb.cp().process(['TT']).AddSyst(
            cb, shape_uncertainty, 'shape', ch.SystMap()(1.))

    print '>> Extracting histograms from input root files...'
    cb.cp().backgrounds().ExtractShapes(
        in_file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
    cb.cp().signals().ExtractShapes(
        in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')


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
    #               std::string const& bin, std::string const& process,
    #               RooAbsReal& mass_var, std::string norm_postfix,
    #               bool allow_morph, bool verbose, bool force_template_limit, TFile * file)

def writeCards(cb, mode='A', width='5', doMorph=False, verbose=True):
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
    writer.WriteCards('output/{mode}_{width}'.format(mode=mode, width=width), cb)
    # writer.WriteCards('output_comb/', cb)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--noBBB', action='store_false', dest='addBBB', help='add bin-by-bin uncertainties', default=True)
    parser.add_argument(
        '--noMorph', action='store_false', dest='doMorph', help='apply mass morphing', default=True)
    parser.add_argument(
        '--lj_file', dest='lj_file', default='templates1D_240317.root')
    parser.add_argument(
        '--ll_file', dest='ll_file', default='ttBSM_13TeV_2D_PS_M400_RelW5_tagv3.root')
    parser.add_argument(
        '--silent', action='store_true', dest='silent', default=False)

    args = parser.parse_args()
    addBBB = args.addBBB
    doMorph = args.doMorph

    aux_shapes = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/Httbar/data/'
    in_file = aux_shapes + args.lj_file

    masses = ['400', '500', '600', '750']
    widths = ['5', '10', '25', '50'] # in percent
    modes = ['A'] #, 'H']

    for mode in modes:
        for width in widths:

            cb = ch.CombineHarvester()

            procs = createProcessNames([width], [mode])
            prepareLeptonPlusJets(cb, procs, in_file, masses)

            if addBBB:
                addBinByBin(cb)
            
            if doMorph:
                f_masses = [float(m) for m in masses]
                performMorphing(cb, procs, min(f_masses), max(f_masses))

            writeCards(cb, mode, width, doMorph, verbose=not args.silent)

    print '>> Done!'

