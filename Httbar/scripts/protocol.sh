### Create text datacards
python setup_common.py
cd output

for MORPHPARAM in A_5 A_10 A_25 A_50
do
    ### Create RooFit workspace, applying the interference model

    combineTool.py -M T2W -i $MORPHPARAM/MORPH -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel

    ### Expected limits for range of masses
    combineTool.py -M Asymptotic -d $MORPHPARAM/MORPH/workspace.root --there -n .limit --parallel 4 -m "400:750:10" -t -1 --minimizerTolerance=0.0001 --minimizerStrategy=2
    combineTool.py -M CollectLimits $MORPHPARAM/MORPH/*.limit.* --use-dirs -o limits_$MORPHPARAM.json
    plotLimits.py --y-title="Coupling modifier" --x-title="M_{A} (GeV)" limits_${MORPHPARAM}_MORPH.json --output limits_$MORPHPARAM


    # ### Pulls

    # # Asimov pulls
    # combine -M MaxLikelihoodFit $MORPHPARAM/workspace.root -m 400 -t -1 --expectSignal 0.
    # python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -A -f text -g nuisances_bonly_$MORPHPARAM.root mlfit.root > nuisances_bonly_$MORPHPARAM.txt
    # combine -M MaxLikelihoodFit $MORPHPARAM/workspace.root -t -1 --expectSignal 2.
    # python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -A -f text -g nuisances_2splusb_$MORPHPARAM.root mlfit.root > nuisances_2splusb_$MORPHPARAM.txt


    # # Expected likelihood scan
    # combine $MORPHPARAM/workspace.root -M MultiDimFit --rMin 0 --rMax 2 --robustFit on --points 200 --algo=grid -t -1 --expectSignal=1. -m 400 -n $MORPHPARAM

    # # Measure ttbar cross section (on the way to unblinding)
    # combine -M MaxLikelihoodFit $MORPHPARAM/workspace.root --redefineSignalPOIs QCDscale_ttbar 
    # python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -A -f text -g nuisances.root mlfit.root


done

### More things to be done once unblinded

# combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --parallel 4
# combineTool.py -M CollectLimits */*/*.limit.* --use-dirs -o limits.json
# plotLimits.py --y-title="Coupling modifier" --x-title="M_{A} (GeV)" limits_A.json 
# 
# combineTool.py -M Impacts -d A/400/workspace.root -m 400 --doInitialFit --robustFit 1
# combineTool.py -M Impacts -d A/400/workspace.root -m 400 --robustFit 1 --doFits
# # combineTool.py -M ImpactsFromScans -d workspace.root -m 400 --robustFit 1 --doFits  --robustFit on
# combineTool.py -M Impacts -d A/400/workspace.root -m 400  -o impacts.json
# plotImpacts.py -i impacts.json -o impacts

