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

import fastr


if __name__ == "__main__":
    ALGS = ["FAST++", "FAST-CS", "FAST-pw", "FAST-all"]
    script, alg = sys.argv

    if alg not in ALGS:
        print("Wrong input algorithm")
        exit()

    directory = "outputLargeScale/"
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
    def log_(x): return int(math.log(x)) + 1
    def one_(x): return 1

    inputFile = "input/scalability/scalability-bbox.txt"

    outpath = "outputLargeScale/"
    sPath = outpath + "selections/"
    tPath = outpath + "measures/"

    numOfTCS = sum((1 for _ in open(inputFile)))
    B = [int(numOfTCS * red / 100) for red in range(1, 30+1)]


    if alg == "FAST++":
        for reduction in range(30):
            sTime, pTime, sel = fastr.fastPlusPlus(
                inputFile, dim=dim, B=B[reduction], memory=False)
            sOut = "{}/{}-{}.pickle".format(sPath, "FAST++", reduction+1)
            pickle.dump(sel, open(sOut, "wb"))
            tOut = "{}/{}-{}.pickle".format(tPath, "FAST++", reduction+1)
            pickle.dump((sTime, pTime), open(tOut, "wb"))
            print("FAST++", reduction+1, sTime, pTime)


    if alg == "FAST-CS":
        for reduction in range(30):
            sTime, pTime, sel = fastr.fastCS(
                inputFile, dim=dim, B=B[reduction], memory=False)
            sOut = "{}/{}-{}.pickle".format(sPath, "FAST-CS", reduction+1)
            pickle.dump(sel, open(sOut, "wb"))
            tOut = "{}/{}-{}.pickle".format(tPath, "FAST-CS", reduction+1)
            pickle.dump((sTime, pTime), open(tOut, "wb"))
            print("FAST-CS", reduction+1, sTime, pTime)


    if alg == "FAST-pw":
        for reduction in range(30):
            sTime, pTime, sel = fastr.fast_pw(
                inputFile, r, b, bbox=True, k=k, memory=False, B=B)
            sOut = "{}/{}-{}.pickle".format(sPath, "FAST-pw", reduction+1)
            pickle.dump(sel, open(sOut, "wb"))
            tOut = "{}/{}-{}.pickle".format(tPath, "FAST-pw", reduction+1)
            pickle.dump((sTime, pTime), open(tOut, "wb"))
            print("FAST-pw", reduction+1, sTime, pTime)


    if alg == "FAST-all":
        for reduction in range(30):
            sTime, pTime, sel = fastr.fast_(
                inputFile, all_, r, b, bbox=True, k=k, memory=False, B=B)
            sOut = "{}/{}-{}.pickle".format(sPath, "FAST-all", reduction+1)
            pickle.dump(sel, open(sOut, "wb"))
            tOut = "{}/{}-{}.pickle".format(tPath, "FAST-all", reduction+1)
            pickle.dump((sTime, pTime), open(tOut, "wb"))
            print("FAST-all", reduction+1, sTime, pTime)
