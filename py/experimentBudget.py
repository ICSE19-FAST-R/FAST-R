'''
This file is part of an ICSE'19 submission that is currently under review.
For more information visit: https://github.com/ICSE19-FAST-R/FAST-R.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

import math
import os
import pickle
import sys

import competitors
import fastr
import metric


if __name__ == "__main__":
    SIR = [("flex", "v3"), ("grep", "v3"), ("gzip", "v1"), ("sed", "v6"), ("make", "v1")]
    D4J = [("math", "v1"), ("closure", "v1"), ("time", "v1"), ("lang", "v1"), ("chart", "v1")]
    script, covType, prog, v = sys.argv

    if (script, v) not in SIR or (script, v) not in D4J:
        print("Wrong input program")
        exit()

    repeats = 50
    for reduction in range(1, 30+1):
        directory = "outputBudget-{}/{}_{}/".format(covType, prog, v)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(directory + "selections/"):
            os.makedirs(directory + "selections/")
        if not os.path.exists(directory + "measures/"):
            os.makedirs(directory + "measures/")

        # FAST-R parameters
        k, n, r, b = 5, 10, 1, 10
        dim = 10

        # FAST-f sample size
        def all_(x): return x
        def sqrt_(x): return int(math.sqrt(x)) + 1
        def log_(x): return int(math.log(x, 2)) + 1
        def one_(x): return 1

        # BLACKBOX
        javaFlag = True if ((prog, v) in D4J) else False

        inputFile = "input/{}_{}/{}-bbox.txt".format(prog, v, prog)
        wBoxFile = "input/{}_{}/{}-{}.txt".format(prog, v, prog, covType)
        if javaFlag:
            faultMatrix = "input/{}_{}/fault_matrix.txt".format(prog, v)
        else:
            faultMatrix = "input/{}_{}/fault_matrix_key_tc.pickle".format(prog, v)

        outpath = "outputBudget-{}/{}_{}/".format(covType, prog, v)
        sPath = outpath + "selections/"
        tPath = outpath + "measures/"

        B = int(sum((1 for _ in open(inputFile))) * reduction / 100)

        for run in range(repeats):
            sTime, pTime, sel = fastr.fastPlusPlus(inputFile, dim=dim, B=B)
            fdl = metric.fdl(sel, faultMatrix, javaFlag)
            sOut = "{}/{}-{}-{}.pickle".format(sPath, "FAST++", reduction, run+1)
            pickle.dump(sel, open(sOut, "wb"))
            tOut = "{}/{}-{}-{}.pickle".format(tPath, "FAST++", reduction, run+1)
            pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
            print("FAST++", reduction, sTime, pTime, fdl)

       for run in range(repeats):
           sTime, pTime, sel = fastr.fastCS(inputFile, dim=dim, B=B)
           fdl = metric.fdl(sel, faultMatrix, javaFlag)
           sOut = "{}/{}-{}-{}.pickle".format(sPath, "FAST-CS", reduction, run+1)
           pickle.dump(sel, open(sOut, "wb"))
           tOut = "{}/{}-{}-{}.pickle".format(tPath, "FAST-CS", reduction, run+1)
           pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
           print("FAST-CS", reduction, sTime, pTime, fdl)


       for run in range(repeats):
           sTime, pTime, sel = fastr.fast_pw(inputFile, r, b, bbox=True, k=k, memory=True, B=B)
           fdl = metric.fdl(sel, faultMatrix, javaFlag)
           sOut = "{}/{}-{}-{}.pickle".format(sPath, "FAST-pw", reduction, run+1)
           pickle.dump(sel, open(sOut, "wb"))
           tOut = "{}/{}-{}-{}.pickle".format(tPath, "FAST-pw", reduction, run+1)
           pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
           print("FAST-pw", reduction, sTime, pTime, fdl)


       for run in range(repeats):
           sTime, pTime, sel = fastr.fast_(inputFile, all_, r=r, b=b, bbox=True, k=k, memory=True, B=B)
           fdl = metric.fdl(sel, faultMatrix, javaFlag)
           sOut = "{}/{}-{}-{}.pickle".format(sPath, "FAST-all", reduction, run+1)
           pickle.dump(sel, open(sOut, "wb"))
           tOut = "{}/{}-{}-{}.pickle".format(tPath, "FAST-all", reduction, run+1)
           pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
           print("FAST-all", reduction, sTime, pTime, fdl)

       # WHITEBOX APPROACHES
       for run in range(repeats):
           sTime, pTime, sel = competitors.ga(wBoxFile, B=B)
           fdl = metric.fdl(sel, faultMatrix, javaFlag)
           sOut = "{}/{}-{}-{}.pickle".format(sPath, "GA", reduction, run+1)
           pickle.dump(sel, open(sOut, "wb"))
           tOut = "{}/{}-{}-{}.pickle".format(tPath, "GA", reduction, run+1)
           pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
           print("GA", reduction, sTime, pTime, fdl)

       for run in range(repeats):
           sTime, pTime, sel = competitors.artd(wBoxFile, B=B)
           fdl = metric.fdl(sel, faultMatrix, javaFlag)
           sOut = "{}/{}-{}-{}.pickle".format(sPath, "ART-D", reduction, run+1)
           pickle.dump(sel, open(sOut, "wb"))
           tOut = "{}/{}-{}-{}.pickle".format(tPath, "ART-D", reduction, run+1)
           pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
           print("ART-D", reduction, sTime, pTime, fdl)

       for run in range(repeats):
           sTime, pTime, sel = competitors.artf(wBoxFile, B=B)
           fdl = metric.fdl(sel, faultMatrix, javaFlag)
           sOut = "{}/{}-{}-{}.pickle".format(sPath, "ART-F", reduction, run+1)
           pickle.dump(sel, open(sOut, "wb"))
           tOut = "{}/{}-{}-{}.pickle".format(tPath, "ART-F", reduction, run+1)
           pickle.dump((sTime, pTime, fdl), open(tOut, "wb"))
           print("ART-F", reduction, sTime, pTime, fdl)
