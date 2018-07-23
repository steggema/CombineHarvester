#! /bin/env python

import os
from argparse import ArgumentParser
import json
import numpy as np

from ROOT import TFile

parser = ArgumentParser()
parser.add_argument('submission_dir')
args = parser.parse_args()

jdl = open('%s/condor.jdl' % args.submission_dir).read()
blocks = jdl.split('\n\n')
header = blocks[0]
block_map = {}
for block in blocks[1:]:
    key = tuple(block.split('Arguments = ')[1].split(' ')[1:4])
    block_map[key] = block

MAX_LIM = 3.
STEP_SIZE = 0.01

summary = {}
npass = 0
fails = []
mis_runs = 0
produced = None
for key, submit in block_map.iteritems():
    parity, mass, width = key
    # width = ('%.1f' % float(width)).replace('.', 'p').replace('p0', '')
    width = width.rstrip('.').replace('.', 'p')
    name = '_'.join([parity, mass, width])
    rname = '%s/%s_limits_gathered.root' % (args.submission_dir, name)
    if not os.path.isfile(rname):
        fails.append(key)
        print 'Point %s not computed successfully! (ROOT file missing)' % (key,), rname
        summary[key] = {}
    else:
        rfile = TFile.Open(rname)
        if rfile.IsZombie():
            fails.append(key)
            print 'Point %s not computed successfully! (ROOT file corrupt)' % (key,)
            summary[key] = {}
            continue
        
        limits = rfile.Get('limit')
        lims = ['obs', 'exp-2', 'exp-1', 'exp0', 'exp+1', 'exp+2']
        quantiles = [-1, 0.025, 0.160, 0.5, 0.840, 0.975]
        # d_upper_limits = {lim:[] for lim in lims}
        # d_lower_limits = {lim:[] for lim in lims}
        # limit_previous = {lim:1. for lim in lims}

        
        
        all_cls = [[] for _ in range(len(lims))]


        print 'File', rname
        # First aggregate all CLs values (with the beautiful entry name entry.limit)
        for entry in limits:
            for i_q, quantile in enumerate(quantiles):
                if abs(entry.quantileExpected - quantile) < 0.0001:
                    all_cls[i_q].append((entry.g, entry.limit))



        upper_limits = [[] for _ in range(len(lims))]
        lower_limits = [[] for _ in range(len(lims))]
        limit_previous = [1.]*len(lims)

        # Then outlier removal and  limit determination
        for i_q, quantile in enumerate(quantiles):
            cls_vals = sorted(all_cls[i_q])
            
            down_outlier_flag = False
            up_outlier_flag = False
            cls_vals_plus_g = [(g, cls_val) for g, cls_val in cls_vals if cls_val >= 0. and cls_val != 0.5 and cls_val != 0.0]
            cls_vals = [cls_val for _, cls_val in cls_vals_plus_g if cls_val >= 0. and cls_val != 0.5 and cls_val != 0.0]
            len_vals = len(cls_vals)

            for i_val, (g, cls_val) in enumerate(cls_vals_plus_g):
                if i_val == 0:
                    continue

                try:
                    if cls_val < 0.05 and cls_vals[i_val-2] > 0.05 and cls_vals[i_val-1] > 0.05 and cls_vals[i_val+1] > 0.05 and cls_vals[i_val+2] > 0.05:
                        print '--_-- outlier'
                        down_outlier_flag = True
                        continue

                    if cls_val < 0.05 and cls_vals[i_val-2] > 0.05 and cls_vals[i_val-1] > 0.05 and cls_vals[i_val+1] > 0.05 and cls_vals[i_val+2] < 0.05:
                        print '--_-_ outlier'
                        down_outlier_flag = True
                        continue
                except IndexError:
                    pass

                if cls_val < 0.05 and cls_vals[i_val-1] > 0.05:
                    # Outlier detection
                    if up_outlier_flag and len(upper_limits[i_q]) > 0: # Make sure there's some UL already
                        print 'Previous point marked as upward outlier, continue'
                        up_outlier_flag = False
                        continue

                    if abs(cls_val - cls_vals[i_val-1]) > 0.035:
                        print 'Found large jump in limit value, investigating', g
                        if i_val > len(cls_vals) - 3:
                            print 'At the end, will just continue'
                            print i_val, cls_vals
                            continue
                        if cls_val < cls_vals[i_val+1]:
                            if cls_vals[i_val+1] > 0.05 and abs(cls_vals[i_val-1] - cls_vals[i_val+1]) < 0.05:
                                print 'Next CLs value higher, marking as outlier', cls_vals[i_val-1], cls_val, cls_vals[i_val+1]
                                down_outlier_flag = True
                                continue
                            elif cls_vals[i_val+2] < 0.05:
                                print 'Next CLs value higher, but both next and next-to-next values below 0.05, so likely fine', cls_vals[i_val-1], cls_val, cls_vals[i_val+1],  cls_vals[i_val+2]
                            elif cls_vals[i_val+2] < 0.05:
                                print 'Complicated... but let\'s say it\'s ok', cls_vals[i_val-2], cls_vals[i_val-1], cls_val, cls_vals[i_val+1], cls_vals[i_val+2], cls_vals[i_val+3]
                            else:
                                print 'Complicated... but let\'s say it\'s not ok', cls_vals[i_val-2], cls_vals[i_val-1], cls_val, cls_vals[i_val+1], cls_vals[i_val+2], cls_vals[i_val+3]
                                down_outlier_flag = True
                                continue
                        # elif cls_val < cls_vals[i_val+2] and abs(cls_vals[i_val-1] - cls_vals[i_val+2]) < 0.05:
                        #     print '!!! Next-to-next CLs value higher, maybe double outlier', cls_vals[i_val-1], cls_val, cls_vals[i_val+1],  cls_vals[i_val+2]
                        #     if cls_vals[i_val+2] > 0.05 and cls_vals[i_val+3] > 0.05:
                        #         down_outlier_flag = True
                        #         continue
                        elif abs(cls_vals[i_val-2] - cls_vals[i_val-1]) > 0.5*abs(cls_val - cls_vals[i_val-1]):
                            print 'Already in large gradient region, likely fine', cls_vals[i_val-2], cls_vals[i_val-1], cls_val
                            pass
                        else:
                            print 'Need to investigate...', cls_vals[i_val-2], cls_vals[i_val-1], cls_val, cls_vals[i_val+1], cls_vals[i_val+2]
                            pass
                            # import pdb; pdb.set_trace()
                    if i_val == 1:
                        import pdb; pdb.set_trace()

                    upper_limits[i_q].append(g - STEP_SIZE/2.) # FIXME, weighted mean based on distance to 0.05??
                up_outlier_flag = False
                
                if i_val < len_vals - 3 and cls_val > 0.05 and cls_vals[i_val-2] < 0.05 and cls_vals[i_val-1] < 0.05 and cls_vals[i_val+1] < 0.05 and cls_vals[i_val+2] < 0.05:
                    print '__-__ outlier'
                    up_outlier_flag = True
                    continue

                if cls_val > 0.05 and cls_vals[i_val-1] < 0.05:
                    if i_val > len(cls_vals) - 3:
                        print 'At the end, will just continue'
                        continue
                    if abs(cls_val - cls_vals[i_val-1]) > 0.035:
                        print 'Found large jump in limit value, investigating', g
                        if cls_val > cls_vals[i_val+1] and abs(cls_vals[i_val-1] - cls_vals[i_val+1]) < 0.05:
                            print 'Next CLs value lower, marking as outlier'
                            up_outlier_flag = True
                            continue
                        # elif cls_val > cls_vals[i_val+2]:
                        #     print '!!! Next-to-next CLs value lower, maybe double outlier', cls_vals[i_val-1], cls_val, cls_vals[i_val+1],  cls_vals[i_val+2]
                        #     up_outlier_flag = True
                        #     continue
                        elif down_outlier_flag:
                            print 'Previous point marked as downward outlier'
                            down_outlier_flag = False
                            continue
                        elif abs(cls_vals[i_val-2] - cls_vals[i_val-1]) > 0.5*abs(cls_val - cls_vals[i_val-1]):
                            pass
                            print 'Already in large gradient region, likely fine'
                        elif cls_val == 0.5 or cls_val == 0. or cls_vals[i_val-1] == 0.5 or cls_vals[i_val-1] == 0.:
                            print 'Outlier-like value, continue', cls_val
                            continue
                        else:
                            print 'Need to investigate...'
                            import pdb; pdb.set_trace()
                    down_outlier_flag = False
                    lower_limits[i_q].append(g - STEP_SIZE/2.) # FIXME, weighted mean based on distance to 0.05??

            if not upper_limits[i_q]:
                print 'No upper limit found, investigating...'
                if all(v>0.05 for v in cls_vals):
                    print 'All CLs values above 0.05, fine! Mass, width:', mass, width
                    upper_limits[i_q].append(MAX_LIM)
                elif cls_vals[-1] > 0.05:
                    print 'Last CLs value above 0.05, so likely fine but with outlier(s)', mass, width
                    upper_limits[i_q].append(MAX_LIM)
                else:
                    import pdb; pdb.set_trace()

            # if len(upper_limits[i_q]) > 1:
            #     import pdb; pdb.set_trace()

            # if int(mass) == 725 and parity == 'H' and width == '25' and i_q == 0:
            #     import pdb; pdb.set_trace()
            # print lower_limits, i_q

            if i_q == 0:
                if len(lower_limits) < i_q + 1:
                    import pdb; pdb.set_trace()
                elif len(lower_limits[i_q]) > 0:
                    if lower_limits[i_q][0] < upper_limits[i_q][0]:
                        del lower_limits[i_q][0]
                    else:
                        pass


            # if int(mass) == 550 and int(width[0]) == 5:
            #     import pdb; pdb.set_trace()


        npass += 1
        summary[key] = [upper_limits, lower_limits]
        # if produced is None:
        #     produced = jmap[mass].keys()

vals_list = []
for key, item in summary.items():
    parity, mass, width = key
    mass = int(mass)
    width = float(width)
    if item:
        vals_list.append(tuple([parity, mass, width] + [i[0] for i in item[0]] + [i[0] if i else MAX_LIM for i in item[1]] + [i[1] if len(i) > 1 else (MAX_LIM if j else np.nan) for i, j in zip(item[0], item[1])]))

print '''Run Summary:
  Successful jobs: %d
  Failed jobs: %d
  Out of which jobs not properly finished: %d
''' % (npass, len(fails), mis_runs)

if fails:
    print 'dumping rescue job'
    with open('%s/condor.rescue.jdl' % args.submission_dir, 'w') as rescue:
        rescue.write(header)
        rescue.write('\n\n')
        rescue.write(
            '\n\n'.join([block_map[key] for key in fails])
            )

# if produced is None:
#     print 'All points failed! Exiting!'
#     exit(0)

with open('%s/summary.npy' % args.submission_dir, 'wb') as out:
    arr = np.array(
        vals_list,
        dtype = [('parity', 'S1'), ('mass', 'i4'), ('width', 'f4')] + [(str(i), 'f4') for i in lims] + [(str(i)+'lower', 'f4') for i in lims] + [(str(i)+'upper', 'f4') for i in lims]
        )
    np.save(out, arr)


