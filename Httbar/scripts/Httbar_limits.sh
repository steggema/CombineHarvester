#! /bin/bash

set -o nounset
set -o errexit

#for wdir in $(ls -d [AH]_[0-9]*); do 
combineTool.py -M AsymptoticLimits -d */*/workspace.root --there -n .limit --parallel 10 --rMin=0 --rMax=4 $@
#done
