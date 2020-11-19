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
import math
import os
import random
import sys
import time

from functools import reduce
import numpy as np

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.random_projection import johnson_lindenstrauss_min_dim
from sklearn.random_projection import SparseRandomProjection

import lsh


"""
This file implements FAST-R test suite reduction algorithms for the Adequate scenario.
"""

# utility function to load test suite
def loadTestSuite(input_file, bbox=False, k=5):
    TS = defaultdict()
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

# store signatures on disk for future re-use
def storeSignatures(input_file, sigfile, hashes, bbox=False, k=5):
    with open(sigfile, "w") as sigfile:
        with open(input_file) as fin:
            tcID = 1
            for tc in fin:
                if bbox:
                    # shingling
                    tc_ = tc[:-1]
                    tc_shingles = set()
                    for i in range(len(tc_) - k + 1):
                        tc_shingles.add(hash(tc_[i:i + k]))

                    sig = lsh.tcMinhashing((tcID, set(tc_shingles)), hashes)
                else:
                    tc_ = tc[:-1].split()
                    sig = lsh.tcMinhashing((tcID, set(tc_)), hashes)
                for hash_ in sig:
                    sigfile.write(hash_)
                    sigfile.write(" ")
                sigfile.write("\n")
                tcID += 1

# load stored signatures
def loadSignatures(input_file):
    sig = {}
    start = time.perf_counter()
    with open(input_file, "r") as fin:
        tcID = 1
        for tc in fin:
            sig[tcID] = [i.strip() for i in tc[:-1].split()]
            tcID += 1
    return sig, time.perf_counter() - start


def loadCoverage(wBoxFile):
    C = defaultdict(set)
    with open(wBoxFile) as fin:
        for tc, cov in enumerate(fin):
            C[tc+1] = set(cov.split())
    return C


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# FAST-PW (pairwise comparison with candidate set)
def fast_pw(input_file, wBoxFile, r, b, bbox=False, k=5, memory=False):
    n = r * b  # number of hash functions

    tC0 = time.perf_counter()
    C = loadCoverage(wBoxFile)
    tC1 = time.perf_counter()
    maxCov = reduce(lambda x, y: x | y, C.values())

    hashes = [lsh.hashFamily(i) for i in range(n)]

    if memory:
        test_suite = loadTestSuite(input_file, bbox=bbox, k=k)
        # generate minhashes signatures
        mh_t = time.perf_counter()
        tcs_minhashes = {tc[0]: lsh.tcMinhashing(tc, hashes)
                         for tc in test_suite.items()}
        mh_time = time.perf_counter() - mh_t
        ptime_start = time.perf_counter()

    else:
        # loading input file and generating minhashes signatures
        sigfile = input_file.replace(".txt", ".sig")
        sigtimefile = "{}_sigtime.txt".format(input_file.split(".")[0])
        if not os.path.exists(sigfile):
            mh_t = time.perf_counter()
            storeSignatures(input_file, sigfile, hashes, bbox, k)
            mh_time = time.perf_counter() - mh_t
            with open(sigtimefile, "w") as fout:
                fout.write(repr(mh_time))
        else:
            with open(sigtimefile, "r") as fin:
                mh_time = eval(fin.read().replace("\n", ""))

        ptime_start = time.perf_counter()
        tcs_minhashes, load_time = loadSignatures(sigfile)

    tcs = set(tcs_minhashes.keys())

    BASE = 0.5
    SIZE = int(len(tcs)*BASE) + 1

    bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)

    prioritized_tcs = [0]

    # First TC

    selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
    first_tc = random.choice(list(tcs_minhashes.keys()))

    for i in range(n):
        if tcs_minhashes[first_tc][i] < selected_tcs_minhash[i]:
            selected_tcs_minhash[i] = tcs_minhashes[first_tc][i]
    prioritized_tcs.append(first_tc)

    cov = C[first_tc]
    for tc in C.keys():
        C[tc] = C[tc] - cov
        if tc in tcs and len(C[tc]) == 0:
            tcs -= set([tc])
            del tcs_minhashes[tc]

    iteration, total = 0, float(len(tcs_minhashes))
    while cov != maxCov:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(tcs_minhashes) < SIZE:
            bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)
            SIZE = int(SIZE*BASE) + 1

        sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                     b, r, n)
        filtered_sim_cand = sim_cand.difference(prioritized_tcs)
        candidates = tcs - filtered_sim_cand

        if len(candidates) == 0:
            selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
            sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                         b, r, n)
            filtered_sim_cand = sim_cand.difference(prioritized_tcs)
            candidates = tcs - filtered_sim_cand
            if len(candidates) == 0:
                candidates = tcs_minhashes.keys()

        selected_tc, max_dist = random.choice(tuple(candidates)), -1
        for candidate in tcs_minhashes:
            if candidate in candidates:
                dist = lsh.jDistanceEstimate(
                    selected_tcs_minhash, tcs_minhashes[candidate])
                if dist > max_dist:
                    selected_tc, max_dist = candidate, dist

        for i in range(n):
            if tcs_minhashes[selected_tc][i] < selected_tcs_minhash[i]:
                selected_tcs_minhash[i] = tcs_minhashes[selected_tc][i]

        prioritized_tcs.append(selected_tc)

        cov = cov | C[selected_tc]
        for tc in C.keys():
            C[tc] = C[tc] - cov
            if tc in tcs and len(C[tc]) == 0:
                tcs -= set([tc])
                del tcs_minhashes[tc]


    ptime = time.perf_counter() - ptime_start

    max_ts_size = sum((1 for line in open(input_file)))
    return mh_time, tC1-tC0, ptime, prioritized_tcs[1:max_ts_size]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# FAST-f (for any input function f, i.e., size of candidate set)
def fast_(input_file, wBoxFile, selsize, r, b, bbox=False, k=5, memory=False):
    n = r * b  # number of hash functions

    tC0 = time.perf_counter()
    C = loadCoverage(wBoxFile)
    tC1 = time.perf_counter()
    maxCov = reduce(lambda x, y: x | y, C.values())

    hashes = [lsh.hashFamily(i) for i in range(n)]

    if memory:
        test_suite = loadTestSuite(input_file, bbox=bbox, k=k)
        # generate minhashes signatures
        mh_t = time.perf_counter()
        tcs_minhashes = {tc[0]: lsh.tcMinhashing(tc, hashes)
                         for tc in test_suite.items()}
        mh_time = time.perf_counter() - mh_t
        ptime_start = time.perf_counter()

    else:
        # loading input file and generating minhashes signatures
        sigfile = input_file.replace(".txt", ".sig")
        sigtimefile = "{}_sigtime.txt".format(input_file.split(".")[0])
        if not os.path.exists(sigfile):
            mh_t = time.perf_counter()
            storeSignatures(input_file, sigfile, hashes, bbox, k)
            mh_time = time.perf_counter() - mh_t
            with open(sigtimefile, "w") as fout:
                fout.write(repr(mh_time))
        else:
            with open(sigtimefile, "r") as fin:
                mh_time = eval(fin.read().replace("\n", ""))

        ptime_start = time.perf_counter()
        tcs_minhashes, load_time = loadSignatures(sigfile)

    tcs = set(tcs_minhashes.keys())

    BASE = 0.5
    SIZE = int(len(tcs)*BASE) + 1

    bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)

    prioritized_tcs = [0]

    # First TC

    selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
    first_tc = random.choice(list(tcs_minhashes.keys()))
    for i in range(n):
        if tcs_minhashes[first_tc][i] < selected_tcs_minhash[i]:
            selected_tcs_minhash[i] = tcs_minhashes[first_tc][i]
    prioritized_tcs.append(first_tc)

    cov = C[first_tc]
    for tc in C.keys():
        C[tc] = C[tc] - cov
        if tc in tcs and len(C[tc]) == 0:
            tcs -= set([tc])
            del tcs_minhashes[tc]

    iteration, total = 0, float(len(tcs_minhashes))
    while cov != maxCov:
        iteration += 1
        if iteration % 100 == 0:
            sys.stdout.write("  Progress: {}%\r".format(
                round(100*iteration/total, 2)))
            sys.stdout.flush()

        if len(tcs_minhashes) < SIZE:
            bucket = lsh.LSHBucket(tcs_minhashes.items(), b, r, n)
            SIZE = int(SIZE*BASE) + 1

        sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                     b, r, n)
        filtered_sim_cand = sim_cand.difference(prioritized_tcs)
        candidates = tcs - filtered_sim_cand

        if len(candidates) == 0:
            selected_tcs_minhash = lsh.tcMinhashing((0, set()), hashes)
            sim_cand = lsh.LSHCandidates(bucket, (0, selected_tcs_minhash),
                                         b, r, n)
            filtered_sim_cand = sim_cand.difference(prioritized_tcs)
            candidates = tcs - filtered_sim_cand
            if len(candidates) == 0:
                candidates = tcs_minhashes.keys()

        to_sel = min(selsize(len(candidates)), len(candidates))
        selected_tc_set = random.sample(tuple(candidates), to_sel)

        for selected_tc in selected_tc_set:
            for i in range(n):
                if tcs_minhashes[selected_tc][i] < selected_tcs_minhash[i]:
                    selected_tcs_minhash[i] = tcs_minhashes[selected_tc][i]
            prioritized_tcs.append(selected_tc)
            cov = cov | C[selected_tc]

        for tc in C.keys():
            C[tc] = C[tc] - cov
            if tc in tcs and len(C[tc]) == 0:
                tcs -= set([tc])
                del tcs_minhashes[tc]


    ptime = time.perf_counter() - ptime_start

    max_ts_size = sum((1 for line in open(input_file)))
    return mh_time, tC1-tC0, ptime, prioritized_tcs[1:max_ts_size]


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Preparation + utils

# load coverage (only for wbox usage)
def loadCoverage(wBoxFile):
    C = defaultdict(set)
    with open(wBoxFile) as fin:
        for tc, cov in enumerate(fin):
            C[tc] = set(cov.split())
    return C

# compute euclidean distance
def euclideanDist(v, w):
    d = 0

    for k in v.keys():
        if k not in w.keys():
            d += v[k] ** 2
        else:
            d += (v[k] - w[k]) ** 2

    for k in w.keys():
        if k not in v.keys():
            d += w[k] ** 2

    return math.sqrt(d)

# Preparation phase for FAST++ and FAST-CS
def preparation(inputFile, dim=0):
    vectorizer = HashingVectorizer()  # compute "TF"
    testCases = [line.rstrip("\n") for line in open(inputFile)]
    testSuite = vectorizer.fit_transform(testCases)

    # dimensionality reduction
    if dim <= 0:
        e = 0.5  # epsilon in jl lemma
        dim = johnson_lindenstrauss_min_dim(len(testCases), eps=e)
    srp = SparseRandomProjection(n_components=dim)
    projectedTestSuite = srp.fit_transform(testSuite)

    # map sparse matrix to dict
    TS = []
    for i in range(len(testCases)):
        tc = {}
        for j in projectedTestSuite[i].nonzero()[1]:
            tc[j] = projectedTestSuite[i, j]
        TS.append(tc)

    return TS


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# FAST++

# FAST++ Reduction phase
def reductionPlusPlus(TS, C, S):
    reducedTS = []

    maxCov = reduce(lambda x, y: x | y, C.values())

    # distance to closest center
    D = defaultdict(lambda:float('Inf'))
    # select first center randomly
    selectedTC = random.randint(0, len(TS)-1)
    reducedTS.append(selectedTC + 1)
    D[selectedTC] = 0

    # adequacy filtering
    cov = C[selectedTC]
    for tc in C.keys():
        C[tc] = C[tc] - cov
        if len(C[tc]) == 0:
            D[tc] = 0

    while cov != maxCov:
        # k-means++ tc selection
        norm = 0
        for tc in range(len(TS)):
            if D[tc] != 0:
                dist = euclideanDist(TS[tc], TS[selectedTC])
                dist *= dist
                if dist < D[tc]:
                    D[tc] = dist
            norm += D[tc]

        # safe exit point (if all distances are 0)
        # (but not all test cases have been selected)
        if norm == 0:
            extraTCS = set(range(1, len(TS)+1)) - set(reducedTS)
            extraTCS = [x-1 for x in extraTCS]
            while cov != maxCov:
                for tc in extraTCS:
                    selectedTC, selTCcov = tc, len(C[tc])
                    break
                for tc in extraTCS:
                    if len(C[tc]) > selTCcov:
                        selTCcov = len(C[tc])
                        selectedTC = tc
                extraTCS.remove(selectedTC)
                reducedTS.append(selectedTC + 1)

                # adequacy filtering
                cov = cov | C[selectedTC]
                for tc in C.keys():
                    C[tc] = C[tc] - cov

            break

        s = 0
        sel = set()
        while s < S and cov != maxCov:
            s += 1
            c = 0
            coinToss = random.random() * norm
            for tc, dist in D.items():
                if coinToss < c + dist:
                    if tc not in sel:
                        sel.add(tc)
                    break
                c += dist

        for selectedTC in sel:
            reducedTS.append(selectedTC + 1)
            D[selectedTC] = 0

            # adequacy filtering
            cov = cov | C[selectedTC]
            for tc in C.keys():
                C[tc] = C[tc] - cov
                if len(C[tc]) == 0:
                    D[tc] = 0

    return reducedTS

# FAST++ test suite reduction algorithm
# Returns: preparation time, reduction time, reduced test suite
def fastPlusPlus(inputFile, wBoxFile, dim=0, S=1, memory=True):
    if memory:
        t0 = time.perf_counter()
        TS = preparation(inputFile, dim=dim)
        t1 = time.perf_counter()
        pTime = t1-t0
    else:
        rpFile = inputFile.replace(".txt", ".rp")
        if not os.path.exists(rpFile):
            t0 = time.perf_counter()
            TS = preparation(inputFile, dim=dim)
            t1 = time.perf_counter()
            pTime = t1-t0
            pickle.dump((pTime, TS), open(rpFile, "wb"))
        else:
            pTime, TS = pickle.load(open(rpFile, "rb"))

    tC0 = time.perf_counter()
    C = loadCoverage(wBoxFile)
    tC1 = time.perf_counter()

    t2 = time.perf_counter()
    reducedTS = reductionPlusPlus(TS, C, S)
    t3 = time.perf_counter()

    return pTime, tC1-tC0, t3-t2, reducedTS


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# FAST-CS

# FAST-CS Reduction phase
def reductionCS(TS, C, simple=True):
    reducedTS = []

    maxCov = reduce(lambda x, y: x | y, C.values())
    cov = set()

    # compute center of mass
    centerOfMass = defaultdict(float)
    for tc in TS:
        for k, v in tc.items():
            centerOfMass[k] += v
    # normalize
    for k in centerOfMass.keys():
        centerOfMass[k] /= len(TS)

    # compute distances
    D = defaultdict(float)
    norm = 0
    for tc in range(len(TS)):
        dist = euclideanDist(TS[tc], centerOfMass)
        D[tc] = dist*dist
        norm += D[tc]

    uselessTCS = set()
    while cov != maxCov:
        # compute probabilities of being sampled
        P = []
        if norm != 0:
            p = 1.0 / (2*(len(TS)-len(uselessTCS)))
            for tc in range(len(TS)):
                P.append(p + D[tc] / (2*norm))
        else:
            P = [1.0 / (len(TS)-len(uselessTCS))] * len(TS)

        for tc in uselessTCS:
            P[tc] = 0.0

        # numeric error: when sum of P != 1
        toSelect = set(range(len(TS))) - uselessTCS - {x-1 for x in reducedTS}
        P[random.choice(list(toSelect))] += 1.0 - sum(P)

        # proportional sampling
        if simple:
            selectedTC = np.random.choice(list(range(len(TS))), p=P, replace=False)
            reducedTS.append(selectedTC + 1)
            # adequate filtering
            cov = cov | C[selectedTC]
            for tc in C.keys():
                C[tc] = C[tc] - cov
                if len(C[tc]) == 0:
                    uselessTCS.add(tc)
                    norm -= D[tc]
                    D[tc] = 0

        else:
            selectedTCS = np.random.choice(list(range(len(TS))), size=1+int(math.log(len(TS), 2)), p=P, replace=False)
            for selectedTC in selectedTCS:
                reducedTS.append(selectedTC + 1)
                # adequate filtering
                cov = cov | C[selectedTC]

            # adequate filtering
            for tc in C.keys():
                C[tc] = C[tc] - cov
                if len(C[tc]) == 0:
                    uselessTCS.add(tc)
                    norm -= D[tc]
                    D[tc] = 0

    return reducedTS

# FAST-CS test suite reduction algorithm
# Returns: preparation time, reduction time, reduced test suite
def fastCS(inputFile, wBoxFile, dim=0, memory=True, simple=True):
    if memory:
        t0 = time.perf_counter()
        TS = preparation(inputFile, dim=dim)
        t1 = time.perf_counter()
        pTime = t1-t0
    else:
        rpFile = inputFile.replace(".txt", ".rp")
        if not os.path.exists(rpFile):
            t0 = time.perf_counter()
            TS = preparation(inputFile, dim=dim)
            t1 = time.perf_counter()
            pTime = t1-t0
            pickle.dump((pTime, TS), open(rpFile, "wb"))
        else:
            pTime, TS = pickle.load(open(rpFile, "rb"))

    tC0 = time.perf_counter()
    C = loadCoverage(wBoxFile)
    tC1 = time.perf_counter()

    t2 = time.perf_counter()
    reducedTS = reductionCS(TS, C, simple)
    t3 = time.perf_counter()
    sTime = t3-t2

    return pTime, tC1-tC0, sTime, reducedTS
