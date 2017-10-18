#! /bin/bash

set -o nounset
set -o errexit

for wdir in 'A_2p5/' 'A_50/'; do #$(ls -d [AH]_[0-9]*); do  #For full set run with this takes long (> 15h)
	cd $wdir
	mkdir -p impacts
	mkdir -p impact_plots
	for subdir in 400 750; do #$(ls -d [0-9]*); do
		cd impacts
		echo 'sample: '$wdir' subdir:'$subdir
		combineTool.py -M Impacts -d ../$subdir/workspace.root -m $subdir --doInitialFit --robustFit 1 -t -1 --expectSignal=1
		combineTool.py -M Impacts -d ../$subdir/workspace.root -m $subdir --robustFit 1 --doFits --parallel 8 -t -1 --expectSignal=1
		combineTool.py -M Impacts -d ../$subdir/workspace.root -m $subdir -o impacts_$subdir.json
		plotImpacts.py -i impacts_$subdir.json -o impacts_$subdir
		mv impacts_${subdir}.* ../impact_plots/
		cd ..
	done
	cd ..
done
