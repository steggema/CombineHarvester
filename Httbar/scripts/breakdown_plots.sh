#! /bin/bash

set -o nounset
set -o errexit

for json in $(ls -d XSections_*.json); do
		#remove "limits"
		mode_width=`echo "${json#*_}" | sed 's|.json||g'`
		ah="${mode_width%_*}"
		width="${mode_width#*_}"
		if [[ $width == M* ]]; then
				xtitle='Width_{'$ah'} (%)'
		else
				xtitle='M_{'$ah'} (GeV)'
		fi
		compareLimits.py $(ls *_$mode_width.json | grep -v Theo_ | grep -v Experimental) -y 'Coupling modifier' -x 'M_{'$ah'} (GeV)' -t "Systematics breakdown for $ah $width" --autolabels -o plots/breakdown_$ah'_'$width.pdf
		compareLimits.py $json $(ls Theo_*_$mode_width.json) -y 'Coupling modifier' -x 'M_{'$ah'} (GeV)' -t "Systematics breakdown for $ah $width" --autolabels -o plots/theory_breakdown_$ah'_'$width.pdf
		compareLimits.py $json Theory_$mode_width.json Experimental_$mode_width.json XSections_$mode_width.json BinByBin_$mode_width.json -y 'Coupling modifier' -x 'M_{'$ah'} (GeV)' -t "Systematics breakdown for $ah $width" --autolabels -o plots/generic_breakdown_$ah'_'$width.pdf
done
