#! /bin/env python


import os
from argparse import ArgumentParser
import numpy as np

parser = ArgumentParser()
parser.add_argument('submission_dir')
parser.add_argument('--save_failed', action='store_true', help='save dummy values for failed jobs')
args = parser.parse_args()

jdl = open('%s/condor.jdl' % args.submission_dir).read()
blocks = jdl.split('\n\n')
header = blocks[0]
block_map = {}
for block in blocks[1:]:
    key = tuple(block.split('Arguments = ')[1].split(' ')[1:4])
    block_map[key] = block

summary = {}
fails = []
mis_runs = 0
produced = []
for key, submit in block_map.iteritems():
    parity, mass, width = key
    # width = '%.1f' % float(width)
    width = str(width).replace('.', 'p')
    if width.endswith('p'):
        width = width[:-1]
    name = '_'.join([parity, mass, width])
    jname = '%s/%s_sig.npy' % (args.submission_dir, name)
    if not os.path.isfile(jname):
        print jname
        # import pdb; pdb.set_trace()
        fails.append(key)
        print 'Point %s not computed successfully!' % (key,)
        summary[key] = {}
        # import pdb; pdb.set_trace()
        if args.save_failed:
	        new_row = np.array(produced[-1])
	        new_row['mass'] = mass
	        new_row['parity'] = parity
	        new_row['width'] = key[2]
	        new_row['sig_g'] = -1.
	        new_row['sig_r'] = -1.
	        new_row['sig_g_scan'] = -1.
	        new_row['sig_r_scan'] = -1.
	        produced.append(new_row)
    else:
        print jname
        row = np.load(open(jname))
        if not len(row):
            fails.append(key)
        produced.append(row)

print '''Run Summary:
  Successful jobs: %d
  Failed jobs: %d
  Out of which jobs not properly finished: %d
''' % (len(produced), len(fails), mis_runs)

if fails:
    print 'dumping rescue job'
    with open('%s/condor.rescue.jdl' % args.submission_dir, 'w') as rescue:
        rescue.write(header)
        rescue.write('\n\n')
        rescue.write(
            '\n\n'.join([block_map[key] for key in fails])
            )

if not produced:
    print 'All points failed! Exiting!'
    exit(0)

with open('%s/sign_summary.npy' % args.submission_dir, 'wb') as out:
    arr = np.concatenate(produced)
    np.save(out, arr)
