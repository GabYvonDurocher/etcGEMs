import sys, os, json, numpy as np
sys.path.insert(0,"src"); sys.path.insert(0,"reports/P4_refit"); sys.path.insert(0,"reports/P3_gate")
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood
from fits import E_TABLE, R2A_LB
import gate_def as G
sys.path.insert(0,"reports/P5_lb_cmax")
from task1e_reoptimise import his_theta_in_our_specs
ctx,specs=_build_gasflux_ctx(strain="eciML1515", medium="LB", experiment="gasflux_configE", table=R2A_LB, otu=2, c_max=450.0, etc_table=E_TABLE, apply_protons=False, fit_clearance=False)
th0,_=his_theta_in_our_specs("/Users/g.yvon-durocher/Downloads/etcGEMs-main_3/strains/eciML1515/outputs/calibration_configE_LB_freecmax", specs)
k=[s.name for s in specs].index("F_ETC_mult")
th1=th0.copy(); th1[k]+=0.5
seq=[("th0",th0),("th0 again",th0),("th1 (F_ETC x1.65)",th1),("th0 after th1",th0),("th1 again",th1),("th0 again",th0)]
for name,th in seq: print(f"[state] {name:22s} logL = {gasflux_log_likelihood(th,ctx,specs):.4f}", flush=True)
print("[state] done")
