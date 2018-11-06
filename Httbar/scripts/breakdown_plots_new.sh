#! /bin/bash

set -o nounset
set -o errexit

for json in $(ls -d limits_*.json); do
		#remove "limits"
		mode_width=`echo "${json#*_}" | sed 's|.json||g'`
		ah="${mode_width%_*}"
		width="${mode_width#*_}"
		if [[ $width == M* ]]; then
				xtitle='Width_{'$ah'} (%)'
		else
				xtitle='M_{'$ah'} (GeV)'
		fi
		echo $xtitle $width $ah $mode_width
		compareLimits.py --same_points $(ls *_$mode_width.json | grep -v Theo_ | grep -v Experimental) -y 'Coupling modifier' -x "$xtitle" -t "Systematics breakdown for $ah $width" --autolabels -o plots/breakdown_$ah'_'$width.pdf
		compareLimits.py --same_points $json $(ls Theo_*_$mode_width.json) -y 'Coupling modifier' -x "$xtitle" -t "Systematics breakdown for $ah $width" --autolabels -o plots/theory_breakdown_$ah'_'$width.pdf
		compareLimits.py --same_points $json Theory_$mode_width.json XSections_$mode_width.json BinByBin_$mode_width.json -y 'Coupling modifier' -x "$xtitle" -t "Systematics breakdown for $ah $width" --autolabels -o plots/generic_breakdown_$ah'_'$width.pdf
done
