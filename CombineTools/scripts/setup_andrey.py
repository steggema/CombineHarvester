#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os

cb = ch.CombineHarvester()

auxiliaries  = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/CombineTools/scripts/'
aux_shapes   = auxiliaries 

addBBB = False

masses = ['400', '500', '600', '750']

# for mode in ['scalar']:#, 'pseudoscalar']:
for mode in ['pseudoscalar']:#, 'pseudoscalar']:

  patterns = ['HToTT-sgn-{mode}-m', 'HToTT-int-{mode}-m', 'HToTT-int-{mode}_neg-m']
  procs = {
    # 'sig'  : ['S0_{mode}_M'.format(mode=mode), 'S0_neg_{mode}_M'.format(mode=mode)],
    'sig'   : [pattern.format(mode=mode) for pattern in patterns],
    # 'sim'  : ['WZ', 'ZZ', 'ttW', 'ttZ', 'ttH'],
    'bkg'  : ['Wjets', 'single-top', 'VV', 'DY', 'ttbar', 'QCD']
  }

  cats = [(0, '1b'), (1, '2b')]

  

  cb.AddObservations(['*'], ['andrey'], ["8TeV"], ['htt'], cats)
  cb.AddProcesses(['*'], ['andrey'], ["8TeV"], ['htt'], procs['bkg'], cats, False)
  cb.AddProcesses(masses, ['andrey'], ["8TeV"], ['htt'], procs['sig'], cats, True)
  # cb.AddProcesses(['*'], ['andrey'], ["8TeV"], ['htt'], procs['sig'], cats, True)

  print '>> Adding systematic uncertainties...'

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'lumi', 'lnN', ch.SystMap()(1.026))

  cb.cp().process(['VV']).AddSyst(
      cb, 'diboson_rate', 'lnN', ch.SystMap()(1.3))

  cb.cp().process(['ttbar']).AddSyst(
      cb, 'ttbar_rate', 'lnN', ch.SystMap()(1.05))

  cb.cp().process(['single-top']).AddSyst(
      cb, 'st_rate', 'lnN', ch.SystMap()(1.05))

  cb.cp().process(['Wjets']).AddSyst(
      cb, 'w_rate', 'lnN', ch.SystMap()(1.03))

  cb.cp().process(['DY']).AddSyst(
      cb, 'dy_rate', 'lnN', ch.SystMap()(1.03))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'trigger', 'lnN', ch.SystMap()(1.0115))

  cb.cp().process(['ttbar']).AddSyst(
      cb, 'scaleTT', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'bTag', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'jec', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'jer', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'pu', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'muID', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'eID', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'metUncl', 'shape', ch.SystMap()(1.))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'bMistag', 'shape', ch.SystMap()(1.))

  cb.cp().process(['Wjets']).AddSyst(
      cb, 'scaleW', 'shape', ch.SystMap()(1.))

  cb.cp().process(['DY']).AddSyst(
      cb, 'scaleDY', 'shape', ch.SystMap()(1.))
  

  print '>> Extracting histograms from input root files...'
  in_file = aux_shapes + 'andrey_tth.inputs-bsm-8TeV.root'
  cb.cp().backgrounds().ExtractShapes(
      in_file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')
  cb.cp().signals().ExtractShapes(
      in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS__$SYSTEMATIC')
    # in_file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')


  # print '>> Generating bbb uncertainties...'
  # bbb = ch.BinByBinFactory()
  # bbb.SetAddThreshold(0.1).SetFixNorm(True)
  # bbb.AddBinByBin(cb.cp().process(['reducible']), cb)


  # for mass in masses:
  #   norm_initial = norms[mode][int(mass)] 

  #   cb.cp().process(['S0_neg_{mode}_M{mass}'.format(mode=mode, mass=mass), 'S0_{mode}_M{mass}'.format(mode=mode, mass=mass)]).ForEachProc(lambda p: p.set_rate(p.rate()/norm_initial))

  if addBBB:
    bbb = ch.BinByBinFactory().SetAddThreshold(0.).SetFixNorm(False)
    bbb.MergeBinErrors(cb.cp().backgrounds())
    bbb.AddBinByBin(cb.cp().backgrounds(), cb)

  print '>> Setting standardised bin names...'
  ch.SetStandardBinNames(cb)
  cb.PrintAll()

  writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID.txt',
  # writer = ch.CardWriter('$TAG/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
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


