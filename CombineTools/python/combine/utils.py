import ROOT
import re

def split_vals(vals, fmt_spec=None):
    """Converts a string '1:3|1,4,5' into a list [1, 2, 3, 4, 5]"""
    res = set()
    first = vals.split(',')
    for f in first:
        second = re.split('[:|]', f)
        # print second
        if len(second) == 1:
            res.add(second[0])
        if len(second) == 3:
            x1 = float(second[0])
            ndigs = '0'
            split_step = second[2].split('.')
            if len(split_step) == 2:
                ndigs = len(split_step[1])
            fmt = '%.' + str(ndigs) + 'f'
            if fmt_spec is not None:
                fmt = fmt_spec
            while x1 < float(second[1]) + 0.0001:
                res.add(fmt % x1)
                x1 += float(second[2])
    return sorted([x for x in res], key=lambda x: float(x))


def list_from_workspace(file, workspace, set):
    """Create a list of strings from a RooWorkspace set"""
    res = []
    wsFile = ROOT.TFile(file)
    argSet = wsFile.Get(workspace).set(set)
    it = argSet.createIterator()
    var = it.Next()
    while var:
        res.append(var.GetName())
        var = it.Next()
    return res


def prefit_from_workspace(file, workspace, params, setPars=None):
    """Given a list of params, return a dictionary of [-1sig, nominal, +1sig]"""
    res = {}
    wsFile = ROOT.TFile(file)
    ws = wsFile.Get(workspace)
    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)
    if setPars is not None:
      parsToSet = [tuple(x.split('=')) for x in setPars.split(',')]
      for par,val in parsToSet:
        print 'Setting paramter %s to %g' % (par, float(val))
        ws.var(par).setVal(float(val))

    for p in params:
        res[p] = {}

        var = ws.var(p)
        pdf = ws.pdf(p+'_Pdf')
        gobs = ws.var(p+'_In')

        # For pyROOT NULL test: "pdf != None" != "pdf is not None"
        if pdf != None and gobs != None:
            # To get the errors we can just fit the pdf
            # But don't do pdf.fitTo(globalObs), it forces integration of the
            # range of the global observable. Instead we make a RooConstraintSum
            # which is what RooFit creates by default when we have external constraints
            nll = ROOT.RooConstraintSum('NLL', '', ROOT.RooArgSet(pdf), ROOT.RooArgSet(var))
            minim = ROOT.RooMinimizer(nll)
            minim.setEps(0.001)  # Might as well get some better precision...
            minim.setErrorLevel(0.5) # Unlike for a RooNLLVar we must set this explicitly
            minim.setPrintLevel(-1)
            minim.setVerbose(False)
            # Run the fit then run minos for the error
            minim.minimize('Minuit2', 'migrad')
            minim.minos(ROOT.RooArgSet(var))
            # Should really have checked that these converged ok...
            # var.Print()
            # pdf.Print()
            val = var.getVal()
            errlo = -1 * var.getErrorLo()
            errhi = +1 * var.getErrorHi()
            res[p]['prefit'] = [val-errlo, val, val+errhi]
            if pdf.IsA().InheritsFrom(ROOT.RooGaussian.Class()):
                res[p]['type'] = 'Gaussian'
            elif pdf.IsA().InheritsFrom(ROOT.RooPoisson.Class()):
                res[p]['type'] = 'Poisson'
            elif pdf.IsA().InheritsFrom(ROOT.RooBifurGauss.Class()):
                res[p]['type'] = 'AsymmetricGaussian'
            else:
                res[p]['type'] = 'Unrecognised'
        elif pdf == None or pdf.IsA().InheritsFrom(ROOT.RooUniform.Class()):
            res[p]['type'] = 'Unconstrained'
            res[p]['prefit'] = [var.getVal(), var.getVal(), var.getVal()]
        res[p]['groups'] = [x.replace('group_', '') for x in var.attributes() if x.startswith('group_')]
    return res


def get_singles_results(file, scanned, columns):
    """Extracts the output from the MultiDimFit singles mode
    Note: relies on the list of parameters that were run (scanned) being correct"""
    res = {}
    f = ROOT.TFile(file)
    if f is None or f.IsZombie():
        return None
    t = f.Get("limit")
    for i, param in enumerate(scanned):
        res[param] = {}
        for col in columns:
            allvals = [getattr(evt, col) for evt in t]
            if len(allvals) < (1 + len(scanned)*2):
                print 'File %s did not contain a sufficient number of entries, skipping' % file
                return None
            res[param][col] = [
                allvals[i * 2 + 1], allvals[0], allvals[i * 2 + 2]]
    return res

def get_none_results(file, params):
    """Extracts the output from the MultiDimFit none (just fit)  mode"""
    res = {}
    f = ROOT.TFile(file)
    if f is None or f.IsZombie():
        return None
    t = f.Get("limit")
    t.GetEntry(0)
    for param in params:
      res[param] = getattr(t, param)
    return res
