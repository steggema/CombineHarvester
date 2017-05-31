#! /bin/bash

set -o nounset
set -o errexit

for wdir in $(ls -d [AH]_[0-9]*); do 
		combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --minimizerTolerance=0.0001 --minimizerStrategy=2 --parallel 8 $@
done
