Experiment Results
----------------

### Raw data
Here you can find the raw data used in our statistical analysis.

 - Data used for evaluating the effectiveness (fault detection loss) and efficiency (time) of the proposed approach in the **inadequate (budget) scenario**: 
   - [data_inadequate_D4J_function.tsv](data/data_inadequate_D4J_function.tsv)
   - [data_inadequate_D4J_statement.tsv](data/data_inadequate_D4J_statement.tsv)
   - [data_inadequate_D4J_branch.tsv](data/data_inadequate_D4J_branch.tsv)
   - [data_inadequate_SIR_function.tsv](data/data_inadequate_SIR_function.tsv)
   - [data_inadequate_SIR_statement.tsv](data/data_inadequate_SIR_statement.tsv)
   - [data_inadequate_SIR_branch.tsv](data/data_inadequate_SIR_branch.tsv)
 - Data used for evaluating the effectiveness (test suite reduction/fault detection loss) and efficiency (time) of the proposed approach in the **adequate scenario**: 
   - [data_adequate_D4J_function.tsv](data/data_adequate_D4J_function.tsv)
   - [data_adequate_D4J_statement.tsv](data/data_adequate_D4J_statement.tsv)
   - [data_adequate_D4J_branch.tsv](data/data_adequate_D4J_branch.tsv)
   - [data_adequate_SIR_function.tsv](data/data_adequate_SIR_function.tsv)
   - [data_adequate_SIR_statement.tsv](data/data_adequate_SIR_statement.tsv)
   - [data_adequate_SIR_branch.tsv](data/data_adequate_SIR_branch.tsv)
 - Data used for evaluating the approach in the **large-scale scenario**: 
   -[data_large_scale.tsv](data/data_large_scale.tsv)
 
---
### The inadequate (budget) scenario
Box plots for Fault Detection Loss in the inadequate (budget) scenario:
<img src="img/fdl_inadequate.png" width="51%">

Fault Detection Loss in the inadequate (budget) scenario:
<img src="img/tab_fdl_budget.png" width="55%">

Reduction times for the budget scenario (including and excluding preparation time):
<img src="img/tab_time_budget.png" width="51%">

---
### The adequate scenario
Box plots for Test Suite Reduction and Fault Detection Loss in the adequate scenario:
<img src="img/tsr_fdl_adequate.png" width="100%">

Test Suite Reduction and Fault Detection in the adequate scenario:
<img src="img/tab_tsr_fdl_adequate.png" width="55%">

Reduction times for the adequate scenario (including and excluding preparation time):
<img src="img/tab_time_adequate.png" width="51%">

---
### The large-scale scenario
Time required to reduce 500k test cases to different reduction targets:
<img src="img/totaltime.png" width="65%">
<img src="img/reductiontime.png" width="65%">

Time and space needed to compute and store prepared data by FAST-R in the large-scale scenario:
<img src="img/tab_time_space.png" width="50%">
