#!/bin/bash

for file in $(ls /eos/user/c/clcheng/LAST/CONSTRAINTED/scaled_100/data/output_cmb_2017Jul25/[AH]_[1-9]*/[1-9]*/combined.txt.cmb); do
 sed -i '5ilumiscale rateParam * * 1' $file
 sed -i '6inuisance edit freeze lumiscale' $file
 mass=$(echo ${file#*output_cmb_2017Jul25/*/} | sed 's|/combined.txt.cmb||g')
 out=$(echo $file | sed 's|combined.txt.cmb|workspace.root|g')
 echo "Doing mass $mass at $file"
 text2workspace.py $file  --X-nuisance-function '.*_bin[0-9]*' 'expr::lumisyst("1/sqrt(@0)",lumiscale[1])' --mass=$mass 
done
