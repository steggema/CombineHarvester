from pdb import set_trace

def harvest_and_outlier_removal(limit_tree, MAX_LIM = 3., STEP_SIZE = 0.01, verbose=False):
   lims = ['obs', 'exp-2', 'exp-1', 'exp0', 'exp+1', 'exp+2']
   quantiles = [-1, 0.025, 0.160, 0.5, 0.840, 0.975]
   
   # First aggregate all CLs values (with the beautiful entry name entry.limit)
   all_cls = [[] for _ in range(len(lims))]
   for entry in limit_tree:
      for i_q, quantile in enumerate(quantiles):
         if abs(entry.quantileExpected - quantile) < 0.0001:
            all_cls[i_q].append(entry.limit)

   upper_limits = [[] for _ in range(len(lims))]
   lower_limits = [[] for _ in range(len(lims))]
   limit_previous = [1.]*len(lims)

   # Then outlier removal and  limit determination
   for i_q, quantile in enumerate(quantiles):
      cls_vals = all_cls[i_q]
      down_outlier_flag = False
      up_outlier_flag = False
      cls_vals_plus_g = [(cls_val, i_g*STEP_SIZE) for i_g, cls_val in enumerate(cls_vals) if cls_val >= 0. and cls_val != 0.5 and cls_val != 0.0]
      cls_vals = [cls_val for cls_val in cls_vals if cls_val >= 0. and cls_val != 0.5 and cls_val != 0.0]
      len_vals = len(cls_vals)

      for i_val, (cls_val, g) in enumerate(cls_vals_plus_g):
         if i_val == 0:
            continue

         if i_val < len_vals - 3 and cls_val < 0.05 and cls_vals[i_val-2] > 0.05 and cls_vals[i_val-1] > 0.05 and cls_vals[i_val+1] > 0.05 and cls_vals[i_val+2] > 0.05:
            if verbose: print '--_-- outlier'
            down_outlier_flag = True
            continue

         if i_val < len_vals - 3 and cls_val < 0.05 and cls_vals[i_val-2] > 0.05 and cls_vals[i_val-1] > 0.05 and cls_vals[i_val+1] > 0.05 and cls_vals[i_val+2] < 0.05:
            if verbose: print '--_-_ outlier'
            down_outlier_flag = True
            continue

         if cls_val < 0.05 and cls_vals[i_val-1] > 0.05:
            # Outlier detection
            if up_outlier_flag and len(upper_limits[i_q]) > 0: # Make sure there's some UL already
               if verbose: print 'Previous point marked as upward outlier, continue'
               up_outlier_flag = False
               continue

            if abs(cls_val - cls_vals[i_val-1]) > 0.035:
               if verbose: print 'Found large jump in limit value, investigating', g
               if i_val > len(cls_vals) - 3:
                  if verbose: print 'At the end, will just continue'
                  #print i_val, cls_vals
                  continue
               if cls_val < cls_vals[i_val+1]:
                  if cls_vals[i_val+1] > 0.05 and abs(cls_vals[i_val-1] - cls_vals[i_val+1]) < 0.05:
                     if verbose: print 'Next CLs value higher, marking as outlier', cls_vals[i_val-1], cls_val, cls_vals[i_val+1]
                     down_outlier_flag = True
                     continue
                  elif cls_vals[i_val+2] < 0.05:
                     if verbose: print 'Next CLs value higher, but both next and next-to-next values below 0.05, so likely fine', cls_vals[i_val-1], cls_val, cls_vals[i_val+1],  cls_vals[i_val+2]
                  elif cls_vals[i_val+2] < 0.05:
                     if verbose: print 'Complicated... but let\'s say it\'s ok', cls_vals[i_val-2], cls_vals[i_val-1], cls_val, cls_vals[i_val+1], cls_vals[i_val+2], cls_vals[i_val+3]
                  else:
                     if verbose: print 'Complicated... but let\'s say it\'s not ok', cls_vals[i_val-2], cls_vals[i_val-1], cls_val, cls_vals[i_val+1], cls_vals[i_val+2], cls_vals[i_val+3]
                     down_outlier_flag = True
                     continue
               # elif cls_val < cls_vals[i_val+2] and abs(cls_vals[i_val-1] - cls_vals[i_val+2]) < 0.05:
               #     if verbose: print '!!! Next-to-next CLs value higher, maybe double outlier', cls_vals[i_val-1], cls_val, cls_vals[i_val+1],  cls_vals[i_val+2]
               #     if cls_vals[i_val+2] > 0.05 and cls_vals[i_val+3] > 0.05:
               #         down_outlier_flag = True
               #         continue
               elif abs(cls_vals[i_val-2] - cls_vals[i_val-1]) > 0.5*abs(cls_val - cls_vals[i_val-1]):
                  if verbose: print 'Already in large gradient region, likely fine', cls_vals[i_val-2], cls_vals[i_val-1], cls_val
                  pass
               else:
                  if verbose: print 'Need to investigate...', cls_vals[i_val-2], cls_vals[i_val-1], cls_val, cls_vals[i_val+1], cls_vals[i_val+2]
                  pass
            if i_val == 1:
               import pdb; pdb.set_trace()

            upper_limits[i_q].append(g - STEP_SIZE/2.) # FIXME, weighted mean based on distance to 0.05??
         up_outlier_flag = False
         if i_val < len_vals - 3 and cls_val > 0.05 and cls_vals[i_val-2] < 0.05 and cls_vals[i_val-1] < 0.05 and cls_vals[i_val+1] < 0.05 and cls_vals[i_val+2] < 0.05:
            if verbose: print '__-__ outlier'
            up_outlier_flag = True
            continue

         if cls_val > 0.05 and cls_vals[i_val-1] < 0.05:
            if i_val > len(cls_vals) - 3:
               if verbose: print 'At the end, will just continue'
               continue
            if abs(cls_val - cls_vals[i_val-1]) > 0.035:
               if verbose: print 'Found large jump in limit value, investigating', g
               if cls_val > cls_vals[i_val+1] and abs(cls_vals[i_val-1] - cls_vals[i_val+1]) < 0.05:
                  if verbose: print 'Next CLs value lower, marking as outlier'
                  up_outlier_flag = True
                  continue
               # elif cls_val > cls_vals[i_val+2]:
               #     if verbose: print '!!! Next-to-next CLs value lower, maybe double outlier', cls_vals[i_val-1], cls_val, cls_vals[i_val+1],  cls_vals[i_val+2]
               #     up_outlier_flag = True
               #     continue
               elif down_outlier_flag:
                  if verbose: print 'Previous point marked as downward outlier'
                  down_outlier_flag = False
                  continue
               elif abs(cls_vals[i_val-2] - cls_vals[i_val-1]) > 0.5*abs(cls_val - cls_vals[i_val-1]):
                  pass
                  if verbose: print 'Already in large gradient region, likely fine'
               elif cls_val == 0.5 or cls_val == 0. or cls_vals[i_val-1] == 0.5 or cls_vals[i_val-1] == 0.:
                  if verbose: print 'Outlier-like value, continue', cls_val
                  continue
               else:
                  print 'Need to investigate...'
                  import pdb; pdb.set_trace()
            down_outlier_flag = False
            lower_limits[i_q].append(g - STEP_SIZE/2.) # FIXME, weighted mean based on distance to 0.05??

      if not upper_limits[i_q]:
         if verbose: print 'No upper limit found, investigating...'
         if all(v>0.05 for v in cls_vals):
            if verbose: print 'All CLs values above 0.05, fine! Mass, width:', mass, width
            upper_limits[i_q].append(MAX_LIM)
         elif cls_vals[-1] > 0.05:
            if verbose: print 'Last CLs value above 0.05, so likely fine but with outlier(s)', mass, width
            upper_limits[i_q].append(MAX_LIM)
         else:
            import pdb; pdb.set_trace()
            if verbose: print 'just to stop pdb here'

      if len(lower_limits[i_q]) > 0 and i_q == 0:
         if lower_limits[i_q][0] < upper_limits[i_q][0]:
            del lower_limits[i_q][0]
         ## else:
         ##    import pdb; pdb.set_trace()
         ##    print 'just to stop pdb here'

   return upper_limits, lower_limits


import argparse
from bisect import bisect_left
from collections import namedtuple
from copy import copy
import itertools
import json
import math
from operator import itemgetter
import os

import numpy as np


