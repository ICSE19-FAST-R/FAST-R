# Scalable Approaches for Test Suite Reduction

This repository is a companion page for an ICSE'19 submission. It contains all the material required for replicating our experiments, including: the implementation of the algorithms, the input data, and supplementary tools. 
Some additional results, not included in the paper for the sake of space, are also provided.


Pseudocode
---------------
The pseudocode of all algorithms are available [here](pseudocode/README.md) (some of them were not reported in the paper for lack of space).


Experiment Results and Data
---------------
The results of our experiments as well as the data we used for our statistical analysis are available [here](results/README.md).


Experiment Replication
---------------
In order to replicate the experiment follow these steps:

### Getting started

1. Clone the repository 
   - `git clone https://github.com/ICSE19-FAST-R/FAST-R`
 
2. Install the additional python packages required:
   - `pip3 install -r requirements.txt`

### Budget Scenario
1. Execute the `experimentBudget.py` script 
   - `python3 py/experimentBudget.py <coverageType> <program> <version>`
   
   The possible values for `<coverageType>` are: `function`, `line`, `branch`.
   
   The possible values for `<entity> <version>` are: `flex v3`, `grep v3`, `gzip v1`, `make v1`, `sed v6`, `chart v0`, `closure v0`, `lang v0`, `math v0`, `time v0`.

2. The results are printed on screen and stored inside folder `outputBudget-<coverageType>/`


### Adequate Scenario
1. Execute the `experimentAdequate.py` script 
   - `python3 py/experimentAdequate.py <coverageType> <program> <version>`
   
   The possible values for `<coverageType>` are: `function`, `line`, `branch`.
   
   The possible values for `<entity> <version>` are: `flex v3`, `grep v3`, `gzip v1`, `make v1`, `sed v6`, `chart v0`, `closure v0`, `lang v0`, `math v0`, `time v0`.

2. The results are printed on screen and stored inside folder `outputAdequate-<coverageType>/`


### Large Scale Scenario
1. Create scalability dataset
   - `cat input/scalability/scalability-bbox.txt.gz_* > input/scalability/scalability-bbox.txt.gz && gunzip input/scalability/scalability-bbox.txt.gz`

2. Execute the `experimentLargeScale.py` script 
   - `python3 py/experimentLargeScale.py <algorithm>`
   
   The possible values for `<algorithm>` are: `FAST++`, `FAST-CS`, `FAST-pw`, `FAST-all`.
   
3. The results are printed on screen and stored inside folder `outputLargeScale/`

Directory Structure
---------------
This is the root directory of the repository. The directory is structured as follows:

    FAST-R
     .
     |
     |--- input/         Input of the algorithms, i.e. fault matrix, coverage information, and BB representation of subjects.
     |
     |--- pseudocode/    Pseudocode of the algorithms.
     |
     |--- py/            Implementation of the algorithms and scripts to execute the experiments.
     |
     |--- results/       Overview of the experiment results and related raw data.
  
