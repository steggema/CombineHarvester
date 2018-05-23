jobid=2017Nov16
runmode=--run blind
channel=cmb
limitdir=output_$(channel)_$(jobid)
masses=400,450,500,550,600,650,700,750

#
#   Morphing and merging
#
../data/templates_ll_sig_$(jobid)_A_morphed_mass.root: ../data/templates_ll_sig_$(jobid).root ../data/templates_ll_bkg_$(jobid).root ../scripts/morph_mass.py
	cd .. && scram b && cd - && morph_mass.py $<  $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750

../data/templates_lj_sig_$(jobid)_A_morphed_mass.root: ../data/templates_lj_sig_$(jobid).root ../data/templates_lj_bkg_$(jobid).root ../scripts/morph_mass.py
	cd .. && scram b && cd - && morph_mass.py $< $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750

../data/templates_ll_sig_$(jobid)_H_morphed_mass.root: ../data/templates_ll_sig_$(jobid).root ../data/templates_ll_bkg_$(jobid).root ../scripts/morph_mass.py
	cd .. && scram b && cd - && morph_mass.py $< $(word 2,$^) H --algo NonLinearPosFractions --input_masses 400,500,600,750

../data/templates_lj_sig_$(jobid)_H_morphed_mass.root: ../data/templates_lj_sig_$(jobid).root ../data/templates_lj_bkg_$(jobid).root ../scripts/morph_mass.py
	cd .. && scram b && cd - && morph_mass.py $< $(word 2,$^) H --algo NonLinearPosFractions --input_masses 400,500,600,750

../data/templates_lj_$(jobid).root: ../data/templates_lj_sig_$(jobid)_A_morphed_mass.root ../data/templates_lj_sig_$(jobid)_H_morphed_mass.root ../data/templates_lj_bkg_$(jobid).root
	hadd -f -O $@ $^

../data/templates_ll_$(jobid).root: ../data/templates_ll_sig_$(jobid)_A_morphed_mass.root ../data/templates_ll_sig_$(jobid)_H_morphed_mass.root ../data/templates_ll_bkg_$(jobid).root
	hadd -f -O $@ $^

../data/templates_ALL_$(jobid).root: ../data/templates_lj_$(jobid).root ../data/templates_ll_$(jobid).root
	hadd -f -O $@ $^

morph: ../data/templates_ALL_$(jobid).root


#
#   Workspace and limits
#
$(limitdir)/.cards: ../data/templates_ALL_$(jobid).root ../scripts/setup_common.py #../data/templates_$(jobid)_morphed.root ../scripts/setup_andrey.py
	python ../scripts/setup_common.py ${jobid} --channels=${channel} --parity=A,H --masses=${masses}  && touch $@

cards: $(limitdir)/.cards

$(limitdir)/.workspace: $(limitdir)/.cards ../scripts/Httbar_workspace.sh
	cd .. && scram b && cd - && cd $(limitdir) && Httbar_workspace.sh && cd - && touch $@

workspace: $(limitdir)/.workspace

$(limitdir)/.limit: $(limitdir)/.workspace ../scripts/Httbar_limits.sh
	cd $(limitdir) && ../../scripts/Httbar_limits.sh ${runmode} && cd - && touch $@

limits: $(limitdir)/.limit

$(limitdir)/.jsons: $(limitdir)/.limit ../scripts/transpose_jsons.py
	cd .. && scram b && cd - && cd $(limitdir) && \
	combineTool.py -M CollectLimits */*/higgsCombine.limit.AsymptoticLimits.mH[0-9][0-9][0-9].root --use-dirs && \
	transpose_jsons.py limits_A_[0-9]*.json && cd - && touch $@

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

##
## Deprecated, everything has moved to batch
##
## $(limitdir)/.impacts: $(limitdir)/.workspace ../scripts/impacts.sh
## 	cd .. && scram b && cd - && cd $(limitdir) && impacts.sh ${runmode} && cd - && touch $@
## 
## impacts: $(limitdir)/.impacts

#
# Other random plots
#

#mass morph check
$(limitdir)/.morph_checks:  ../data/templates_lj_sig_$(jobid).root ../data/templates_lj_bkg_$(jobid).root ../data/templates_ll_sig_$(jobid).root ../data/templates_ll_bkg_$(jobid).root ../scripts/morph_mass.py ../scripts/morph_widths.py ../scripts/plot_morph_check.py
	cd .. && scram b && cd - && \
	\
	morph_mass.py $<  $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single 500 --nosystematics && \
	morph_mass.py $<  $(word 2,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting 500 --nosystematics && \
	morph_widths.py ../data/templates_lj_sig_$(jobid)_A_M500.root --forchecks && \
	\
	morph_widths.py ../data/templates_lj_sig_$(jobid).root --forchecks  --nocopy --out ../data/templates_lj_sig_$(jobid)_widthmorphed.root && \
	morph_mass.py ../data/templates_lj_sig_$(jobid)_widthmorphed.root  $(word 2,$^) A --algo NonLinearPosFractions --fortesting 500 --nosystematics --out ../data/templates_lj_sig_$(jobid)_A_M500_doublemorphed.root && \
	\
	plot_morph_check.py ../data/templates_lj_sig_$(jobid)_A_M500_width_morphed.root ../data/templates_lj_sig_$(jobid)_A_mass_morph_testing.root ../data/templates_lj_sig_$(jobid)_A_M500_doublemorphed.root $(limitdir)/checks && \
	\
	\
	morph_mass.py $(word 3,$^) $(word 4,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single 500 --nosystematics && \
	morph_mass.py $(word 3,$^) $(word 4,$^) A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting 500 --nosystematics && \
	morph_widths.py ../data/templates_ll_sig_$(jobid)_A_M500.root --forchecks && \
	\
	morph_widths.py ../data/templates_ll_sig_$(jobid).root --forchecks  --nocopy --out ../data/templates_ll_sig_$(jobid)_widthmorphed.root && \
	morph_mass.py ../data/templates_ll_sig_$(jobid)_widthmorphed.root  $(word 4,$^) A --algo NonLinearPosFractions --fortesting 500 --nosystematics --out ../data/templates_ll_sig_$(jobid)_A_M500_doublemorphed.root && \
	\
	plot_morph_check.py ../data/templates_ll_sig_$(jobid)_A_M500_width_morphed.root ../data/templates_ll_sig_$(jobid)_A_mass_morph_testing.root ../data/templates_ll_sig_$(jobid)_A_M500_doublemorphed.root $(limitdir)/checks --categories ll && \
	touch $@

morph_checks: $(limitdir)/.morph_checks

#../scripts/morph_mass.py ../data/templates_lj_sig_2017Aug04.root ../data/templates_lj_bkg_2017Aug04.root A --algo NonLinearPosFractions --input_masses 400,500,600,750 --single 500
#../scripts/morph_mass.py ../data/templates_lj_sig_2017Aug04.root ../data/templates_lj_bkg_2017Aug04.root A --algo NonLinearPosFractions --input_masses 400,500,600,750 --fortesting 500

all: $(limitdir)/.limitplots $(limitdir)/.breakdownplots $(limitdir)/.impacts
