#!/bin/bash
script="$CMSSW_BASE/src/CombineHarvester/Httbar/myscripts/Httbar_clcheng/SusHi/scripts/Map_2HDMC_in.py"
dir2HDMC="/afs/cern.ch/user/s/steggema/Software/2HDMC-1.7.0"
dirSusHi="/afs/cern.ch/user/s/steggema/Software/SusHi-1.6.1/bin"
dirSusHiCard='/afs/cern.ch/user/s/steggema/Software/SusHi-1.6.1/example'
SusHiCard="2HDMC_physicalbasis.in"

lo="2" # order ggh, bbh: -1 = off, 0 = LO, 1 = NLO, 2 = NNLO, 3 = N3LO
model="2" # model: 0 = SM, 1 = MSSM, 2 = 2HDM, 3 = NMSSM
h="12" # 11 = h, 12 = H, 21 = A
mh="125.09" # mass of lightest Higgs boson
scale="0.5"  # factorization and renormalization scale relative to the Higgs mass mh

while IFS='' read -r line || [[ -n "$line" ]]; do
 case "$line" in \#*) continue ;; esac
 IFS=$'\t' read -ra dat <<< "$line"
 mass="${dat[0]}"
 tanb="${dat[1]}"
 ntanb=`echo "${tanb}" | sed 's|\.|p|g' `
 echo "doing mass: ${mass} tanb: ${tanb} ntanb: ${ntanb}"
 cd $dir2HDMC
 ./CalcHMSSM $mh $mass $tanb > result
 python ${script} ${dir2HDMC}/result "$dirSusHiCard/$SusHiCard" --gghlo=$lo --bbhlo=$lo --model=$model --higgs=$h --gghscale=$scale
 cd $dirSusHi
 if [ ! -f ./map/tanb_${ntanb}_${mass} ]; then
 ./sushi.2HDMC ../example/$SusHiCard ./map/tanb_${ntanb}_${mass} 
 fi
done < "$1"
