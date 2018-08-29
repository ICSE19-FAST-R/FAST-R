Experiment Results
----------------

### Raw data
Here you can find the raw data used in our statistical analysis.

 - Data used for evaluating the effectiveness (fault detection loss) and efficiency (time) of the proposed approach in the **inadequate (budget) scenario**: 
 -- [data_inadequate_D4J_function.tsv](data_inadequate_D4J_function.tsv)
 -- [data_inadequate_D4J_statement.tsv](data_inadequate_D4J_statement.tsv)
 -- [data_inadequate_D4J_branch.tsv](data_inadequate_D4J_branch.tsv)
 -- [data_inadequate_SIR_function.tsv](data_inadequate_SIR_function.tsv)
 -- [data_inadequate_SIR_statement.tsv](data_inadequate_SIR_statement.tsv)
 -- [data_inadequate_SIR_branch.tsv](data_inadequate_SIR_branch.tsv)
 - Data used for evaluating the effectiveness (test suite reduction/fault detection loss) and efficiency (time) of the proposed approach in the **adequate scenario**: 
 -- [data_adequate_D4J_function.tsv](data_adequate_D4J_function.tsv)
 -- [data_adequate_D4J_statement.tsv](data_adequate_D4J_statement.tsv)
 -- [data_adequate_D4J_branch.tsv](data_adequate_D4J_branch.tsv)
 -- [data_adequate_SIR_function.tsv](data_adequate_SIR_function.tsv)
 -- [data_adequate_SIR_statement.tsv](data_adequate_SIR_statement.tsv)
 -- [data_adequate_SIR_branch.tsv](data_adequate_SIR_branch.tsv)
 - Data used for evaluating the approach in the **large-scale scenario**: 
 --[data_large_scale.tsv](data_large_scale.tsv)
 
---
### The inadequate (budget) scenario
Fault Detection Loss for the test suite reduction approaches (in %):
<img src="img/fdl_inadequate.png" width="100%">

Fault Detection Loss in the inadequate (budget) scenario:
<img src="img/tab_fdl_budget.png" width="100%">

Reduction times for the budget scenario (including and excluding preparation time):
<img src="img/tab_time_budget.png" width="100%">

---
### The adequate scenario
Test Suite Reduction and Fault Detection Loss in the adequate scenario:
<img src="img/tsr_fdl_adequate.png" width="100%">

Fault detection loss in the adequate scenario:
<img src="img/tab_tsr_fdl_adequate.png" width="100%">

Reduction times for the adequate scenario (including and excluding preparation time):
<img src="img/tab_time_adequate.png" width="100%">

---
### The large-scale scenario
Time required to reduce 500k test cases to different reduction targets:
<img src="img/totaltime.png" width="100%">
<img src="img/reductiontime.png" width="100%">

Time and space needed to compute and store prepared data by FAST-R in the large-scale scenario:
<img src="img/tab_time_space.png" width="100%">
