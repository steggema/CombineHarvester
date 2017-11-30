#! /bin/bash

set -o nounset
set -o errexit

tarfile=$1
mass=$2
filename="${tarfile%.*}"

mkdir -p impacts_$filename
cp $tarfile impacts_$filename/.
tar -xf $tarfile
combineTool.py -M Impacts -d */$mass/workspace.root -m $mass --doInitialFit --robustFit 1 -t -1 --expectSignal=1
combineTool.py -M Impacts -d ../$mass/workspace.root -m $mass --robustFit 1 --doFits --parallel 8 -t -1 --expectSignal=1
combineTool.py -M Impacts -d ../$mass/workspace.root -m $mass -o impacts_$mass.json
plotImpacts.py -i impacts_$mass.json -o impacts_$mass
