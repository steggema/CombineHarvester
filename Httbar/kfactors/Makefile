2HDMC=~/Software/2HDMC-1.7.0/CalcHMSSM
SusHi=~/Software/SusHi-1.6.1/bin/sushi.2HDMC
masses=400-750:50
tanb=0.4-10:0.2
outdir=/afs/cern.ch/user/s/steggema/work/stats/CMSSW_8_1_0/src/CombineHarvester/Httbar/kfactors/results/
sushi_card=${outdir}/../2HDMC_physicalbasis.in

$(outdir)/.mapping: ../scripts/map_mA_mH_2HDMC.py
	cd .. && scram b && cd - && mkdir -p ${outdir} && cd ${outdir} && \
	map_mA_mH_2HDMC.py ${2HDMC} ${SusHi} --mass ${masses} --tanb ${tanb} --sushi_card ${sushi_card} && \
	touch $@

mapping: $(outdir)/.mapping


