import ROOT

var_name = 'hDfitTTBarMBest'

f_in = ROOT.TFile('htt_from_markus.root')

procs = ['t_bar_t__correct', 'Single_t', 'W_jets', 'Z_jets', 'QCD_multijet', 'Diboson']

masses = [400, 500, 600, 700, 800]

procs_signal = []

signal_patterns = ['S0_M{mass}_scalar',  'S0_M{mass}_pseudoscalar']
for signal_pattern in signal_patterns:
    for m in masses:
        procs_signal.append(signal_pattern.format(mass=m))

procs += procs_signal

f_out = ROOT.TFile('hexo_tth.inputs-bsm-8TeV.root', 'RECREATE')
f_out.mkdir('l_plus_jets')
f_out.cd('l_plus_jets')

h_data = None


def scale(hist, name):
    # from Markus
    # norms = {
    #     'scalar': {
    #         400: 320.1311476,
    #         500: 273.1221192,
    #         600: 466.4397227,
    #         700: 557.3818845,
    #         800: 749.5767624,
    #     },
    #     'pseudoscalar': {
    #         400: 306.6004165,
    #         500: 453.386398,
    #         600: 643.1835984,
    #         700: 856.970862,
    #         800: 1131.366058,
    #     }
    # }
    norms = {
        'scalar': {
            400: 2074732./1000.,
            500: 1990686./1000.,
            600: 2354567./1000.,
            700: 1999935./1000.,
            800: 1999938./1000.,
        },
        'pseudoscalar': {
            400: 2279557./1000.,
            500: 1999940./1000.,
            600: 1999949./1000.,
            700: 1999932./1000.,
            800: 1999940./1000.,
        }
    }

    mode = 'scalar'
    if 'pseudoscalar' in name:
        mode = 'pseudoscalar'

    mass = int(name[-3:])

    norm = norms[mode][mass]
    hist.Scale(1./norm)

for i_proc, proc in enumerate(procs):
    in_name = var_name + proc
    hist = f_in.Get(in_name)
    out_name = proc
    if '_scalar' in out_name:
        out_name = out_name.replace('_scalar', '').replace('S0', 'S0_scalar')
        scale(hist, out_name)
    if '_pseudoscalar' in out_name:
        out_name = out_name.replace('_pseudoscalar', '').replace('S0', 'S0_pseudoscalar')
        scale(hist, out_name)

    # Split signal templates into pos/neg parts
    if 'scalar' in out_name:
        hist_neg = hist.Clone(out_name.replace('S0', 'S0_neg'))
        for i_bin in xrange(0, hist_neg.GetNbinsX()+2):
            if hist_neg.GetBinContent(i_bin) > 0. or hist_neg.GetXaxis().GetBinCenter(i_bin) > 1000.:
                hist_neg.SetBinContent(i_bin, 0.)

        hist_neg.Scale(-1.)
        hist_neg.Write(hist_neg.GetName())

        for i_bin in xrange(0, hist.GetNbinsX()+2):
            if hist.GetBinContent(i_bin) < 0.:
                hist.SetBinContent(i_bin, 0.)

    else:  # background
        if i_proc == 0:
            h_data = hist.Clone('data_obs')
        else:
            h_data.Add(hist)

    hist.Write(out_name)

for i_bin in xrange(0, h_data.GetNbinsX()+2):
    h_data.SetBinContent(i_bin, round(h_data.GetBinContent(i_bin)))

h_data.Write()
