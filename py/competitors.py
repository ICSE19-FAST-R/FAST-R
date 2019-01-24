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

from collections import defaultdict
from collections import OrderedDict
from functools import reduce
import random
import time
import sys

import lsh




"""
This file contains an implementation of the following Test Case Reduction 
(Prioritization with a budget), each in standard and adequate version:
 - Greedy Additional (GA)
 - Adaptive Random Test with Fixed-size candidate set (ART-F)
 - Adaptive Random Test with Dynamic-size candidate set (ART-D)
Each function returns: preparation time, reduction time, reduced test suite.
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# utility function that loads test suites 
# format: source code of one test case per line (bbox)
# format: space-separated covered entities of one test case per line (wbox)
def loadTestSuite(input_file, bbox=False, k=5):
    TS = {}
    with open(input_file) as fin:
        tcID = 1
        for tc in fin:
            if bbox:
                TS[tcID] = tc[:-1]
            else:
                TS[tcID] = set(tc[:-1].split())
            tcID += 1
    shuffled = list(TS.keys())
    random.shuffle(shuffled)
    newTS = OrderedDict()
    for key in shuffled:
        newTS[key] = TS[key]
    if bbox:
        newTS = lsh.kShingles(TS, k)
    return newTS


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# GREEDY SET COVER (ADDITIONAL)
def ga(input_file, B=0):
    def select(TS, U, Cg):
        s, uncs_s = 0, -1
        for ui in U:
            uncs = len(TS[ui] - Cg)
            if uncs > uncs_s:
                s, uncs_s = ui, uncs
        return s

    ptime_start = time.clock()

    TCS = loadTestSuite(input_file)
    TS = OrderedDict(sorted(TCS.items(), key=lambda t: -len(t[1])))

    # budget B modification
    if B == 0:
        B = len(TS)

    U = TS.copy()
    Cg = set()

    TS[0] = set()
    P = [0]

    maxC = len(reduce(lambda x, y: x | y, TS.values()))

    while len(U) > 0:
        if len(Cg) == maxC:
            Cg = set()
        s = select(TS, U, Cg)
        P.append(s)

        # select budget B
        if len(P) >= B+1:
            break

        Cg = Cg | U[s]
        del U[s]

    ptime = time.clock() - ptime_start

    return 0.0, ptime, P[1:]


# GREEDY SET COVER (ADDITIONAL and ADEQUATE)
def gaAdequacy(input_file):
    def select(TS, U, Cg):
        s, uncs_s = 0, -1
        for ui in U:
            uncs = len(TS[ui] - Cg)
            if uncs > uncs_s:
                s, uncs_s = ui, uncs
        return s

    ptime_start = time.clock()

    TCS = loadTestSuite(input_file)
    TS = OrderedDict(sorted(TCS.items(), key=lambda t: -len(t[1])))

    U = TS.copy()
    Cg = set()

    TS[0] = set()
    P = [0]

    maxC = len(reduce(lambda x, y: x | y, TS.values()))

    while len(U) > 0:
        if len(Cg) == maxC:
            break
        s = select(TS, U, Cg)
        P.append(s)

        Cg = Cg | U[s]
        del U[s]

    ptime = time.clock() - ptime_start

    return 0.0, ptime, P[1:]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# JIANG (ART-D)
# dynamic candidate set
def artd(input_file, B=0):
    def generate(U):
        C, T = set(), set()
        while True:
            ui = random.choice(list(U.keys()))
            S = U[ui]
            if T | S == T:
                break
            T = T | S
            C.add(ui)
        return C

    def select(TS, P, C):
        D = {}
        for cj in C:
            D[cj] = {}
            for pi in P:
                D[cj][pi] = lsh.jDistance(TS[pi], TS[cj])
        # maximum among the minimum distances
        j, jmax = 0, -1
        for cj in D.keys():
            min_di = min(D[cj].values())
            if min_di > jmax:
                j, jmax = cj, min_di
        return j

    # # # # # # # # # # # # # # # # # # # # # #

    ptime_start = time.clock()

    TS = loadTestSuite(input_file)

    # budget B modification
    if B == 0:
        B = len(TS)

    U = TS.copy()

    TS[0] = set()
    P = [0]

    C = generate(U)

    iteration, total = 0, float(len(U))
    while len(U) > 0:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(C) == 0:
            C = generate(U)
        s = select(TS, P, C)
        P.append(s)

        # select budget B
        if len(P) >= B+1:
            break

        del U[s]
        C = C - set([s])

    ptime = time.clock() - ptime_start

    return 0.0, ptime, P[1:]


# JIANG (ART-D ADEQUATE)
# dynamic candidate set
def artdAdequacy(input_file, B=0):
    def generate(U):
        C, T = set(), set()
        while True:
            ui = random.choice(list(U.keys()))
            S = U[ui]
            if T | S == T:
                break
            T = T | S
            C.add(ui)
        return C

    def select(TS, P, C):
        D = {}
        for cj in C:
            D[cj] = {}
            for pi in P:
                D[cj][pi] = lsh.jDistance(TS[pi], TS[cj])
        # maximum among the minimum distances
        j, jmax = 0, -1
        for cj in D.keys():
            min_di = min(D[cj].values())
            if min_di > jmax:
                j, jmax = cj, min_di
        return j

    # # # # # # # # # # # # # # # # # # # # # #

    ptime_start = time.clock()

    TS = loadTestSuite(input_file)

    # budget B modification
    if B == 0:
        B = len(TS)

    U = TS.copy()

    TS[0] = set()
    P = [0]

    Cg = set()
    maxC = len(reduce(lambda x, y: x | y, TS.values()))
    C = generate(U)

    iteration, total = 0, float(len(U))
    while len(U) > 0:
        if len(Cg) == maxC:
            break
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(C) == 0:
            C = generate(U)
        s = select(TS, P, C)
        P.append(s)

        # select budget B
        if len(P) >= B+1:
            break

        Cg = Cg | U[s]
        del U[s]
        C = C - set([s])

    ptime = time.clock() - ptime_start

    return 0.0, ptime, P[1:]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# ZHOU (ART-F)
# fixed size candidate set + manhattan distance
def artf(input_file, B=0):
    def generate(U):
        C = set()
        if len(U) < 10:
            C = set(U.keys())
        else:
            keys = list(U.keys())
            while len(C) < 10:
                ui = random.choice(keys)
                C.add(ui)
        return C

    def manhattanDistance(TCS, i, j):
        u, v = TCS[i], TCS[j]
        return sum([abs(float(ui) - float(vi)) for ui, vi in zip(u, v)])

    def select(TS, P, C):
        D = {}
        for cj in C:
            D[cj] = {}
            for pi in P:
                D[cj][pi] = manhattanDistance(TS, pi, cj)
        # maximum among the minimum distances
        j, jmax = 0, -1
        for cj in D.keys():
            min_di = min(D[cj].values())
            if min_di > jmax:
                j, jmax = cj, min_di

        return j

    # # # # # # # # # # # # # # # # # # # # # #

    ptime_start = time.clock()

    TS = loadTestSuite(input_file)

    # budget B modification
    if B == 0:
        B = len(TS)

    U = TS.copy()

    TS[0] = set()
    P = [0]

    C = generate(U)

    iteration, total = 0, float(len(U))
    while len(U) > 0:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(C) == 0:
            C = generate(U)
        s = select(TS, P, C)
        P.append(s)

        # select budget B
        if len(P) >= B+1:
            break

        del U[s]
        C = C - set([s])

    ptime = time.clock() - ptime_start

    return 0.0, ptime, P[1:]


# ZHOU (ART-F ADEQUATE)
# fixed size candidate set + manhattan distance
def artfAdequacy(input_file, B=0):
    def generate(U):
        C = set()
        if len(U) < 10:
            C = set(U.keys())
        else:
            keys = list(U.keys())
            while len(C) < 10:
                ui = random.choice(keys)
                C.add(ui)
        return C

    def manhattanDistance(TCS, i, j):
        u, v = TCS[i], TCS[j]
        return sum([abs(float(ui) - float(vi)) for ui, vi in zip(u, v)])

    def select(TS, P, C):
        D = {}
        for cj in C:
            D[cj] = {}
            for pi in P:
                D[cj][pi] = manhattanDistance(TS, pi, cj)
        # maximum among the minimum distances
        j, jmax = 0, -1
        for cj in D.keys():
            min_di = min(D[cj].values())
            if min_di > jmax:
                j, jmax = cj, min_di

        return j

    # # # # # # # # # # # # # # # # # # # # # #

    ptime_start = time.clock()

    TS = loadTestSuite(input_file)

    # budget B modification
    if B == 0:
        B = len(TS)

    U = TS.copy()

    TS[0] = set()
    P = [0]

    Cg = set()
    maxC = len(reduce(lambda x, y: x | y, TS.values()))
    C = generate(U)

    iteration, total = 0, float(len(U))
    while len(U) > 0:
        if len(Cg) == maxC:
            break
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(C) == 0:
            C = generate(U)
        s = select(TS, P, C)
        P.append(s)

        # select budget B
        if len(P) >= B+1:
            break

        Cg = Cg | U[s]
        del U[s]
        C = C - set([s])

    ptime = time.clock() - ptime_start

    return 0.0, ptime, P[1:]

