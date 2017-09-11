#!/bin/bash
higgs=("A" "H")

basedir="$CMSSW_BASE/src/CombineHarvester/Httbar/results/"
masses=( "400" "450" "500" "550" "600" "650" "700" "750" )
file="workspace.root"
cd $basedir


for h in "${higgs[@]}"; do
for mass in "${masses[@]}"; do
input="/afs/cern.ch/work/c/clcheng/LAST/data/output_cmb_2017Jul25/width_${h}_${mass}.json:exp0:Title=\"median_nominal\",MarkerSize=0.4,LineColor=2,MarkerStyle=21,MarkerColor=2 "
input="$input /afs/cern.ch/work/c/clcheng/LAST/data/output_cmb_2017Jul25_noBBB/width_${h}_${mass}.json:exp0:Title=\"median_nominal_noBBB\",MarkerSize=0.4,LineColor=2,MarkerStyle=34,MarkerColor=2 "
input="$input /afs/cern.ch/work/c/clcheng/LAST/scaled_100/data/output_cmb_2017Jul25/width_${h}_${mass}.json:exp0:Title=\"median_100pb-1\",MarkerSize=0.4,LineColor=3,MarkerStyle=21,MarkerColor=3 "
input="$input /afs/cern.ch/work/c/clcheng/LAST/scaled_100/data/output_cmb_2017Jul25_noBBB/width_${h}_${mass}.json:exp0:Title=\"median_100pb-1_noBBB\",MarkerSize=0.4,LineColor=3,MarkerStyle=34,MarkerColor=3 "
input="$input /afs/cern.ch/work/c/clcheng/LAST/scaled_1000/data/output_cmb_2017Jul25/width_${h}_${mass}.json:exp0:Title=\"median_1000pb-1\",MarkerSize=0.4,LineColor=4,MarkerStyle=21,MarkerColor=4 "
input="$input /afs/cern.ch/work/c/clcheng/LAST/scaled_1000/data/output_cmb_2017Jul25_noBBB/width_${h}_${mass}.json:exp0:Title=\"median_1000pb-1_noBBB\",MarkerSize=0.4,LineColor=4,MarkerStyle=34,MarkerColor=4 "
  
   echo "Input: $input"
  python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotLimits.py --auto-style obs,exp --y-title='Coupling modifier' --x-title="width (pc)" $input ${basedir}/Analysis/shortened/hMSSM_${h}_${mass}_coupling-width_Inc.json:exp0:Title=\"hMSSM\",MarkerStyle=5,MarkerColor=1,LineColor=1,LineWidth=1,MarkerSize=0.3 ${basedir}/Analysis/shortened/hMSSM_${h}_${mass}_coupling-width_Dec.json:exp0:Title=\"hMSSM\",MarkerStyle=5,MarkerColor=1,LineColor=1,LineWidth=1,MarkerSize=0.3 -o All_Width_${h}_$mass --show=exp 
done
done
cd $CMSSW_BASE/src/CombineHarvester/Httbar/myscripts  
