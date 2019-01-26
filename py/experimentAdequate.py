'''
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
import fastr_adequate
import metric


"""
This file runs all FAST-R algorithms (fastr_adequate.py) and the competitors (competitors.py)
in the Adequate scenario and in all input test suite.
"""


usage = """USAGE: python3 py/experimentAdequate.py <coverageType> <program> <version> <repetitions>
OPTIONS:
  <coverageType>: the target coverage criterion.
    options: function, line, branch
  <program> <version>: the target subject and its respective version.
    options: flex v3, grep v3, gzip v1, make v1, sed v6, chart v0, closure v0, lang v0, math v0, time v0
  <repetitions>: number of times the test suite reduction should be computed.
    options: positive integer value, e.g. 50"""


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(usage)
        exit()

    SIR = [("flex", "v3"), ("grep", "v3"), ("gzip", "v1"), ("sed", "v6"), ("make", "v1")]
    D4J = [("math", "v1"), ("closure", "v1"), ("time", "v1"), ("lang", "v1"), ("chart", "v1")]
    script, covType, prog, v, rep = sys.argv
    repeats = int(rep)

    directory = "outputAdequate-{}/{}_{}/".format(covType, prog, v)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(directory + "selections/"):
        os.makedirs(directory + "selections/")
    if not os.path.exists(directory + "measures/"):
        os.makedirs(directory + "measures/")    

    # FAST parameters
    k, n, r, b = 5, 10, 1, 10
    dim = 10

    # FAST-f sample size
    def all_(x): return x
    def sqrt_(x): return int(math.sqrt(x)) + 1
    def log_(x): return int(math.log(x, 2)) + 1
    def one_(x): return 1

    # BLACKBOX EXPERIMENTS
    javaFlag = True if ((prog, v) in D4J) else False

    inputFile = "input/{}_{}/{}-bbox.txt".format(prog, v, prog)
    wBoxFile = "input/{}_{}/{}-{}.txt".format(prog, v, prog, covType)
    if javaFlag:
        faultMatrix = "input/{}_{}/fault_matrix.txt".format(prog, v)
    else:
        faultMatrix = "input/{}_{}/fault_matrix_key_tc.pickle".format(prog, v)

    outpath = "outputAdequate-{}/{}_{}/".format(covType, prog, v)
    sPath = outpath + "selections/"
    tPath = outpath + "measures/"

    for run in range(repeats):
        pTime, cTime, rTime, sel = fastr_adequate.fastPlusPlus(inputFile, wBoxFile, dim=dim)
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "FAST++", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "FAST++", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("FAST++", pTime, cTime, rTime, fdl, tsr)


    for run in range(repeats):
        pTime, cTime, rTime, sel = fastr_adequate.fastCS(inputFile, wBoxFile, dim=dim)
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "FAST-CS", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "FAST-CS", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("FAST-CS", pTime, cTime, rTime, fdl, tsr)


    for run in range(repeats):
        pTime, cTime, rTime, sel = fastr_adequate.fast_pw(inputFile, wBoxFile, r=r, b=b, bbox=True, k=k, memory=True)
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "FAST-pw", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "FAST-pw", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("FAST-pw", pTime, cTime, rTime, fdl, tsr)


    for run in range(repeats):
        sTime, cTime, pTime, sel = fastr_adequate.fast_(inputFile, wBoxFile, all_, r=r, b=b, bbox=True, k=k, memory=True)
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "FAST-all", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "FAST-all", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("FAST-all", pTime, cTime, rTime, fdl, tsr)


    # WHITEBOX EXPERIMENTS
    for run in range(repeats):
        pTime, rTime, sel = competitors.gaAdequacy(wBoxFile)
        cTime = 0.0
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "GA", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "GA", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("GA", pTime, cTime, rTime, fdl, tsr)


    for run in range(repeats):
        pTime, rTime, sel = competitors.artdAdequacy(wBoxFile)
        cTime = 0.0
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "ART-D", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "ART-D", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("ART-D", pTime, cTime, rTime, fdl, tsr)


    for run in range(repeats):
        pTime, rTime, sel = competitors.artfAdequacy(wBoxFile)
        cTime = 0.0
        fdl = metric.fdl(sel, faultMatrix, javaFlag)
        tsr = metric.tsr(sel, inputFile)
        sOut = "{}/{}-{}.pickle".format(sPath, "ART-F", run+1)
        pickle.dump(sel, open(sOut, "wb"))
        tOut = "{}/{}-{}.pickle".format(tPath, "ART-F", run+1)
        pickle.dump((pTime, cTime, rTime, fdl, tsr), open(tOut, "wb"))
        print("ART-F", pTime, cTime, rTime, fdl, tsr)
