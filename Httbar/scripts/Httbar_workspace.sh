#! /bin/bash

set -o nounset
set -o errexit

for wdir in $(ls -d ./[AH]_[1-9]*); do 
		combineTool.py -M T2W -i $wdir/* -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel
done
