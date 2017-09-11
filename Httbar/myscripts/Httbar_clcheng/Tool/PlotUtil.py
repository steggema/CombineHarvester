import ROOT as R
from array import array
from pdb import set_trace
import numpy as np
import CombineHarvester.CombineTools.plotting as plot
import scipy.interpolate
R.gROOT.SetBatch(True)
        
def RatioPlot(hist, output="",normalize = True,**style):
  
 canv = R.TCanvas(output, output)
 pads = plot.TwoPadSplit(0.30, 0.01, 0.01)
 legend = plot.PositionedLegend(0.45, 0.10, 3, 0.015)
 defcols = [
    R.kGreen+3, R.kRed, R.kBlue, R.kBlack, R.kYellow+2,
    R.kOrange+10, R.kCyan+3, R.kMagenta+2, R.kViolet-5, R.kGray
    ]
    
#Referenced from plotLimits.py 
 hist[0].SetStats(0)
 for pad in pads:
  plot.Set(pad, Tickx=1, Ticky=1)
  if ("pad" in style and style["pad"] is not None):
   settings = {x.split('=')[0]: eval(x.split('=')[1]) for x in style["pad"].split(',')}
   print "Applying the following pad settings:"
   print settings
   plot.Set(pad, **settings)
 pads[0].cd()
 for i, h in enumerate(hist):
  if normalize is True:
   h.Scale(1/abs(h.Integral()))
  h.SetFillColorAlpha(defcols[i],0.3)
  h.SetMarkerColor(defcols[i])
  h.Draw('HIST SAME')
  legend.AddEntry(h, h.GetName())

 pads[1].cd()
 formataxis = False
 for i,h in enumerate(hist[1:]):
  h_ratio = hist[0].Clone()
  h_ratio.Divide(h)
  h_ratio.SetNdivisions(506, 'Y')
  if formataxis is False:
   plot.SetupTwoPadSplitAsRatio(pads, hist[0], h_ratio, 'Ratio_{}', True, 0.1, 2.4)
   formataxis = True 
  h_ratio.SetMarkerColor(defcols[i+1])
  h_ratio.SetMarkerStyle(5)
  if ("ratio" in style and style["ratio"] is not None):
   settings = {x.split('=')[0]: eval(x.split('=')[1]) for x in style["ratio"].split(',')}
   print "Applying the following ratio plot settings:"
   print settings
   plot.Set(h_ratio, **settings)
  h_ratio.Draw("P SAME")



 if legend.GetNRows() == 1:
    legend.SetY1(legend.GetY2() - 0.5*(legend.GetY2()-legend.GetY1()))
 legend.Draw()
  
 canv.SaveAs(".pdf")
 
def TH2FixAxisPlot( hist, step, Xfix = None, Yfix = None, XaxisTitle= "", YaxisTitle = "", output = "",style = None):
 if (Xfix is None) == (Yfix is None):
  raise Exception("Incorrect input argument: only fix either x or y axis") 
 canv = R.TCanvas(output, output)
 x = []
 y = []
 fixNum = Xfix if Yfix is None else Yfix
 bmin, bmax = (hist.GetXaxis().GetXmin(),hist.GetXaxis().GetXmax()) if Xfix is None else (hist.GetYaxis().GetXmin(),hist.GetYaxis().GetXmax())
 for bin in np.arange(bmin, bmax, step):
  x.append(bin)
  if Yfix is None:
   y.append(hist.GetBinContent(hist.FindBin(fixNum,bin)))
  else:
   y.append(hist.GetBinContent(hist.FindBin(bin,fixNum)))
 g = R.TGraph(len(x),array('d',x),array('d',y))
 g.SetTitle("")
 g.GetXaxis().SetTitle(XaxisTitle)
 g.GetYaxis().SetTitle(YaxisTitle) 
 if XaxisTitle == "":
  g.GetXaxis().SetTitle(hist.GetXaxis().GetTitle() if Xfix is None else hist.GetYaxis().GetTitle())
 if YaxisTitle == "":  
  g.GetYaxis().SetTitle(hist.GetZaxis().GetTitle())
 if (style is not None):
  settings = {x.split('=')[0]: eval(x.split('=')[1]) for x in style.split(',')}
  print "Applying the following ratio plot settings:"
  print settings
  plot.Set(g, **settings)
 g.Draw()
 if output != "":
  canv.SaveAs(".pdf")
 return g, zip(x,y)

#Input a list containing tuples of bin content and return a list of x bins that has values equal to the input value
def InverseInterpolate(arr, value):
 arr = sorted(arr)
 arr = [i for i in arr if i[1] != 0]
 result = []
 trigger = True if arr[0][1] < value else False
 PreVal = arr[0] 
 for i in arr:
  if (trigger != (i[1] < value)) :
   trigger = not trigger
   points = zip(PreVal, i) if not trigger else zip(i,PreVal)
   result.append(float(scipy.interpolate.interp1d(points[1],points[0])(value)))
  PreVal = i 
 return result
