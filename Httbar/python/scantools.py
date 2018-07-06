from pdb import set_trace
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

quantiles = [-1, 0.025, 0.160, 0.5, 0.840, 0.975]
lims = ['obs', 'exp-2', 'exp-1', 'exp0', 'exp+1', 'exp+2']

def tree2dataset(limit_tree):
   # First aggregate all CLs values (with the beautiful entry name entry.limit)
   all_cls = [[] for _ in range(len(lims))]
   for entry in limit_tree:
      for i_q, quantile in enumerate(quantiles):
         if abs(entry.quantileExpected - quantile) < 0.0001:
            all_cls[i_q].append((entry.limit, entry.g))
   return all_cls

def harvest_and_outlier_removal(limit_tree, MAX_LIM = 3., STEP_SIZE = 0.01, verbose=False, plot=''):
   # Convert tree to dataset
   all_cls = tree2dataset(limit_tree)
   upper_limits = [[] for _ in range(len(lims))]
   lower_limits = [[] for _ in range(len(lims))]
   limit_previous = [1.]*len(lims)

   # Then outlier removal and  limit determination
   for i_q, quantile in enumerate(quantiles):
      down_outlier_flag = False
      up_outlier_flag = False
      cls_vals_plus_g = [(i, j) for i, j in all_cls[i_q] if i >= 0. and i != 0.5 and i != 0.0]
      cls_vals = [i for i, _ in cls_vals_plus_g]
      len_vals = len(cls_vals)
      if plot:
         plt.plot(
            [i for _, i in cls_vals_plus_g], cls_vals, label=lims[i_q], 
            linestyle='None', marker='o', markersize=5, 
            )

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
         ##    import pdb; pdbs.set_trace()
         ##    print 'just to stop pdb here'

   if plot:
      plt.xlabel('g')
      plt.ylabel('CLs')
      plt.yscale('log')
      plt.ylim(10**-2, 3)
      plt.grid(which='both', axis='both')
      plt.legend(loc='best')
      #plt.gca().xaxis.set_major_locator(MultipleLocator(0.2))
      #plt.gca().xaxis.set_minor_locator(MultipleLocator(0.05))
      plt.savefig(plot)
      plt.clf()

   return upper_limits, lower_limits


#
# Mostly copied from Andrey's algorithm
#
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


Crossing = namedtuple('Crossing', ['g', 'up'])
## Crossing.__doc__ = """Value of g and sign of derivative of CLs(g).
## 
## An auxiliary class to aggreate value of g at which CL(g) crosses a
## threshold and the direction of the crossing, i.e. the sign of the
## derivative of CLs(g).  Attribute up is expected to be set to True
## if the derivative is positive and to False otherwise.
## """

class PointWithDerivatives:
    """Auxiliary class describing a point with derivatives.
    
    Used in method _clean_series.  Contains a coordinate and
    (finite) derivatives of a function to the left and to the right
    of that point.
    """
    
    __slots__ = ['x', 'der_left', 'der_right']
    
    def __init__(self, x, der_left, der_right):
        """Initialize from x coordinate and two derivatives."""
        self.x = x
        self.der_left = der_left
        self.der_right = der_right
    
    @property
    def der_scale(self):
        """Return characteristic scale of derivatives."""
        return min(abs(self.der_left), abs(self.der_right))
    
    @property
    def is_spike(self):
        """Check if derivative changes sign at this point."""
        return (self.der_left > 0.) != (self.der_right > 0.)

def clean_series(x, y, y_range=(-np.inf, np.inf), der_cutoff=3., knn=5):
    """Clean y(x) series of spikes and constrain it to a y range.
    
    Remove points for which y coordinate falls outside of the given
    range.  Find and remove spikes, which are defined as points at
    which the (finite) derivative changes sign and is large in
    value.  The latter condition is evaluated by comparing the scale
    of the derivative with the median one computed among given
    number of nearest neighbours; their ratio should be above the
    given cutoff value.
    
    Arguments:
        x, y:  Arrays with x and y coordinates.  Must be sorted in
            x coordinate.
        y_range:  Allowed range for y values.
        der_cutoff:  Minimal ratio of the scale of the derivative to
            the local median one to consider the point a spike.
        knn:  Number of nearest neighbours to use in the computation
            of the median scale of the derivative.
    
    Return value:
        Tuple of filtered arrays x and y.
    
    This method is used by _find_crossings to clean CLs(g).
    """
    
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Identify points that lay outside of the y range
    out_of_range = np.logical_or(y < y_range[0], y > y_range[1])
    
    # See if any points survive the selection
    if len(y) - np.sum(out_of_range) == 0:
        return [], []
    
    
    # Look for spikes
    spikes = np.zeros(len(x), dtype=bool)
    
    if der_cutoff > 0:
        
        # Construct a list of points with left and right
        # derivatives
        points = []
        derivative = (y[1:] - y[:-1]) / (x[1:] - x[:-1])
        
        for i in range(1, len(x) - 1):
            points.append((
                i,
                PointWithDerivatives(
                    x[i], derivative[i - 1], derivative[i]
                )
            ))
        
        
        # Loop over identified points
        for i in range(len(points)):
            cur_index, cur_point = points[i]
            
            # Find up to knn closest neighbours on each side.  The
            # current point is included in the list of neighbours.
            neighbours = []
            
            for j in range(max(i - knn, 0), min(i + knn + 1, len(points))):
                neighbours.append(points[j][1])
            
            neighbours.sort(key=lambda p: abs(p.x - cur_point.x))
            
            
            # Compute median scale of the derivative for knn nearest
            # neighbours
            der_scales = [n.der_scale for n in neighbours]
            median_der_scale = np.median(der_scales[:knn])
            
            
            # Check if there is a spike above the threshold at the
            # current point
            if cur_point.is_spike and cur_point.der_scale > der_cutoff * median_der_scale:
                spikes[cur_index] = True
        
        
        # A sanity check: make sure that the fraction of detected
        # points with spikes with respect to all points in the
        # allowed range is small
        num_spikes = np.sum(np.logical_and(spikes, np.logical_not(out_of_range)))
        num_probed =  len(x) - np.sum(out_of_range)
        
        if num_spikes / num_probed > 0.05:
            raise RuntimeError(
                'Cleaning algorithm has rejected {} / {} points as spikes.'.format(
                    num_spikes, num_probed
                )
            )
    
    
    # Return cleaned series
    masked = np.logical_or(out_of_range, spikes)
    return x[np.logical_not(masked)], y[np.logical_not(masked)]

def find_crossings(x, y, level=0.05):
    """Solve y(x) = level for x.
    
    Find all solutions.  Use a linear approximation to interpolate
    between the given points.
    
    Arguments:
        x, y:  Arrays with x and y coordinates.  Must be sorted in
            x coordinate.
        level:  Desired value for y(x).
    
    Return value:
        List of objects of type Crossing.
    """
    x, y = clean_series(x, y, y_range=(level / 5, level * 5))
    crossings = []
    
    for i in range(len(y) - 1):
        if (y[i] > level) != (y[i + 1] > level) or y[i] == level:
            # Function crosses the given level within the current
            # segment.  Find the crossing point using linear
            # approximation.
            x_cross = x[i] + (x[i + 1] - x[i]) / (y[i + 1] - y[i]) * (level - y[i])
            
            # Determine the sign of the derivative
            upcrossing = ((y[i + 1] > y[i]) == (x[i + 1] > x[i]))
            crossings.append(Crossing(x_cross, upcrossing))
    
    return crossings



def andrey_harvest_and_outlier_removal(limit_tree, verbose=False, plot=''):
   # Convert tree to dataset
   all_cls = tree2dataset(limit_tree)
   upper_limits = [[] for _ in range(len(lims))]
   lower_limits = [[] for _ in range(len(lims))]

   # Then outlier removal and  limit determination
   for i_q, quantile in enumerate(quantiles):
      #cls_vals_plus_g = [(i, j) for i, j in all_cls[i_q] if i >= 0. and i != 0.5 and i != 0.0]
      cls_vals = np.array([i for i, _ in all_cls[i_q]])
      g_vals = np.array([i for _, i in all_cls[i_q]])
      #_plus_g = [(i, j) for i, j in all_cls[i_q] if i >= 0. and i != 0.5 and i != 0.0]
      if plot:
         plt.plot(
            g_vals, cls_vals, label=lims[i_q], 
            linestyle='None', marker='o', markersize=5, 
            )
      
      # Find crossings for the current mass point and construct a
      # matching to crossings for the previous mass point
      #set_trace()
      crossings = find_crossings(g_vals, cls_vals)
      upper_limits[i_q] = [c.g for c in crossings if not c.up]
      lower_limits[i_q] = [c.g for c in crossings if c.up]
      if len(crossings) not in {1,3} or len(upper_limits[i_q]) > 2 or len(lower_limits[i_q]) > 1:
         print 'Found inconsistent number of crossings (%d) for %s. Please check' \
            ' manually, plot dumped in tmp.png' % (len(crossings), lims[i_q])
         plt.xlabel('g')
         plt.ylabel('CLs')
         plt.yscale('log')
         plt.ylim(10**-2, 3)
         plt.grid(which='both', axis='both')
         plt.legend(loc='best')
         plt.savefig('tmp.png')
         #set_trace()
         #upper_limits[i_q] = []
         #lower_limits[i_q] = []
         continue

   if plot:
      plt.xlabel('g')
      plt.ylabel('CLs')
      plt.yscale('log')
      plt.ylim(10**-2, 3)
      plt.grid(which='both', axis='both')
      plt.legend(loc='best')
      #plt.gca().xaxis.set_major_locator(MultipleLocator(0.2))
      #plt.gca().xaxis.set_minor_locator(MultipleLocator(0.05))
      plt.savefig(plot)
      plt.clf()
   
   return upper_limits, lower_limits
