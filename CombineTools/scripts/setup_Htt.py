#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os

cb = ch.CombineHarvester()

auxiliaries  = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/CombineTools/scripts/'
aux_shapes   = auxiliaries 

for mode in ['scalar']:#, 'pseudoscalar']:
# for mode in ['pseudoscalar']:#, 'pseudoscalar']:

  procs = {
    'sig'  : ['S0_{mode}_M'.format(mode=mode), 'S0_neg_{mode}_M'.format(mode=mode)],
    # 'sim'  : ['WZ', 'ZZ', 'ttW', 'ttZ', 'ttH'],
    'bkg'  : ['t_bar_t__correct', 'Single_t','W_jets','Z_jets','QCD_multijet','Diboson']#'t_bar_t__wrong', 't_bar_t__unmatched',
  }

  cats = [(0, 'l_plus_jets')]

  masses = ['400', '500', '600', '700', '800']

  cb.AddObservations(['*'], ['hexo'], ["8TeV"], ['htt'], cats)
  cb.AddProcesses(['*'], ['hexo'], ["8TeV"], ['htt'], procs['bkg'], cats, False)
  cb.AddProcesses(masses, ['hexo'], ["8TeV"], ['htt'], procs['sig'], cats, True)

  print '>> Adding systematic uncertainties...'

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'lumi_$ERA', 'lnN', ch.SystMap()(1.026))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'CMS_th_eff_e_$ERA', 'lnN', ch.SystMap('bin')(['emt'], 1.051))

  cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
      cb, 'CMS_th_eff_m_$ERA', 'lnN', ch.SystMap('bin')(['emt'], 1.051)(['mmt'], 1.102))


  cb.cp().process(procs['sig'] + ['ttW', 'ttH', 'ZZ', 'WZ']).AddSyst(
      cb, 'CMS_scale_j_$ERA', 'lnN', ch.SystMap()(1.04))

  cb.cp().AddSyst(
      cb, 'CMS_th_mc_stats_$PROCESS_$BIN_$ERA', 'lnN', ch.SystMap( 'process')
        (['QCD_multijet'], 5.) # yes crazy 1 single entry
        # (['ttW'], 1.14)
        # (['ttH'], 1.06)
        # (['ZZ'],  1.10)
        # (['WZ'],  1.12)
  )

  cb.cp().AddSyst(
      cb, 'CMS_eff_b_$ERA', 'lnN', ch.SystMap('process')
        (procs['sig'], 1.05)
        (procs['bkg'], 1.03))

  cb.cp().AddSyst(
      cb, 'CMS_fake_b_$ERA', 'lnN', ch.SystMap('process')
        (procs['bkg'], 1.01))


  # cb.cp().process(procs['sig']).AddSyst(cb, 'QCDscale_tHq', 'lnN', ch.SystMap()(1.019))
  cb.cp().process(['t_bar_t__correct']).AddSyst(cb, 'QCDscale_tt', 'lnN', ch.SystMap()(1.053))
  cb.cp().process(['Single_t']).AddSyst(cb, 'QCDscale_singlet', 'lnN', ch.SystMap()(1.10))
  cb.cp().process(['W_jets']).AddSyst(cb, 'QCDscale_w4jets', 'lnN', ch.SystMap()(1.2))
  cb.cp().process(['Z_jets']).AddSyst(cb, 'QCDscale_VV', 'lnN', ch.SystMap()(1.2))
  cb.cp().process(['Diboson']).AddSyst(cb, 'QCDscale_Diboson', 'lnN', ch.SystMap()(1.05))

  cb.cp().AddSyst(
      cb, 'pdf_gg', 'lnN', ch.SystMap('process')
        (procs['sig'], 1.05)
        (['t_bar_t__correct'], 1.025)
        )

  cb.cp().AddSyst(
      cb, 'pdf_qqbar', 'lnN', ch.SystMap('process')
        (['t_bar_t__correct'], 1.01))

  cb.cp().AddSyst(
      cb, 'pdf_qg', 'lnN', ch.SystMap('process')
        (['tHW'], 1.048))


  print '>> Extracting histograms from input root files...'
  in_file = aux_shapes + 'hexo_tth.inputs-bsm-8TeV.root'
  cb.cp().backgrounds().ExtractShapes(
      in_file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
  cb.cp().signals().ExtractShapes(
      in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')


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

  writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
                         '$TAG/common/$ANALYSIS_$CHANNEL.input.root')
  writer.SetVerbosity(1)
  writer.WriteCards('output/sm_cards/{mode}'.format(mode=mode), cb)

print '>> Done!'

# Post instructions:
'''
combineTool.py -M T2W -i {scalar,pseudoscalar}/* -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel
combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --parallel 4
combineTool.py -M CollectLimits */*/*.limit.* --use-dirs -o limits.json
'''


