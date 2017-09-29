#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os

cb = ch.CombineHarvester()

auxiliaries  = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/CombineTools/scripts/'
aux_shapes   = auxiliaries 

for mode in ['scalar']:#, 'pseudoscalar']:
# for mode in ['pseudoscalar']:#, 'pseudoscalar']:

  procs = {
    # 'sig'  : ['S0_{mode}_M'.format(mode=mode), 'S0_neg_{mode}_M'.format(mode=mode)],
    'sig'   : ['H600_pseudoscalar', 'H600_pseudoscalar_neg'],
    # 'sim'  : ['WZ', 'ZZ', 'ttW', 'ttZ', 'ttH'],
    'bkg'  : ['wjets', 'single_antitop', 'single_top', 'dibosons', 'zjets', 'TT']
  }

  cats = [(0, 'e_1btag'), (1, 'e_2btag'), (2, 'mu_1btag'), (3, 'mu_2btag')]

  # masses = ['400', '500', '600', '700', '800']

  cb.AddObservations(['*'], ['lyon'], ["8TeV"], ['htt'], cats)
  cb.AddProcesses(['*'], ['lyon'], ["8TeV"], ['htt'], procs['bkg'], cats, False)
  # cb.AddProcesses(masses, ['lyon'], ["8TeV"], ['htt'], procs['sig'], cats, True)
  cb.AddProcesses(['*'], ['lyon'], ["8TeV"], ['htt'], procs['sig'], cats, True)

  print '>> Adding systematic uncertainties...'

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'lumi', 'lnN', ch.SystMap()(1.026))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'lept_e', 'lnN', ch.SystMap('bin')(['e_1btag', 'e_2btag'], 1.0059))

  cb.cp().process(['dibosons']).AddSyst(
      cb, 'diboson_rate', 'lnN', ch.SystMap()(1.3))

  cb.cp().process(['TT']).AddSyst(
      cb, 'ttbar_rate', 'lnN', ch.SystMap()(1.05))

  cb.cp().process(['single_top', 'single_antitop']).AddSyst(
      cb, 'st_rate', 'lnN', ch.SystMap()(1.05))

  cb.cp().process(['wjets']).AddSyst(
      cb, 'w_rate', 'lnN', ch.SystMap()(1.23))

  cb.cp().process(['zjets']).AddSyst(
      cb, 'z_rate', 'lnN', ch.SystMap()(1.23))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'pu', 'lnN', ch.SystMap()(1.0024))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'trigger', 'lnN', ch.SystMap()(1.0115))

  cb.cp().process(['TT']).AddSyst(
      cb, 'alphaspdf', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'btag', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'jec', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'jer', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'btag', 'shape', ch.SystMap()(1.))

  cb.cp().process(['zjets', 'wjets', 'TT']).AddSyst(
      cb, 'scale', 'shape', ch.SystMap()(1.))
  
  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'lept_mu', 'lnN', ch.SystMap('bin')(['mu_1btag', 'mu_2btag'], 1.))

  print '>> Extracting histograms from input root files...'
  in_file = aux_shapes + 'lyon_tth.inputs-bsm-8TeV.root'
  cb.cp().backgrounds().ExtractShapes(
      in_file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')
  cb.cp().signals().ExtractShapes(
      # in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')
    in_file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')


  # print '>> Generating bbb uncertainties...'
  # bbb = ch.BinByBinFactory()
  # bbb.SetAddThreshold(0.1).SetFixNorm(True)
  # bbb.AddBinByBin(cb.cp().process(['reducible']), cb)


  # for mass in masses:
  #   norm_initial = norms[mode][int(mass)] 

  #   cb.cp().process(['S0_neg_{mode}_M{mass}'.format(mode=mode, mass=mass), 'S0_{mode}_M{mass}'.format(mode=mode, mass=mass)]).ForEachProc(lambda p: p.set_rate(p.rate()/norm_initial))

  print '>> Setting standardised bin names...'
  ch.SetStandardBinNames(cb)
  cb.PrintAll()

  # writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
  # writer = ch.CardWriter('$TAG/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
                         # '$TAG/$ANALYSIS_$CHANNEL.input.root')
  # writer.SetVerbosity(100)
  # writer.WriteCards('output/lyon_cards/{mode}'.format(mode=mode), cb)
  print 'Try writing cards...'
  import ROOT
  f_out = ROOT.TFile('lyon_out.root', 'RECREATE')
  cb.WriteDatacard("lyon_out.txt", 'lyon_out.root')
  # writer.WriteCards('output/lyon_cards/', cb)

print '>> Done!'

# Post instructions:
'''
combineTool.py -M T2W -i {scalar,pseudoscalar}/* -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel
combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --parallel 4
combineTool.py -M CollectLimits */*/*.limit.* --use-dirs -o limits.json
'''


