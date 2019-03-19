#! /bin/env python

import glob
import numpy as np

npy_files = glob.glob('Bunch?/*_sig_toys*.npy')


big_array = np.concatenate([np.load(open(f)) for f in npy_files])

with open('lle_summary.npy', 'wb') as out:
    np.save(out, big_array)
