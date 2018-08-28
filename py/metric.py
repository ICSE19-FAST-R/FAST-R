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

from collections import defaultdict
from pickle import load


def fft(selection, faultMatrix, javaFlag):
    if javaFlag:
        faultyTCS = set()
        with open(faultMatrix) as fIn:
            for line in fIn:
                faultyTCS.add(int(line.strip()))
        for pos, tc in enumerate(selection):
            if tc in faultyTCS:
                return pos+1
        return -1.0
    else:
        faultsDict = getFaultDetected(faultMatrix)
        for pos, tc in enumerate(selection):
            if len(faultsDict[tc]) != 0:
                return pos+1
        return -1.0


def tsr(selection, faultMatrix, inputFile):
    with open(inputFile) as fIn:
        numOfTCS = sum((1 for line in fIn))
    return (numOfTCS - len(selection)) / numOfTCS


def fdl(selection, faultMatrix, javaFlag):
    if javaFlag:
        faultyTCS = set()
        with open(faultMatrix) as fIn:
            for line in fIn:
                faultyTCS.add(int(line.strip()))
        dFaults = 1.0 if len(set(selection) & faultyTCS) > 0.0 else 0.0
        return 1.0 - dFaults / 1.0
    else:
        faultsDict = getFaultDetected(faultMatrix)
        totalFaults = set()
        detectedFaults = set()

        for tc in selection:
            for f in faultsDict[tc]:
                detectedFaults.add(f)

        for faults in faultsDict.values():
            for f in faults:
                totalFaults.add(f)

        return (len(totalFaults) - len(detectedFaults)) / len(totalFaults)



def apfd(prioritization, fault_matrix, javaFlag):
    """INPUT:
    (list)prioritization: list of prioritization of test cases
    (str)fault_matrix: path of fault_matrix (pickle file)
    (bool)javaFlag: True if output for Java fault_matrix

    OUTPUT:
    (float)APFD = 1 - (sum_{i=1}^{m} t_i / n*m) + (1 / 2n)
    n = number of test cases
    m = number of faults detected
    t_i = position of first test case revealing fault i in the prioritization
    Average Percentage of Faults Detected
    """

    if javaFlag:
        # key=version, val=[faulty_tcs]
        faults_dict = getFaultDetected(fault_matrix)
        apfds = []
        for v in range(1, len(faults_dict)+1):
            faulty_tcs = set(faults_dict[v])
            numerator = 0.0  # numerator of APFD
            position = 1
            m = 0.0
            for tc_ID in prioritization:
                if tc_ID in faulty_tcs:
                    numerator, m = position, 1.0
                    break
                position += 1

            n = len(prioritization)
            apfd = 1.0 - (numerator / (n * m)) + (1.0 / (2 * n)) if m > 0 else 0.0
            apfds.append(apfd)

        return apfds

    else:
        # dict: key=tcID, val=[detected faults]
        faults_dict = getFaultDetected(fault_matrix)
        detected_faults = set()
        numerator = 0.0  # numerator of APFD
        position = 1
        for tc_ID in prioritization:
            for fault in faults_dict[tc_ID]:
                if fault not in detected_faults:
                    detected_faults.add(fault)
                    numerator += position
            position += 1

        n, m = len(prioritization), len(detected_faults)
        apfd = 1.0 - (numerator / (n * m)) + (1.0 / (2 * n)) if m > 0 else 0.0

        return apfd


def getFaultDetected(fault_matrix):
    """INPUT:
    (str)fault_matrix: path of fault_matrix (pickle file)

    OUTPUT:
    (dict)faults_dict: key=tcID, val=[detected faults]
    """
    faults_dict = defaultdict(list)

    with open(fault_matrix, "rb") as picklefile:
        pickledict = load(picklefile)
    for key in pickledict.keys():
        faults_dict[int(key)] = pickledict[key]

    return faults_dict
