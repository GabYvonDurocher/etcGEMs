# calibration_configD_NLDM_recipe_P8_zeus — what is here, and what is not

P8 (2026-09-09) ran configuration D NLDM under zeus-mcmc 2.5.4 (40 walkers, all sixteen
parameters, P6's model/data/priors/c_max, 16 processes) from P4's final ensemble state.
The 1500-step run was **stopped before its first 250-step checkpoint** (2 h 2 min of wall
clock, no chain written: the driver checkpoints per block and the first block never
completed — one worker's sequential slice loop starved the other fifteen). `chain.npy` /
`log_prob.npy` here are the **30-step measured cost diagnostic** that replaced it
(`reports/P8_ridge/task2b_cost.py`, blocks of 10): 20.4 s/step, 1.86 evaluations per walker
per step, 10 % utilisation, τ_max 0.9 / 2.0 / 3.2 at steps 10 / 20 / 30. Nothing in this
directory is a posterior. See `reports/P8_ridge/DECISIONS.md` D4–D5.
