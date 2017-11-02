#! /bin/bash

set -o nounset
set -o errexit

#d $CMSSW_BASE/src/CombineHarvester/Httbar/results/output_cmb_2017Jul20/
# combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --minimizerTolerance=0.1 --minimizerStrategy=0 --job-mode lxbatch --sub-opts='-q 8nh' --task-name AsymLim2 --merge 10 --dry-run
combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --minimizerTolerance=0.0001 --minimizerStrategy=2 --parallel 10 $@

