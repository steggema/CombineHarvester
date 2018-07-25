#! /bin/bash

filter=${4:-"UNSET"}
echo 'filter - '$filter

set -o nounset
set -o errexit

tarfile=$1
mass=$2
coupling=$3
filename="${tarfile%.*}"

echo 'creating directory'
mkdir -p impacts_$filename
cp $tarfile impacts_$filename/.
cd impacts_$filename
echo 'untarring files'
tar -xf $tarfile

echo 'initial fit'
combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --cminPreScan --X-rtd MINIMIZER_analytic --doInitialFit --robustFit 1  --expectSignal=1 --setParameters g=$coupling --freezeParameters g --redefineSignalPOIs r &> initial_fit.log
if [ "$filter" == "UNSET" ]; then
		echo 'impacts'
		combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --X-rtd MINIMIZER_analytic  --robustFit 1 --cminPreScan --doFits --parallel 8 --setParameters g=$coupling --freezeParameters g --redefineSignalPOIs r > impacts.log
		echo 'making json'
		combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --redefineSignalPOIs r -o impacts_$mass.json
else
		echo 'impacts'
		combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --X-rtd MINIMIZER_analytic  --robustFit 1 --cminPreScan --doFits --parallel 8 --setParameters g=$coupling --freezeParameters g --redefineSignalPOIs r --filter=$filter &> impacts.log		
		echo 'making json'
		combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --redefineSignalPOIs r -o impacts_$mass.json --filter=$filter
fi
echo 'making plots'
plotImpacts.py -i impacts_$mass.json -o impacts_$mass
cd -