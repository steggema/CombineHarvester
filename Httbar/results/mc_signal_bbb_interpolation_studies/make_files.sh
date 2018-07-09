
for chan in ll lj; do
		for m in 400 500 600 750; do
				for p in H A; do 
						morph_mass.py /afs/cern.ch/work/m/mverzett/HTT_LIMITS_81/src/CombineHarvester/Httbar/data/templates_$chan'_sig_2018Jun25.root' /afs/cern.ch/work/m/mverzett/HTT_LIMITS_81/src/CombineHarvester/Httbar/data/templates_$chan'_bkg_2018Jun25.root' $p --algo NonLinearPosFractions --single=$m --out $chan$p$m.root -q --nosystematics				
				done
		done
done
hadd -f templates.root *[AH][4-7][05]0.root

