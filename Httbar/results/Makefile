jobid=1D_2017Mar23
runmode='--run blind'
limitdir=output$(jobid)

#../data/templates_$(jobid)_morphed.root: ../data/templates_$(jobid).root ../scripts/morph_widths.py
#	../scripts/morph_widths.py ../data/templates_$(jobid).root

$(limitdir)/.cards: ../data/templates_$(jobid).root ../scripts/setup_andrey.py #../data/templates_$(jobid)_morphed.root ../scripts/setup_andrey.py
	python ../scripts/setup_andrey.py 1D_2017Mar23 --parity=A && touch $@

cards: $(limitdir)/.cards

$(limitdir)/.workspace: $(limitdir)/.cards ../scripts/Httbar_workspace.sh
	cd .. && scram b && cd - && cd $(limitdir) && Httbar_workspace.sh && cd - && touch $@

workspace: $(limitdir)/.workspace

$(limitdir)/.limit: $(limitdir)/.workspace
	cd $(limitdir) && combineTool.py -M Asymptotic -m 400:750:50 --freezeNuisances MH -d */*/workspace.root --there -n .limit --parallel 8 $(runmode) && cd - && touch $@

limits: $(limitdir)/.limit

$(limitdir)/.jsons: $(limitdir)/.limit
	cd $(limitdir) && combineTool.py -M CollectLimits */*/*.limit.* --use-dirs && cd - && touch $@

jsons: $(limitdir)/.jsons

$(limitdir)/.plot: $(limitdir)/.jsons ../scripts/Httbar_plots.sh
	cd .. && scram b && cd - && cd $(limitdir) &&	mkdir -p plots && Httbar_plots.sh && cd - && touch $@

$(limitdir)/.jsons: $(limitdir)/.limit
	cd $(limitdir) && combineTool.py -M CollectLimits */*/*.limit.* --use-dirs && cd - && touch $@

plots: $(limitdir)/.plot

$(limitdir)/.breakdown: $(limitdir)/.workspace
	cd $(limitdir) && systematics_breakdown.py $(runmode) && cd - && touch $@

breakdown: $(limitdir)/.breakdown


all: $(limitdir)/.plot
