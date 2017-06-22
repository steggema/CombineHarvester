#jobid=2D_240317_morph
jobid=2D_2017Mar23
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

$(limitdir)/.jsons: $(limitdir)/.limit ../scripts/transpose_jsons.py
	cd .. && scram b && cd - && cd $(limitdir) && \
	combineTool.py -M CollectLimits */*/higgsCombine.limit.Asymptotic.mH[0-9][0-9][0-9].root --use-dirs && \
	transpose_jsons.py limits_A_[0-9]*.json && cd - && touch $@

jsons: $(limitdir)/.jsons

$(limitdir)/.limitplots: $(limitdir)/.jsons ../scripts/Httbar_plots.sh
	cd .. && scram b && cd - && cd $(limitdir) &&	mkdir -p plots && Httbar_plots.sh && cd - && touch $@

limitplots: $(limitdir)/.limitplots

$(limitdir)/.breakdown: $(limitdir)/.workspace ../scripts/systematics_breakdown.py ../scripts/transpose_jsons.py
	cd .. && scram b && cd - && cd $(limitdir) && \
	../../scripts/systematics_breakdown.py ${runmode} --masses '[0-9]00' && \
	transpose_jsons.py *_A_[0-9]*.json && cd - && touch $@

breakdown: $(limitdir)/.breakdown

$(limitdir)/.breakdownplots: $(limitdir)/.breakdown $(limitdir)/.jsons ../scripts/breakdown_plots.sh
	cd .. && scram b && cd - && cd $(limitdir) && mkdir -p plots && breakdown_plots.sh && cd - && touch $@

breakdownplots: $(limitdir)/.breakdownplots

$(limitdir)/.impacts: $(limitdir)/.workspace ../scripts/impacts.sh
	cd $(limitdir) && impacts.sh ${runmode} && cd - && touch $@

impacts: $(limitdir)/.impacts

all: $(limitdir)/.limitplots $(limitdir)/.breakdownplots $(limitdir)/.impacts
