#! /bin/bash

set -o nounset
set -o errexit

for json in $(ls -d limits_*.json); do
		#remove "limits"
		mode_width=`echo "${json#*_}" | sed 's|.json||g'`
		ah="${mode_width%_*}"
		width="${mode_width#*_}"
		plotLimits.py --y-title='Coupling modifier' --x-title='M_{'$ah'} (GeV)' $json -o plots/limit_$ah'_'$width'_pc' --show=exp --grid --mapping='lambda x: sqrt(x)'
done
