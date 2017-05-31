#! /bin/bash

set -o nounset
set -o errexit

for json in $(ls -d limits_*.json); do
		#remove "limits"
		mode_width=`echo "${json#*_}" | sed 's|.json||g'`
		ah="${mode_width%_*}"
		width="${mode_width#*_}"
		plotLimits.py --y-title='Coupling modifier' --x-title='M_{'$ah'} (GeV)' $json -o plots/limit_$ah'_'$width'_pc' --show=exp  #--grid --mapping='lambda x: sqrt(x)'
		compareLimits.py $(ls *_$mode_width.json | grep -v Theo_ | grep -v Experimental) -y 'Coupling modifier' -x 'M_{'$ah'} (GeV)' -t "Systematics breakdown for $ah $width" --autolabels -o plots/breakdown_$ah'_'$width'_pc'.pdf
		compareLimits.py $json $(ls Theo_*_$mode_width.json) -y 'Coupling modifier' -x 'M_{'$ah'} (GeV)' -t "Systematics breakdown for $ah $width" --autolabels -o plots/theory_breakdown_$ah'_'$width'_pc'.pdf
		compareLimits.py $json Theory_$mode_width.json Experimental_$mode_width.json XSections_$mode_width.json BinByBin_$mode_width.json -y 'Coupling modifier' -x 'M_{'$ah'} (GeV)' -t "Systematics breakdown for $ah $width" --autolabels -o plots/generic_breakdown_$ah'_'$width'_pc'.pdf
done
