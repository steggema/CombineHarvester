#! /bin/env python

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
from scipy.stats import norm

lle = np.load(open('./lle_summary.npy'))

# lle = lle[lle['fitted_g']>=0.]
# lle = lle[lle['sig_g'] < 6.]sig_g = np.minimum(lee_a_m_w['sig_g'], lee_a_m_w['sig_g_2p5'])

# significances_g = [np.max(lle[lle['i_toy'] == i_toy]['sig_g']) for i_toy in xrange(10000) if (lle[lle['i_toy'] == i_toy]['sig_g']).any()]
# p_value = 1. - percentileofscore(significances_g, 3.8)/100.
# print '* Fitting g *'
# print 'p value of 3.8', p_value
# print 'Significance', norm.ppf(1 - p_value)

# significances_r = [np.max(lle[lle['i_toy'] == i_toy]['sig_r']) for i_toy in xrange(10000) if (lle[lle['i_toy'] == i_toy]['sig_r']).any()]
# p_value = 1. - percentileofscore(significances_r, 3.8)/100.
# print '* Fitting r *'
# print 'p value of 3.8', p_value
# print 'Significance', norm.ppf(1 - p_value)

# significances_g2p5 = [np.max(lle[lle['i_toy'] == i_toy]['sig_g_2p5']) for i_toy in xrange(10000) if (lle[lle['i_toy'] == i_toy]['sig_g_2p5']).any()]
# p_value = 1. - percentileofscore(significances_g2p5, 3.8)/100.
# print '* Fitting g, 2p5 option *'
# print 'p value of 3.8', p_value
# print 'Significance', norm.ppf(1 - p_value)

# significances_r_g1 = [np.max(lle[lle['i_toy'] == i_toy]['sig_r_g1']) for i_toy in xrange(10000) if (lle[lle['i_toy'] == i_toy]['sig_r_g1']).any()]
# p_value = 1. - percentileofscore(significances_r_g1, 3.8)/100.
# print '* Fitting r, g fixed to 1 *'
# print 'p value of 3.8', p_value
# print 'Significance', norm.ppf(1 - p_value)


# # Redefine column (easier than appending)
# lle['sig_r_g1'] = np.minimum(lle['sig_g'], lle['sig_g_2p5'])

# significances_min_g = np.array([np.max(lle[lle['i_toy'] == i_toy]['sig_r_g1']) for i_toy in xrange(10000) if (lle[lle['i_toy'] == i_toy]['sig_r_g1']).any()])
# p_value = 1. - percentileofscore(significances_min_g, 3.8)/100.
# print '* Fitting g, minimum of max 3 and 2p5 *'
# print 'p value of 3.8', p_value
# print 'Significance', norm.ppf(1 - p_value)

mu = 0.
sigma = 1.
s = np.random.normal(mu, sigma, 1000000)
s[s < 0.] = 0.
y_normal, _ = np.histogram(s, bins=20, range=(0., 5.), weights=[float(10000)/len(s) for _ in xrange(len(s))])
y_normal = np.array([y_normal, y_normal]).T.flatten()

for mass, width in [
    (400, 4), (500, 4), (600, 4), (750, 4),
    (400, 1), (500, 1), (600, 1), (750, 1),
    (400, 10), (500, 10), (600, 10), (750, 10),
    (400, 25), (500, 25), (600, 25), (750, 25),
    ]:

    lee_a_m_w = lle[(lle['mass'] == mass) & (lle['width'] == width) & (lle['parity'] == 'H')]
    sig_g = np.minimum(lee_a_m_w['sig_g'], lee_a_m_w['sig_g_2p5'])
    p_value = 1. - percentileofscore(sig_g, 3.8)/100.
    print '* Fitting g, minimum of max 3 and 2p5, for mA {} GeV, {}% width *'.format(mass, width)
    print 'p value of 3.8', p_value
    print 'Significance', norm.ppf(1 - p_value)

    y, bins = np.histogram(sig_g, bins=20, range=(0., 5.))
    left, right = bins[:-1], bins[1:]
    x = np.array([left, right]).T.flatten()
    y = np.array([y, y]).T.flatten()
    plt.plot(x, y)
    plt.xlabel('Significance')
    plt.ylabel('N')

    plt.plot(x, y_normal, '--')
    _, top = plt.ylim()
    plt.legend(('Fit g', 'Normal'))
    plt.ylim(0., top)
    plt.xlim(0., 5.)
    # plt.show()
    plt.savefig('toys_h_{}_{}.pdf'.format(mass, width))
