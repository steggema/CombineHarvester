#!/bin/bash
scriptdir="/afs/cern.ch/user/c/clcheng/local"
MG5dir="./"
Carddir="../Cards"

while IFS='' read -r line || [[ -n "$line" ]]; do
 case "$line" in \#*) continue ;; esac
 
 IFS=$'\t' read -ra dat <<< "$line"
 mass="${dat[0]}"
 coupling="${dat[1]}"
 width="${dat[2]}"
 echo "doing mass: ${mass} width: ${width} coupling: ${coupling}"
 python $scriptdir/Map_MG5_paramcard.py $Carddir/param_card_default.dat $Carddir/param_card.dat --mass=$mass --width=$width --coupling=$coupling --higgs="A"

 printf 'launch\n\n\nexit\n' | ./madevent   
done < "$1"
