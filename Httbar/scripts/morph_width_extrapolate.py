#!/usr/bin/env python
import ROOT
from argparse import ArgumentParser
import shutil

parser = ArgumentParser()
parser.add_argument('input', nargs='+', help="Input templates for morphing")
parser.add_argument(
    '--width', default=1, type=float, help="""width in pc to be extrapolated""")
parser.add_argument(
    '--refwidth', default=2.5, type=float, help="""Reference width for extrapolation""")
parser.add_argument(
    '--sgnfactor', default=2.524551213, type=float, help="""Factor by which the signal shapes scale between the ref width and extrapolated width: new = ref*factor""")
parser.add_argument(
    '--intfactor', default=1., type=float, help="""Factor by which the interference shapes scale between the ref width and extrapolated width: new = ref(factor)""")
parser.add_argument('--out', help='forces output name')
args = parser.parse_args()

print 'FIXME - determine sgnfactor and intfactor automatically from some input'
print '   Now assuming constant sgnfactor', args.sgnfactor
print '   Now assuming constant intfactor', args.intfactor

ref = "-{0}pc-".format(str(args.refwidth).replace(".", "p"))
if float(int(args.width)) == args.width:
    args.width = int(args.width)
new = "-{0}pc-".format(str(args.width).replace(".", "p"))
for files in args.input:
    print "Loading file {0}".format(files)
    f = args.out if args.out else files.replace(".root", "_extrapolated.root")
    shutil.copyfile(files, f)
    f = ROOT.TFile(f, "UPDATE")
    for category in [i.GetName() for i in f.GetListOfKeys()]:
        tdir = f.Get(category)
        tdir.cd()

        shapes = [i.GetName() for i in tdir.GetListOfKeys()]
        shapes = [i for i in shapes if (i.startswith(
            'ggA_') or i.startswith('ggH_')) and ref in i]
        shapes = {"sgn": [tdir.Get(i) for i in shapes if '_pos-sgn' in i],
                  "int": [tdir.Get(i) for i in shapes if '-int-' in i]}

        factor = {"sgn": args.sgnfactor, "int": args.intfactor}
        n = {"sgn": len(shapes["sgn"]), "int": len(shapes["int"])}
        print "category: {0} # of sgn shapes: {1} # of int shapes: {2}".format(category, n["sgn"], n["int"])
        for _type in shapes:
            counter = 0
            for shape in shapes[_type]:
                h_new = shape.Clone(shape.GetName().replace(ref, new))
                # set_trace()
                h_new.Scale(factor[_type])
                h_new.Write()
                counter += 1
                print "Doing {0} shapes: {1}/{2}".format(_type, counter, n[_type])
    f.Close()
