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
	code = proc.wait()
	if code != 0:
		raise RuntimeError(
			'\n\nCommand: %s \n\nFailed with code %d and error \n\n %s' \
				% (cmd, code, nothing)
			)
	return code

def backup(src):
	ret = '%s.bak' % src
	shutil.move(src, ret)
	return ret

def unbackup(src):
	if not src.endswith('.bak'):
		raise ValueError('%s is not a backup file!')
	shutil.move(src, src[:-4])
	return src[:-4]

def tag(src, value):
	dname, bname = os.path.dirname(src), os.path.basename(src)
	ret = '%s/%s_%s' % (dname, value, bname)
	shutil.move(src, ret)
	return ret

parser = ArgumentParser()
parser.add_argument('--run', choices=['blind'])
parser.add_argument('--masses', default='[0-9][0-9][0-9]', help='posix-regex for the masses to use')
args = parser.parse_args()

txts = glob('[AH]_[0-9]*/%s/combined.txt.cmb' % args.masses)# % args.jobid)
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
	'BinByBin' 	: ['*_MCstatBin[0-9]*'],
	'BTag'     	: ['CMS_*_b_13TeV'],
	'Leptons'  	: ['CMS_eff_[em]', 'CMS_eff_trigger_[em]'],
	'JetMET'   	: ['CMS_*_j_13TeV', 'CMS_METunclustered_13TeV'],
	'XSections' : ['CMS_httbar_*_13TeV'],
	'QCDNorm'   : ['CMS_httbar_QCD*Norm'],
	'PU'        : ['CMS_pileup'],
	'Theory'    : ['*_TT', 'TMass', 'pdf'],	
	'Theo_TMass': ['TMass'],	
	'Theo_pdf'  : ['CMS_httbar_PDF_alphaS', 'CMS_httbar_PDF_1', 'CMS_httbar_PDF_2'],	
	'Theo_HigherOrders' : ['*_TT'],	
}
groups['Experimental'] = groups['BTag']+groups['Leptons']+groups['JetMET']+groups['PU']+groups['QCDNorm']

class Backup:
	def __init__(self, flist):
		self.backed_up = [backup(i) for i in flist]
		print 'backed up %d files' % len(self.backed_up)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		[unbackup(i) for i in self.backed_up]
		print 'restored %d files' % len(self.backed_up)
		if isinstance(value, Exception):
			raise value

#backup files
#backed_up = [backup(i) for i in glob('[AH]_[0-9]*/000/higgsCombine.limit.AsymptoticLimits.*.root')]

with Backup(glob('[AH]_[0-9]*/[0-9][0-9][0-9]/higgsCombine.limit.AsymptoticLimits.*.root')) as back:
	#run limits
	for group, names in groups.iteritems():
		print 'running for group: ', group
		tofreeze = [i for i in nuisances if any((fnmatch(i, j) for j in names))]
		if not tofreeze:
			raise RuntimeError('I could not find any nuisance matching the group %s (%s)' % (group, ', '.join(names)))
		print 'Run', 'combineTool.py -M AsymptoticLimits --freezeNuisances {freeze} -d */{masses}/workspace.root --there -n .limit --parallel 8 {opts}'.format(
				freeze=','.join(tofreeze),
				opts='--run blind' if args.run == 'blind' else '',
				masses = args.masses
				)
		call(
			('combineTool.py -M AsymptoticLimits --freezeNuisances {freeze}'
			 ' -d */{masses}/workspace.root --there -n .limit --parallel 8 {opts}').format(
				freeze=','.join(tofreeze),
				opts='--run blind' if args.run == 'blind' else '',
				masses = args.masses
				)
			)
	  #tag outputs
		[tag(i, group) for i in glob('[AH]_[0-9]*/%s/higgsCombine.limit.AsymptoticLimits.*.root' % args.masses)]
		call(
			'combineTool.py -M CollectLimits */*/{0}_*.limit.* --use-dirs -o {0}.json'.format(group)
			)

#[unbackup(i) for i in backed_up]
