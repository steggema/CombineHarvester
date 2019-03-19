for SEED in {0..9999}
do
  # combine workspace.root -M GenerateOnly --toysFrequentist  -t 1 --saveToys  --expectSignal=0 -s $SEED
  combine ../A_4/400/workspace.root -M GenerateOnly -t 1 --saveToys  --expectSignal=0 -s $SEED --setParameters g=0,r=0
done
