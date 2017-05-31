jobid=2D_2017Mar23
#jobid=morph
runmode=--run blind
limitdir=output$(jobid)
#masses=400,450,500,550,600,650,700,750
masses=400,500,600,750

#../data/templates_$(jobid)_morphed.root: ../data/templates_$(jobid).root ../scripts/morph_widths.py
#	../scripts/morph_widths.py ../data/templates_$(jobid).root

$(limitdir)/.cards: ../data/templates_$(jobid).root ../scripts/setup_common.py #../data/templates_$(jobid)_morphed.root ../scripts/setup_andrey.py
	python ../scripts/setup_common.py ${jobid} --parity=A --masses=${masses}  && touch $@

cards: $(limitdir)/.cards

$(limitdir)/.workspace: $(limitdir)/.cards ../scripts/Httbar_workspace.sh
	cd .. && scram b && cd - && cd $(limitdir) && Httbar_workspace.sh && cd - && touch $@

workspace: $(limitdir)/.workspace

$(limitdir)/.limit: $(limitdir)/.workspace ../scripts/Httbar_limits.sh
	cd $(limitdir) && ../../scripts/Httbar_limits.sh ${runmode} && cd - && touch $@

limits: $(limitdir)/.limit

$(limitdir)/.jsons: $(limitdir)/.limit
	cd $(limitdir) && combineTool.py -M CollectLimits */*/higgsCombine.limit.Asymptotic.mH[0-9][0-9][0-9].root --use-dirs && cd - && touch $@

jsons: $(limitdir)/.jsons

$(limitdir)/.breakdown: $(limitdir)/.workspace ../scripts/systematics_breakdown.py
	cd $(limitdir) && ../../scripts/systematics_breakdown.py ${runmode} && cd - && touch $@

breakdown: $(limitdir)/.breakdown

$(limitdir)/.impacts: $(limitdir)/.workspace ../scripts/impacts.sh
	cd $(limitdir) && impacts.sh ${runmode} && cd - && touch $@

impacts: $(limitdir)/.impacts

$(limitdir)/.plot: $(limitdir)/.jsons $(limitdir)/.breakdown ../scripts/Httbar_plots.sh ../scripts/compareLimits.py
	cd .. && scram b && cd - && cd $(limitdir) &&	mkdir -p plots && Httbar_plots.sh && cd - && touch $@

plots: $(limitdir)/.plot

all: $(limitdir)/.plot
