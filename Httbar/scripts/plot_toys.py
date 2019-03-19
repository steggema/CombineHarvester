import numpy as np
import matplotlib.pyplot as plt

mu = 0.
sigma = 1.
s = np.random.normal(mu, sigma, 1000000)
s[s < 0.] = 0.
y_normal, _ = np.histogram(s, bins=20, range=(0., 5.), weights=[1000./len(s) for _ in xrange(len(s))])

d = np.load(open('A_400_4_sig_toys_0.npy'))
# d = np.load(open('H_425_4_sig_toys_0.npy'))


y, bins = np.histogram(d['sig_r'], bins=20, range=(0., 5.))
left, right = bins[:-1], bins[1:]
x = np.array([left, right]).T.flatten()
y = np.array([y, y]).T.flatten()
plt.plot(x, y)
plt.xlabel('Significance')
plt.ylabel('N')

y, bins = np.histogram(d['sig_g'], bins=20, range=(0., 5.))
left, right = bins[:-1], bins[1:]
x = np.array([left, right]).T.flatten()
y = np.array([y, y]).T.flatten()
plt.plot(x, y)


# import pdb; pdb.set_trace()
y_normal = np.array([y_normal, y_normal]).T.flatten()
plt.plot(x, y_normal, '--')
_, top = plt.ylim()
plt.legend(('Fit r using best-fit g', 'Fit g', 'Normal'))
plt.ylim(0., top)
plt.xlim(0., 5.)
plt.show()
