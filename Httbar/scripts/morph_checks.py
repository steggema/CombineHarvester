#!/usr/bin/env python

'''
Make morph plots, replace makefile
'''

import os
import pickle
from argparse import ArgumentParser
import shutil
from glob import glob
from pdb import set_trace

parser = ArgumentParser()
parser.add_argument('jobid')
parser.add_argument('mass')
args = parser.parse_args()

def syscall(cmd):
   print 'Executing: %s' % cmd
   retval = os.system(cmd)
   if retval != 0:
      raise RuntimeError('Command failed! %s' % cmd)

checkdir = '%s/src/CombineHarvester/Httbar/results/%s/checks' % (os.environ['CMSSW_BASE'], args.jobid)
if not os.path.isdir(checkdir):
   os.makedirs(checkdir)

for chan in ['ll','lj']:
   # get the FullSim point
   syscall('morph_mass.py ../data/templates_{CHAN}_sig_{JOBID}.root  ../data/templates_{CHAN}_bkg_{JOBID}.root A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single {MASS} --nosystematics'.format(CHAN=chan, JOBID=args.jobid, MASS=args.mass))
   
   # make the mass morphed of the same point
   syscall('morph_mass.py ../data/templates_{CHAN}_sig_{JOBID}.root  ../data/templates_{CHAN}_bkg_{JOBID}.root A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting {MASS} --nosystematics'.format(CHAN=chan, JOBID=args.jobid, MASS=args.mass))
   
   # morph widths from the extracted 1D FullSim shapes
   syscall('morph_widths.py ../data/templates_{CHAN}_sig_{JOBID}_A_M{MASS}.root --forchecks'.format(CHAN=chan, JOBID=args.jobid, MASS=args.mass))
   
   ## double morphin, first width
   syscall('morph_widths.py ../data/templates_{CHAN}_sig_{JOBID}.root --forchecks  --nocopy --out ../data/templates_{CHAN}_sig_{JOBID}_widthmorphed.root'.format(CHAN=chan, JOBID=args.jobid))
   # then mass
   syscall('morph_mass.py ../data/templates_{CHAN}_sig_{JOBID}_widthmorphed.root  ../data/templates_{CHAN}_bkg_{JOBID}.root A --algo NonLinearPosFractions --fortesting {MASS} --nosystematics --out ../data/templates_{CHAN}_sig_{JOBID}_A_M{MASS}_doublemorphed.root'.format(CHAN=chan, JOBID=args.jobid, MASS=args.mass))
   
   # make plots
   syscall('plot_morph_check.py ../data/templates_{CHAN}_sig_{JOBID}_A_M{MASS}.root ../data/templates_{CHAN}_sig_{JOBID}_A_mass_morph_testing.root ../data/templates_{CHAN}_sig_{JOBID}_A_M{MASS}_width_morphed.root ../data/templates_{CHAN}_sig_{JOBID}_A_M{MASS}_doublemorphed.root {CHECKDIR} --mass={MASS}'.format(CHAN=chan, JOBID=args.jobid, MASS=args.mass, CHECKDIR=checkdir))
