#! /bin/bash

set -o nounset
set -o errexit

for wdir in $(ls -d [AH]_[0-9]*); do 
	cd $wdir
	mkdir -p impacts
	mkdir -p impact_plots
	for subdir in $(ls -d [0-9]*); do
		cd impacts
		combineTool.py -M Impacts -d ../$subdir/workspace.root -m $subdir --doInitialFit --robustFit 1  -t -1 --expectSignal=1  --toysFreq
		combineTool.py -M Impacts -d ../$subdir/workspace.root -m $subdir --robustFit 1 --doFits --parallel 4  -t -1 --expectSignal=1  --toysFreq
		combineTool.py -M Impacts -d ../$subdir/workspace.root -m $subdir -o impacts_$subdir.json
		plotImpacts.py -i impacts_$subdir.json -o impacts_$subdir
		mv impacts_${subdir}.* ../impact_plots/
		cd ..
	done
	cd ..
done
