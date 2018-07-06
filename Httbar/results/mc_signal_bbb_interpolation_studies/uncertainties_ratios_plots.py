import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import ROOT as R
from itertools import product
import numpy as np

tf = R.TFile('templates.root')

for chan, par, width in product( #chan, par, mass, width, comp
   ['ll', 'ejets', 'mujets'],
   ['A', 'H'],
   ['50', '5', '10', '25', '2p5'],
   ):
   plt.clf()
   for comp in ['pos-sgn', 'pos-int', 'neg-int']:
      data = []
      for mass in ['400', '500', '600', '750']:
         key = '%s/gg%s_%s-%spc-M%s' % (chan, par, comp, width, mass)
         histo = tf.Get(key)
         vals = []
         errs = []
         for ibin in range(1, histo.GetNbinsX()+2):
            val = histo.GetBinContent(ibin)
            err = histo.GetBinError(ibin)
            if val:
               vals.append(val)
               errs.append(err)
         vals = np.array(vals)
         errs = np.array(errs)
         ratios = errs/np.sqrt(vals)
         data.append((int(mass), ratios.mean(), ratios.std()))
      plt.errorbar(
         [i for i, _, _ in data], [i for _, i, _ in data], yerr=[i for _, _, i in data],
         label=comp, ls='none', marker='o', markersize=5
         )
   plt.legend(loc='best')
   plt.xlim(350, 800)
   plt.savefig('%s_%s_%s.png' % (chan, par, width))
   plt.savefig('%s_%s_%s.pdf' % (chan, par, width))

