#! /bin/env python

import pickle
from argparse import ArgumentParser
from pdb import set_trace

parser = ArgumentParser()
parser.add_argument('input')
args = parser.parse_args()

with open(args.input) as pkl:
	mapping = pickle.load(pkl)

import ROOT
ROOT.gROOT.SetStyle('Plain')
ROOT.gStyle.SetOptTitle(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)

excluded = {
	"exp+1": [],
	"exp+2": [],
	"exp-1": [],
	"exp-2": [],
	"exp0" : [],
}
failed = []

def DrawAxisHists(pads, axis_hists, def_pad=None):
    for i, pad in enumerate(pads):
        pad.cd()
        axis_hists[i].Draw('AXIS')
        axis_hists[i].Draw('AXIGSAME')
    if def_pad is not None:
        def_pad.cd()

col_store = []
def CreateTransparentColor(color, alpha):
  adapt   = ROOT.gROOT.GetColor(color)
  new_idx = ROOT.gROOT.GetListOfColors().GetSize() + 1
  trans = ROOT.TColor(new_idx, adapt.GetRed(), adapt.GetGreen(), adapt.GetBlue(), '', alpha)
  col_store.append(trans)
  trans.SetName('userColor%i' % new_idx)
  return new_idx

def make_graph(points):
	gr = ROOT.TGraph(len(points))
	for i, xy in enumerate(points):
		gr.SetPoint(i, xy[0], xy[1])
	return gr

def make_band(p1, p2, default=-2):
	p1d = dict(p1)
	p2d = dict(p2)
	xs = sorted(set(i for i, _ in p1+p2))
	gr = ROOT.TGraphErrors(len(xs))
	for i, x in enumerate(xs):
		y = abs(p1d.get(x, default) + p2d.get(x, default))/2.
		err = abs(p1d.get(x, default) - p2d.get(x, default))
		gr.SetPoint(i, x, y)
		gr.SetPointError(i, 0, err)
	return gr

for point, vals in mapping.iteritems():
	_, tb = point
	if not vals: 
		failed.append(point)
		continue
	for key in excluded:
		if vals[key] < 1/tb: excluded[key].append(point)

print 'Excluded %d points, %d failed' % (len(excluded), len(failed))
g_excluded = make_graph(excluded["exp0"])
g_excluded.SetMarkerColor(4)
g_excluded.SetMarkerStyle(20)
g_failed = make_graph(failed)
g_failed.SetMarkerColor(2)
g_failed.SetMarkerStyle(34)

canvas = ROOT.TCanvas('asd', 'asd', 800, 800)
g_excluded.Draw('AP')
g_failed.Draw('P same')

x_min = min(
	g_excluded.GetXaxis().GetXmin(),
	min(x for x, _ in mapping.iterkeys())
	)
x_max = max(
	max(x for x, _ in mapping.iterkeys())+50,
	g_excluded.GetXaxis().GetXmax()
	)
g_excluded.GetXaxis().SetLimits(x_min, x_max)
y_min = min(x for _, x in mapping.iterkeys())
y_max = max(x for _, x in mapping.iterkeys())*1.2
g_excluded.GetYaxis().SetRangeUser(y_min, y_max)
g_excluded.GetXaxis().SetTitle('m(A)')
g_excluded.GetYaxis().SetTitle('tan #beta')

canvas.SaveAs('exclusion.png')

#
# Get nicer plot
#

import CombineHarvester.CombineTools.plotting as plot
plot.ModTDRStyle(width=600, l=0.12)
ROOT.gStyle.SetFrameLineWidth(2)

ROOT.gStyle.SetNdivisions(510, 'XYZ') # probably looks better
canvas = ROOT.TCanvas('asd', 'asd', 800, 800)

pads = plot.OnePad()

plot.Set(pads[0], Tickx=1, Ticky=1)#, Logx=args.logx)
axis = plot.CreateAxisHists(
	len(pads), 
	make_graph(mapping.keys()),
	True
	)
DrawAxisHists(pads, axis, pads[0])
axis[0].GetXaxis().SetTitle('m_{A} (GeV)')
axis[0].GetYaxis().SetTitle('tan #beta')
axis[0].GetXaxis().SetLabelOffset(axis[0].GetXaxis().GetLabelOffset()*2)

pads[0].cd()
legend = plot.PositionedLegend(0.45, 0.10, 3, 0.015)
plot.Set(legend, NColumns=2)

legend.SetNColumns(2)
legend.SetFillStyle(1001)
legend.SetTextSize(0.15)
legend.SetTextFont(62)


best_points = {}
for key in excluded:
	points = excluded[key]
	xs = sorted(list(set(i for i, _ in points)))
	ys = [max(y for x, y in points if x == i) for i in xs]
	best_points[key] = zip(xs, ys)

expected = make_graph(best_points["exp0"])
expected.SetLineStyle(2)
onesigma = make_band(best_points['exp+1'], best_points['exp-1'])
onesigma.SetLineColor(1)
onesigma.SetFillColor(ROOT.kGray+2)
onesigma.SetFillStyle(3315)#1001)

twosigma = make_band(best_points['exp+2'], best_points['exp-2'])
twosigma.SetLineColor(ROOT.kGreen+1)
twosigma.SetFillColor(ROOT.kGreen+1)
twosigma.SetFillStyle(3351)#1001)

twosigma.Draw("4 same")
onesigma.Draw("4 same")

#legend.AddEntry(graphs[-1], '', 'PL')
#legend.AddEntry(graphs[-1], '', 'PL')

## axis[0].GetXaxis().SetLimits(x_min, x_max)
## axis[0].GetYaxis().SetLimits(y_min, y_max)

box = ROOT.TPave(pads[0].GetLeftMargin(), 0.81, 1-pads[0].GetRightMargin(), 1-pads[0].GetTopMargin(), 1, 'NDC')
box.Draw()
legend.Draw()

plot.DrawCMSLogo(pads[0], 'CMS', 'Preliminary', 11, 0.045, 0.035, 1.2, '', 0.8)
plot.DrawTitle(pads[0], '19.7 fb^{-1} (8TeV)', 3);
plot.DrawTitle(pads[0], 'hMSSM scenario', 1)

canvas.SaveAs('exclusion_summary.png')
