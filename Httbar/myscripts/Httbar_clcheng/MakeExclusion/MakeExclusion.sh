#!/bin/bash
limitdir="/afs/cern.ch/work/c/clcheng/LAST/scaled_1000/data/output_cmb_2017Jul25"
hMSSMdir="$CMSSW_BASE/src/CombineHarvester/Httbar/myscripts/Httbar_clcheng/MakeExclusion/hMSSM_SusHi/"
scriptdir="$CMSSW_BASE/src/CombineHarvester/Httbar/myscripts/Httbar_clcheng/MakeExclusion"
refdir="$CMSSW_BASE/src/CombineHarvester/Httbar/myscripts/Httbar_clcheng/SusHi/results/"
higgs=("A" "H")

python $CMSSW_BASE/src/CombineHarvester/Httbar/myscripts/limit_jsons_in_width.py $limitdir -o $limitdir
echo "json files for coupling modifier against width created"
cd $limitdir
for h in "${higgs[@]}"; do
for json in $(ls -d width_${h}_*.json); do
 mh=$(echo "${json#width_*_}" | sed 's|.json||g')
 input1=""
 input2=""
 style=':exp0:Title="hMSSM",LineWidth=2,LineColor=4,MarkerStyle=0,MarkerColor=4'
 echo "$json"
 for json2 in $(ls -d $hMSSMdir/hMSSM_${h}_${mh}_coupling-width_*.json); do
  input1="$input1 $json2$style"
  input2="$input2 $json2"
 done
 cd $limitdir
 echo "Using $input2"
 if [ "$h" = "A" ]
 then
  mask=3.74
 elif [ "$h" = "H" ]
 then
  mask=5.56
 fi
 python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotLimits.py --y-title='95% CL_{s} limit on coupling modifier' --x-title="width [pc]" "$limitdir/$json" $input1  -o width_${h}_${mh} --show=exp --title-right='35.9 fb^{-1},#sqrt{s} = 13TeV' --mask=$mask
 cd $limitdir
done
done

cd $limitdir

for h in "${higgs[@]}"; do
input=$(ls -d width_${h}_*.json)
python $scriptdir/exclude_jsons.py $input  --ref=$refdir/SusHi_m${h}_out.txt -o=$limitdir --higgs=$h
python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotLimits.py --y-title='tan#beta' --x-title="m_{${h}} [GeV]" $limitdir/limit_m${h}_tanb.json  --shade -o m${h}_tanb_exclusion_limit --show=exp --title-right='35.9 fb^{-1},#sqrt{s} = 13 TeV, all limits at 95% CL' --ymax=2.5

done


cd $scriptdir
