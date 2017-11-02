#! /bin/env bash

set -o nounset
set -o errexit

#
# Creates a single hMSSM point workspace
# Usage: make_point.sh jobid pointName ASetting HSetting
# A/H setting mini-syntax 'A/H:MASS:WIDTH'
#

jobid=$1
tagname=$2
settings1=$3
settings2=$4

torm=""
toadd=''
for setting in $settings1 $settings2; do
		IFS=':' read -r -a options <<< "$setting"
		for chan in 'll' 'lj'; do
				wmorph=temp_$chan'_widthmorph'.$setting.root
				morph_widths.py ../data/templates_$chan'_sig_'$jobid.root --single="${options[2]}" \
						--filter='gg'"${options[0]}"'*'	--nocopy --out $wmorph
				mmorph=temp_$chan'_massmorph'.$setting.root
				morph_mass.py $wmorph ../data/templates_$chan'_bkg_'$jobid.root \
						"${options[0]}" --algo NonLinearPosFractions --fortesting "${options[1]}" --out $mmorph
				toadd=$toadd' '$mmorph
				torm=$wmorph' '$torm
		done
done

hadd -f $tagname.root $toadd
rm -r $toadd $torm