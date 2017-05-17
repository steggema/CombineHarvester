jobid=morph
runmode='--run blind'
limitdir=output$(jobid)
masses=400,450,500,550,600,650,700,750

#../data/templates_$(jobid)_morphed.root: ../data/templates_$(jobid).root ../scripts/morph_widths.py
#	../scripts/morph_widths.py ../data/templates_$(jobid).root

$(limitdir)/.cards: ../data/templates_$(jobid).root ../scripts/setup_common.py #../data/templates_$(jobid)_morphed.root ../scripts/setup_andrey.py
	python ../scripts/setup_common.py ${jobid} --parity=A --masses=${masses}  && touch $@

cards: $(limitdir)/.cards

$(limitdir)/.workspace: $(limitdir)/.cards ../scripts/Httbar_workspace.sh
	cd .. && scram b && cd - && cd $(limitdir) && Httbar_workspace.sh && cd - && touch $@

workspace: $(limitdir)/.workspace

$(limitdir)/.limit: $(limitdir)/.workspace ../scripts/Httbar_limits.sh
	cd $(limitdir) && Httbar_limits.sh ${runmode} && cd - && touch $@

limits: $(limitdir)/.limit

$(limitdir)/.jsons: $(limitdir)/.limit
	cd $(limitdir) && combineTool.py -M CollectLimits */*/*.limit.* --use-dirs && cd - && touch $@

jsons: $(limitdir)/.jsons

$(limitdir)/.plot: $(limitdir)/.jsons ../scripts/Httbar_plots.sh
	cd .. && scram b && cd - && cd $(limitdir) &&	mkdir -p plots && Httbar_plots.sh && cd - && touch $@

plots: $(limitdir)/.plot

$(limitdir)/.breakdown: $(limitdir)/.workspace
	cd $(limitdir) && systematics_breakdown.py $(runmode) && cd - && touch $@

breakdown: $(limitdir)/.breakdown

$(limitdir)/.impacts: $(limitdir)/.workspace ../scripts/impacts.sh
	cd $(limitdir) && impacts.sh ${runmode} && cd - && touch $@

impacts: $(limitdir)/.impacts

all: $(limitdir)/.plot
