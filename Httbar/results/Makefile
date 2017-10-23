jobid=2017Aug04
runmode=--run blind
channel=cmb
limitdir=/afs/cern.ch/user/s/steggema/work/stats/CMSSW_7_4_7/src/CombineHarvester/Httbar/results/combination/
datdir=/afs/cern.ch/user/s/steggema/work/stats/CMSSW_7_4_7/src/CombineHarvester/Httbar/data/
masses=500
widths=2p5,5,10
masses=400,450,500,550,600,650,700,750
#widths='1,1p5,2,2p5,3,3p5,4,4p5,5,5p5,6,6p5,7,7p5,8,8p5,9,9p5,10,10p5,11,11p5,12,12p5,13,13p5,14,14p5,15,15p5,16,16p5,17,17p5,18,18p5,19,19p5,20,20p5,21,21p5,22,22p5,23,23p5,24,24p5,25,25p5,26,26p5,27,27p5,28,28p5,29,29p5,30,30p5,31,31p5,32,32p5,33,33p5,34,34p5,35,35p5,36,36p5,37,37p5,38,38p5,39,39p5,40,40p5,41,41p5,42,42p5,43,43p5,44,44p5,45,45p5,46,46p5,47,47p5,48,48p5,49,49p5,50'

#Morphing and merging


# $(datdir)/templates_ll_sig_$(jobid)_A_morphed_mass.root: $(datdir)/templates_ll_sig_$(jobid).root $(datdir)/templates_ll_bkg_$(jobid).root ../scripts/morph_mass.py
# 	cd .. && scram b && cd - && morph_mass.py $<  $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750

# $(datdir)/templates_lj_sig_$(jobid)_A_morphed_mass.root: $(datdir)/templates_lj_sig_$(jobid).root $(datdir)/templates_lj_bkg_$(jobid).root ../scripts/morph_mass.py
# 	cd .. && scram b && cd - && morph_mass.py $< $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750

# $(datdir)/templates_ll_sig_$(jobid)_H_morphed_mass.root: $(datdir)/templates_ll_sig_$(jobid).root $(datdir)/templates_ll_bkg_$(jobid).root ../scripts/morph_mass.py
# 	cd .. && scram b && cd - && morph_mass.py $< $(word 2,$^) H --algo NonLinearPosFractions --input_masses 400,500,600,750

# $(datdir)/templates_lj_sig_$(jobid)_H_morphed_mass.root: $(datdir)/templates_lj_sig_$(jobid).root $(datdir)/templates_lj_bkg_$(jobid).root ../scripts/morph_mass.py
# 	cd .. && scram b && cd - && morph_mass.py $< $(word 2,$^) H --algo NonLinearPosFractions --input_masses 400,500,600,750

# $(datdir)/templates_lj_$(jobid).root: $(datdir)/templates_lj_sig_$(jobid)_A_morphed_mass.root $(datdir)/templates_lj_sig_$(jobid)_H_morphed_mass.root $(datdir)/templates_lj_bkg_$(jobid).root
# 	hadd -f -O $@ $^

# $(datdir)/templates_ll_$(jobid).root: $(datdir)/templates_ll_sig_$(jobid)_A_morphed_mass.root $(datdir)/templates_ll_sig_$(jobid)_H_morphed_mass.root $(datdir)/templates_ll_bkg_$(jobid).root
# 	hadd -f -O $@ $^

# $(datdir)/templates_ALL_$(jobid).root: $(datdir)/templates_lj_$(jobid).root $(datdir)/templates_ll_$(jobid).root
# 	hadd -f -O $@ $^

# morph: $(datdir)/templates_ALL_$(jobid).root


#
#   Workspace and limits
#
$(limitdir)/.cards: $(datdir)/templates_ALL_$(jobid).root ../scripts/setup_common.py #$(datdir)/templates_$(jobid)_morphed.root ../scripts/setup_andrey.py
	python ../scripts/setup_common.py ${jobid} --channels=${channel} --parity=A,H --masses=${masses}  --widths=${widths} --limitdir=${limitdir} --indir=$(datdir) --noBBB && touch $@


cards: $(limitdir)/.cards

$(limitdir)/.workspace: $(limitdir)/.cards ../scripts/Httbar_workspace.sh
	cd .. && scram b && cd - && cd $(limitdir) && Httbar_workspace.sh && cd - && touch $@

workspace: $(limitdir)/.workspace

$(limitdir)/.limit:  $(limitdir)/.workspace  ../scripts/Httbar_limits.sh
	cd $(limitdir) && Httbar_limits.sh ${runmode} && cd - && touch $@

limits: $(limitdir)/.limit

$(limitdir)/.jsons:  $(limitdir)/.workspace ../scripts/transpose_jsons.py
	cd .. && scram b && cd - && cd $(limitdir) && \
	combineTool.py -M CollectLimits */*/higgsCombine.limit.Asymptotic.mH[0-9][0-9][0-9].root --use-dirs && \
	transpose_jsons.py limits_A_[0-9]*.json && cd -&& touch $@

jsons: $(limitdir)/.jsons

$(limitdir)/.limitplots: $(limitdir)/.jsons ../scripts/Httbar_plots.sh
	cd .. && scram b && cd - && cd $(limitdir) &&	mkdir -p plots && Httbar_plots.sh && cd - && touch $@

limitplots: $(limitdir)/.limitplots


#
#   Limit diagnostics
#
$(limitdir)/.breakdown: $(limitdir)/.workspace ../scripts/systematics_breakdown.py
	cd .. && scram b && cd - && cd $(limitdir) && \
	../../scripts/systematics_breakdown.py ${runmode} --masses '[3-6]00' && \
	../../scripts/systematics_breakdown.py ${runmode} --masses '750' && \
	cd - && touch $@

breakdown: $(limitdir)/.breakdown

$(limitdir)/.breakdownplots: $(limitdir)/.breakdown $(limitdir)/.jsons ../scripts/breakdown_plots.sh ../scripts/transpose_jsons.py
	cd .. && scram b && cd - && cd $(limitdir) && transpose_jsons.py *_?_[0-9]*.json && \
	mkdir -p plots && breakdown_plots.sh && cd - && touch $@

breakdownplots: $(limitdir)/.breakdownplots

$(limitdir)/.impacts: $(limitdir)/.workspace ../scripts/impacts.sh
	cd .. && scram b && cd - && cd $(limitdir) && impacts.sh ${runmode} && cd - && touch $@

impacts: $(limitdir)/.impacts

#
# Other random plots
#

#mass morph check
$(limitdir)/.morph_checks:  ../data/templates_lj_sig_$(jobid).root ../data/templates_lj_bkg_$(jobid).root ../data/templates_ll_sig_$(jobid).root ../data/templates_ll_bkg_$(jobid).root ../scripts/morph_mass.py ../scripts/morph_widths.py ../scripts/plot_morph_check.py
	cd .. && scram b && cd - && \
	morph_mass.py $<  $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single 500 && \
	morph_mass.py $<  $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting 500 && \
	morph_widths.py ../data/templates_lj_sig_$(jobid)_A_M500.root --forchecks && \
	plot_morph_check.py ../data/templates_lj_sig_$(jobid)_A_M500_width_morphed.root ../data/templates_lj_sig_$(jobid)_A_mass_morph_testing.root $(limitdir)/checks && \
	morph_mass.py $(word 3,$^) $(word 4,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single 500 && \
	morph_mass.py $(word 3,$^) $(word 4,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting 500 && \
	morph_widths.py ../data/templates_ll_sig_$(jobid)_A_M500.root --forchecks && \
	plot_morph_check.py ../data/templates_ll_sig_$(jobid)_A_M500_width_morphed.root ../data/templates_ll_sig_$(jobid)_A_mass_morph_testing.root $(limitdir)/checks --categories ll && \
	touch $@

morph_checks: $(limitdir)/.morph_checks

#../scripts/morph_mass.py ../data/templates_lj_sig_2017Aug04.root ../data/templates_lj_bkg_2017Aug04.root A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single 500
#../scripts/morph_mass.py ../data/templates_lj_sig_2017Aug04.root ../data/templates_lj_bkg_2017Aug04.root A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting 500

all: $(limitdir)/.limitplots $(limitdir)/.breakdownplots $(limitdir)/.impacts
