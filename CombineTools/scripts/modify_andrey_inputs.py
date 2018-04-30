import ROOT


f_in = ROOT.TFile('andrey.root')

masses = [400, 500, 600, 750]

procs_signal = []

signal_patterns = ['HToTT-scalar-m{mass}-sgn', 
                   'HToTT-scalar-m{mass}-int', 
                   'HToTT-pseudoscalar-m{mass}-int',
                   'HToTT-pseudoscalar-m{mass}-sgn',]
for signal_pattern in signal_patterns:
    for m in masses:
        procs_signal.append(signal_pattern.format(mass=m))

f_out = ROOT.TFile('andrey_tth.inputs-bsm-8TeV.root', 'RECREATE')
# f_out.mkdir('mu_2btag')
# f_out.cd('l_plus_jets')


for cat_key in f_in.GetListOfKeys():
    dir_name = cat_key.GetName()
    cat = f_in.Get(dir_name)

    f_out.mkdir(dir_name)
    f_out.cd(dir_name)

    for hist_key in cat.GetListOfKeys():
        hist_name = hist_key.GetName()
        # print 'Hist name', hist_name
        if any(hist_name.startswith(pattern) for pattern in procs_signal):
            print 'Do signal stuff with', hist_name
            # Split signal templates into pos/neg parts
            hist = cat.Get(hist_name)

            if '-int' in hist_name:

                hist_neg = hist.Clone(hist_name.replace('scalar', 'scalar_neg'))
                for i_bin in xrange(0, hist_neg.GetNbinsX()+2):
                    if hist_neg.GetBinContent(i_bin) > 0. or hist_neg.GetXaxis().GetBinCenter(i_bin) > 1000.:
                        hist_neg.SetBinContent(i_bin, 0.)

                hist_neg.Scale(-1.)
                out_name = hist_neg.GetName().replace('-int', '').replace('HToTT', 'HToTT-int')
                hist_neg.Write(out_name)

                for i_bin in xrange(0, hist.GetNbinsX()+2):
                    if hist.GetBinContent(i_bin) < 0.:
                        hist.SetBinContent(i_bin, 0.)

            out_name = hist_name
            if '-int' in out_name:
                out_name = out_name.replace('-int', '').replace('HToTT', 'HToTT-int')
            if '-sgn' in out_name:
                out_name = out_name.replace('-sgn', '').replace('HToTT', 'HToTT-sgn')
            hist.Write(out_name)
        elif hist_name == 'data':
            hist = cat.Get(hist_name)
            h_data = hist.Clone('data_obs')
            h_data.Write()
        else:
            hist = cat.Get(hist_name)
            hist.Write(hist_name)


    