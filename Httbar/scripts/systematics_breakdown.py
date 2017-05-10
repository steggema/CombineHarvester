#!/usr/bin/env python
from argparse import ArgumentParser
from pdb import set_trace
from fnmatch import fnmatch
from glob import glob
import shutil
import os
from subprocess import Popen, PIPE, STDOUT
from pdb import set_trace

def call(cmd):
	proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
	stdout, nothing = proc.communicate()    
	return proc.wait()

def backup(src):
	ret = '%s.bak' % src
	shutil.copyfile(src, ret)
	return ret

def unbackup(src):
	if not src.endswith('.bak'):
		raise ValueError('%s is not a backup file!')
	shutil.copyfile(src, src[:-4])
	return src[:-4]

def tag(src, value):
	dname, bname = os.path.dirname(src), os.path.basename(src)
	ret = '%s/%s_%s' % (dname, value, bname)
	shutil.copyfile(src, ret)
	return ret

parser = ArgumentParser()
parser.add_argument('--run', choices=['blind'])
args = parser.parse_args()

txts = glob('[AH]_[0-9]*/000/combined.txt.cmb')# % args.jobid)
if not txts:
	raise RuntimeError('I could not find any datacard available')
txt = txts[0]

#get all nuisances
nuisances = set()
with open(txt) as card:
	for line in card:
		#the space in ' param ' is important to not select spurious things
		if any((i in line for i in [' shape ', ' lnN ', ' param '])):
			nuisances.add(line.split()[0])

groups = {
	'BinByBin' 	: ['*_TT_bin_[0-9]*'],
	'BTag'     	: ['CMS_*_b_13TeV'],
	'Leptons'  	: ['CMS_eff_[em]', 'CMS_eff_trigger_[em]'],
	'JetMET'   	: ['CMS_*_j_13TeV', 'CMS_METunclustered_13TeV'],
	'XSections' : ['CMS_httbar_*_13TeV'],
	'QCDNorm'   : ['CMS_httbar_*_QCDNorm'],
	'PU'        : ['CMS_pileup'],
	'Theory'    : ['*_TT', 'TMass', 'pdf'],	
}

#backup files
backed_up = [backup(i) for i in glob('[AH]_[0-9]*/000/higgsCombine.limit.Asymptotic.*.root')]

#run limits
for group, names in groups.iteritems():
	print 'running for group: ', group
	tofreeze = [i for i in nuisances if any((fnmatch(i, j) for j in names))]
	retval = call(
		('combineTool.py -M Asymptotic -m 400:750:50 --freezeNuisances MH,%s'
		' -d */*/workspace.root --there -n .limit --parallel 8 %s') % \
			(','.join(tofreeze), '--run blind' if args.run == 'blind' else '')
		)
	if retval != 0:
		raise RuntimeError('combineTool.py crashed with exit code %d' % retval)
	#tag outputs
	[tag(i, group) for i in glob('[AH]_[0-9]*/000/higgsCombine.limit.Asymptotic.*.root')]
	retval = call(
		'combineTool.py -M CollectLimits */*/{0}_*.limit.* --use-dirs -o {0}.json'.format(group)
		)
	if retval != 0:
		raise RuntimeError('limit harvesting crashed with exit code %d' % retval)

[unbackup(i) for i in backed_up]
