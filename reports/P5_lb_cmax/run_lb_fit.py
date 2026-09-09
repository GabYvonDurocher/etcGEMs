#!/usr/bin/env python3
"""P5 TASK 1b -- ONE fit (OUTCOME: the chain is TRAPPED IN A DEAD MODE by the warm start --
growth R2 -2.19, zero growth everywhere; see DECISIONS D3 and OPEN_ITEMS 3.20. Kept as that
record; the c_max question is answered by task1c/1d/1e instead): configuration D on LB, recipe ceilings, transporter k_cat 300, at
c_max = 257, with exactly P4's sampler settings. A diagnostic against P4's own D_LB refit at
c_max 120 (growth R2 0.196), NOT a converged result: both chains are 2000 steps against
tau ~ 220, i.e. ~9 autocorrelation times against the >= 40 criterion.

Why 257: it is the c_max of Parsa's own configuration-D LB fit at its MAP (230 x 1.116 =
256.7, read from his chain in task1_parsa_lb_cmax.py), which is the point P3's gate
reproduced his 0.90 at. So the two things this fit changes relative to his are the medium
convention (recipe ceilings, as P4) and a FIXED rather than sampled cap -- and the only thing
it changes relative to P4's D_LB is the cap, 120 -> 257.

Writes to strains/eciML1515/outputs/calibration_configD_LB_recipe_cmax257/ (new directory;
nothing of P4's or Parsa's is touched) and a scores.json beside the chain, then
lb_cmax_comparison.csv in this directory.

    python reports/P5_lb_cmax/run_lb_fit.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "reports", "P4_refit"))
os.chdir(ROOT)

from etcgem.calibration_multi import run_gasflux_fit          # noqa: E402
from run_fits import score, STEPS, WALKERS                     # noqa: E402  (P4's scorer, unchanged)
from fits import R2A_LB                                        # noqa: E402  (P4's data table)

C_MAX = 257.0
LABEL, CFG, MEDIUM, OTU = "D_LB_cmax257", "D", "LB", 2
REL = os.path.join("strains", "eciML1515", "outputs", "calibration_configD_LB_recipe_cmax257")
OUT = os.path.join(ROOT, REL)


def main():
    t0 = time.time()
    if not os.path.exists(os.path.join(OUT, "summary.json")):
        res = run_gasflux_fit("eciML1515", OUT, medium=MEDIUM, table=R2A_LB, otu=OTU,
                              experiment=f"gasflux_config{CFG}", c_max=C_MAX,
                              etc_table=None, apply_protons=False, fit_clearance=False,
                              label=LABEL, n_walkers=WALKERS, n_steps_max=STEPS[CFG], seed=1)
        s = res["sampler"]
        print(f"[p5] {LABEL}: {s['n_steps']} steps x {s['n_walkers']} walkers, "
              f"{s['wall_time_s'] / 60:.1f} min, accept {s['acceptance_fraction']}, "
              f"tau {s['autocorr_time_max']}, n_eff {s['n_eff']}, "
              f"{'CONVERGED' if s['converged'] else 'NOT CONVERGED'}: {s['stop_reason']}", flush=True)
    else:
        print(f"[p5] {LABEL}: summary.json exists, scoring only", flush=True)
    sc = score(OUT, LABEL, CFG, MEDIUM, R2A_LB, OTU, C_MAX, None, False, False)
    # the comparison row, beside P4's D_LB at c_max 120 and Parsa's D_LB (blanket, c_max fitted)
    import pandas as pd
    p4 = pd.read_csv(os.path.join(ROOT, "reports", "P4_refit", "refit_comparison.csv"))
    p4 = p4[p4.fit == "D_LB"].iloc[0]
    summ = json.load(open(os.path.join(OUT, "summary.json")))["sampler"]
    rows = []
    for point in ("MAP", "posterior median"):
        r = sc[point]
        rows.append(dict(fit="D_LB_cmax257", medium="LB (recipe)", c_max=C_MAX, point=point,
                         growth_R2=round(r["growth_R2"], 4), resp_R2=round(r["resp_R2"], 4),
                         rmax=round(r["rmax"], 4), Topt_C=r["Topt_C"], acetate_37C=round(r["acetate_37C"], 3),
                         RQ_37C=round(r["RQ_37C"], 3), resp_scale=round(r["resp_scale"], 3),
                         steps=summ["n_steps"], walkers=summ["n_walkers"], tau=summ["autocorr_time_max"],
                         chain_over_tau=round(summ["n_steps"] / summ["autocorr_time_max"], 1),
                         n_eff=summ["n_eff"], converged=summ["converged"]))
    rows.append(dict(fit="D_LB (P4)", medium="LB (recipe)", c_max=120.0, point=p4.point,
                     growth_R2=p4.growth_R2_refit, resp_R2=p4.resp_R2_refit, rmax=p4.rmax, Topt_C=p4.Topt_C,
                     acetate_37C=p4.acetate_37C, RQ_37C=p4.RQ_37C, resp_scale=p4.resp_scale,
                     steps=p4.steps, walkers=40, tau=p4.tau, chain_over_tau=round(p4.steps / p4.tau, 1),
                     n_eff=p4.n_eff, converged=False))
    rows.append(dict(fit="D_LB (Parsa, P3 gate)", medium="LB (blanket)", c_max=256.7, point="MAP",
                     growth_R2=p4.growth_R2_blanket, resp_R2=p4.resp_R2_blanket, rmax="", Topt_C="",
                     acetate_37C="", RQ_37C="", resp_scale="", steps=2000, walkers=36, tau=211.9,
                     chain_over_tau=9.4, n_eff="", converged=False))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "lb_cmax_comparison.csv"), index=False)
    pd.set_option("display.width", 220)
    print(df.to_string(index=False))
    print(f"[p5] done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
