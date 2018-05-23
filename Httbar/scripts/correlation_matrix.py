#!/usr/bin/env python

import ROOT
import json
from operator import itemgetter
from os import path

N_PARS = 20

j = json.load(open('impacts.json'))

rename = json.load(open(path.expandvars('$CMSSW_BASE/src/CombineHarvester/Httbar/data/impacts_rename.json')))

pars = sorted(j['params'], key=itemgetter('impact_r'), reverse=True)

# 10 most important parameters
pars = pars[:N_PARS]

f = ROOT.TFile("fitDiagnostics.root")
fit_s = f.Get("fit_s")
nuisances = f.Get("nuisances_prefit")

h2 = ROOT.TH2F('corr', '', N_PARS, -0.5, -0.5+N_PARS, N_PARS, -0.5, -0.5+N_PARS)

for i1, par1 in enumerate(pars):
    for i2, par2 in enumerate(pars):
        h2.Fill(i1, i2, fit_s.correlation(par1['name'], par2['name']))
        if fit_s.correlation(par1['name'], par2['name'])>1.:
            import pdb; pdb.set_trace()

for i, par in enumerate(pars):
    h2.GetXaxis().SetBinLabel(i + 1, rename[par['name']])
    h2.GetYaxis().SetBinLabel(i + 1, rename[par['name']])

cv = ROOT.TCanvas()
h2.Draw('COLZ')

# Style shit
h2.SetStats(False)
h2.GetXaxis().SetLabelSize(0.05)
h2.GetXaxis().SetLabelOffset(0.01)
h2.GetYaxis().SetLabelSize(0.05)
h2.GetXaxis().LabelsOption('v')
cv.SetLeftMargin(0.3)
cv.SetBottomMargin(0.3)
cv.SetRightMargin(0.2)

cv.Print('correlation.pdf')
