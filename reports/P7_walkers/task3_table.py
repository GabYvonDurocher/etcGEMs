#!/usr/bin/env python3
"""P7 TASK 3/4 -- the checkpoint table from chain.h5, with P6's 40-walker checkpoints beside it,
and the ensemble spread at start and end. Applies the TASK 2 rule (DECISIONS D3) mechanically.

Writes task3_checkpoints.csv, task3_spread.csv and task3_verdict.json beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)
import emcee                                                              # noqa: E402
from etcgem.calibration_multi import build_gasflux_specs                  # noqa: E402

OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P7_w128")
# P6's 40-walker checkpoints, same fit, same start, from reports/P6_convergence/run_fits.log
P6 = {250: 28.1, 500: 53.4, 750: 78.5, 1000: 103.5, 1250: 128.9, 1500: 155.9}
P6_S_PER_STEP = 1.86
specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); names = [s.name for s in specs]


def main():
    b = emcee.backends.HDFBackend(os.path.join(OUT, "chain.h5"), read_only=True)
    ch = b.get_chain(); acc = b.accepted / float(b.iteration)
    summ = json.load(open(os.path.join(OUT, "summary.json")))["sampler"] if os.path.exists(os.path.join(OUT, "summary.json")) else {}
    s_per_step = summ.get("wall_time_s", np.nan) / summ.get("n_steps", np.nan) if summ else np.nan
    N, W = ch.shape[0], ch.shape[1]
    rows, prev = [], 0.0
    for n in range(250, N + 1, 250):
        tau = np.array(emcee.autocorr.integrated_time(ch[:n], tol=0), float); k = int(np.argmax(tau))
        tm = float(tau[k]); inc = tm - prev; prev = tm
        rows.append(dict(N=n, walkers=W, tau_max=round(tm, 1), carrier=names[k], increment=round(inc, 1),
                         tau_min=round(float(tau.min()), 1), chain_over_tau=round(n / tm, 1),
                         n_eff_walkers_steps_over_tau=round(W * n / tm), acceptance=round(float(acc.mean()), 3),
                         wall_min=round(n * s_per_step / 60, 1) if np.isfinite(s_per_step) else "",
                         p6_40w_tau_max=P6.get(n, ""), p6_40w_increment=(round(P6[n] - P6.get(n - 250, 0.0), 1) if n in P6 else ""),
                         p6_40w_chain_over_tau=(round(n / P6[n], 1) if n in P6 else ""),
                         p6_40w_n_eff=(round(40 * n / P6[n]) if n in P6 else ""),
                         p6_40w_wall_min=(round(n * P6_S_PER_STEP / 60, 1) if n in P6 else "")))
        print(f"[p7] N={n:5d} tau_max {tm:6.1f} ({names[k]:14s}) +{inc:5.1f}  chain/tau {n/tm:4.1f}  n_eff {W*n/tm:6.0f}  "
              f"| 40w: tau {P6.get(n, float('nan')):6.1f} chain/tau {n/P6[n] if n in P6 else float('nan'):4.1f}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task3_checkpoints.csv"), index=False)
    # spread start / end, natural units, per parameter; against P4's 40-walker final spread
    init = json.load(open(os.path.join(OUT, "init_128.json")))
    def nat(x, s): return np.exp(x) if s.space == "log" else x
    sp = []
    for j, s in enumerate(specs):
        a, z = nat(ch[0, :, j], s), nat(ch[-1, :, j], s)
        p4 = np.load(os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_cmax120", "chain.npy"))[-1, :, j]
        sp.append(dict(param=s.name, sd_start=a.std(), sd_end=z.std(), sd_p4_40w_final=nat(p4, s).std(),
                       median_start=np.median(a), median_end=np.median(z), end_over_start=z.std() / a.std()))
    sdf = pd.DataFrame(sp); sdf.to_csv(os.path.join(HERE, "task3_spread.csv"), index=False)
    # the TASK 2 rule
    last3 = df[df.N.isin([1000, 1250, 1500])].increment.to_numpy(float) if N >= 1500 else np.array([])
    tau1500 = float(df[df.N == 1500].tau_max.iloc[0]) if N >= 1500 else np.nan
    first = float(df.increment.iloc[0])
    verdict = None
    if len(last3) == 3:
        mixing = (last3.mean() < 10) and (tau1500 < 100)
        partial = (not mixing) and (last3.mean() < 20) and bool((last3 < first).all())
        verdict = "MIXING" if mixing else ("PARTIAL" if partial else "NOT MIXING")
    v = dict(N=N, walkers=W, tau_max_1500=tau1500, mean_increment_last3=float(last3.mean()) if len(last3) else None,
             increments=df.increment.tolist(), first_increment=first, verdict_at_1500=verdict,
             rule="MIXING: mean increment over steps 750->1500 < 10 per block AND tau_max(1500) < 100; PARTIAL: mean < 20 and each of the last three below the first; else NOT MIXING")
    if N >= 2500:
        l3 = df[df.N.isin([2000, 2250, 2500])].increment.to_numpy(float); t25 = float(df[df.N == 2500].tau_max.iloc[0])
        v.update(tau_max_2500=t25, mean_increment_last3_at_2500=float(l3.mean()),
                 verdict_at_2500=("MIXING" if (l3.mean() < 10 and t25 < 100) else "PARTIAL" if (l3.mean() < 20 and (l3 < first).all()) else "NOT MIXING"))
    json.dump(v, open(os.path.join(HERE, "task3_verdict.json"), "w"), indent=2)
    print(f"[p7] verdict: {json.dumps({k: v[k] for k in v if k != 'rule'})}", flush=True)
    pd.set_option("display.width", 200); print(sdf.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
