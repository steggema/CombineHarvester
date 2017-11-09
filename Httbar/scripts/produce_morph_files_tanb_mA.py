#!/usr/bin/env python

'''Given tan beta and mA values, produces combined datacard with morphed masses
and widths, using SusHi/2HDMC results as input.
'''

import os
import pickle
from argparse import ArgumentParser
import shutil
from glob import glob
from pdb import set_trace

def syscall(cmd):
	print 'Executing: %s' % cmd
	retval = os.system(cmd)
	if retval != 0:
		raise RuntimeError('Command failed!')

parser = ArgumentParser()
parser.add_argument('jobid')
parser.add_argument('mA', type=int)
parser.add_argument('tanb')
parser.add_argument('input_sushi')
parser.add_argument('--blind', action='store_true')
# parser.add_argument('inputs_bkg', help='comma separated list of bkg input files. Same order required as for signal files')
# parser.add_argument('outfile')
args = parser.parse_args()

val2name = lambda x: str(x).replace('.','p').replace('p0','')
mA = args.mA
tanb = args.tanb
# inputs_sig = args.inputs_sig.split(',')
# inputs_bkg = args.inputs_bkg.split(',')

mH = mA
widthH = 0.
widthA = 0.

with open(args.input_sushi) as sushi_pkl:
	mapping = pickle.load(sushi_pkl)
	values = [d for d in mapping.values() if d['m_A'] == mA and d['tan(beta)'] == eval(tanb)]
	
	if len(values) == 0:
		raise RuntimeError('No entry found for mA and tan(beta)', mA, tanb)
	if len(values) > 1:
		print 'Multiple entries found for mA and tan(beta)', mA, tanb, 'picking first'
	
	values = values[0]
	mH = int(round(float(values['m_H'])))
	# Widths are relative and in per cent
	widthA = round(float(values['A_width'])/mA*100., 1)
	widthH = round(float(values['H_width'])/mH*100., 1)
	
	print 'For mA =', mA, 'tan(beta) =', tanb, 'obtain:'
	print '  widthA =', widthA
	print '  widthH =', widthH
	print '  mH =', mH
	if widthH < 1. or widthA < 1.:
		print 'LIMITING WIDTH TO 1%'
		widthA = max(widthA, 1.)
		widthH = max(widthH, 1.)
	
	syscall('make_point.sh {} TESTME A:{}:{} H:{}:{}'.format(args.jobid, mA, widthA, mH, widthH))
	syscall(
		'hadd -f templates_ALL_POINT.root TESTME.root '
		'%s/src/CombineHarvester/Httbar/data/templates_l?_bkg_2017Aug04.root' % os.environ['CMSSW_BASE']
		)
	print '\n\ncreating workspace\n\n'
	syscall((
			'setup_common.py POINT --indir=./ --limitdir=./'
			' --masses="A:{},H:{}" --widths="A:{},H:{}"').format(
			mA, mH, val2name(widthA), val2name(widthH)
			))
	syscall((
			'combineTool.py -M T2W -i A_{}_{}_H_{}_{} -o workspace.root -P CombineHarvester'
			'.CombineTools.InterferenceModel:interferenceModel').format(
			val2name(widthA), mA, val2name(widthH), mH
			))
	print '\n\nRunning LIMIT\n\n'
	syscall((
			'combineTool.py -M Asymptotic -d A_{}_{}_H_{}_{}/workspace.root --there -n'
			' .limit --minimizerTolerance=0.0001 --minimizerStrategy=2').format(
			val2name(widthA), mA, val2name(widthH), mH, '--run blind' if args.blind else ''
			))
	syscall((
			'combineTool.py -M CollectLimits '
			'A_{}_{}_H_{}_{}/higgsCombine.limit.Asymptotic.mH120.root').format(
			val2name(widthA), mA, val2name(widthH), mH, '--run blind' if args.blind else ''
			))
shutil.move('limits.json', 'mA%d_tanb%s.json' % (mA, tanb))
shutil.rmtree(
        'A_{}_{}_H_{}_{}'.format(
                val2name(widthA), mA, val2name(widthH), mH, '--run blind' if args.blind else ''
                )
        )
for fname in glob('*.root'):
	os.remove(fname)

