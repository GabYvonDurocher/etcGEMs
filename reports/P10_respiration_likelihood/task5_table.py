#!/usr/bin/env python3
"""P8 TASK 2B -- the checkpoint table for the zeus chain beside P6's 40-walker and P7's
128-walker emcee rows, tau per step AND per wall-hour, zeus's own diagnostics, and the D3 rule
applied mechanically. Writes task5_checkpoints.csv and task5_verdict.json beside this file.
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
import emcee                                                     # noqa: E402
from etcgem.calibration_multi import build_gasflux_specs         # noqa: E402

OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P10")
P6 = {250: 28.1, 500: 53.4, 750: 78.5, 1000: 103.5, 1250: 128.9, 1500: 155.9}; P6_SPS = 1.86
P7 = {250: 26.1, 500: 52.2, 750: 76.5, 1000: 99.6, 1250: 120.7, 1500: 140.8}; P7_SPS = 5.02
P8Z = {10: 0.9, 20: 2.0, 30: 3.2}   # zeus, stopped at 30 steps (P8)
names = [s.name for s in build_gasflux_specs({"use_etc": False, "fit_clearance": True})]


def main():
    import emcee as _e
    ch = _e.backends.HDFBackend(os.path.join(OUT, "chain.h5"), read_only=True).get_chain() if os.path.exists(os.path.join(OUT, "chain.h5")) else np.load(os.path.join(OUT, "chain.npy")); N, W, D = ch.shape
    summ = json.load(open(os.path.join(OUT, "summary.json"))) if os.path.exists(os.path.join(OUT, "summary.json")) else {}
    zck = {c["step"]: c for c in (summ.get("sampler", {}).get("zeus", {}) or {}).get("checkpoints", [])}
    wall_s = summ.get("sampler", {}).get("wall_time_s", np.nan); sps = wall_s / N if np.isfinite(wall_s) else np.nan
    rows, prev = [], 0.0
    for n in range(250, N + 1, 250):
        tau = np.array(emcee.autocorr.integrated_time(ch[:n], tol=0), float); k = int(np.argmax(tau)); tm = float(tau[k])
        inc = tm - prev; prev = tm
        z = zck.get(n, {})
        rows.append(dict(N=n, sampler="emcee stretch, new likelihood", walkers=W, tau_max=round(tm, 1), carrier=names[k], increment=round(inc, 1),
                         chain_over_tau=round(n / tm, 1), n_eff=round(W * n / tm), wall_min=round(n * sps / 60, 1) if np.isfinite(sps) else "",
                         tau_per_wall_hour=round(tm / (n * sps / 3600), 1) if np.isfinite(sps) else "",
                         zeus_act_max=z.get("zeus_act_max", ""), zeus_efficiency=z.get("zeus_efficiency", ""), zeus_ess=z.get("zeus_ess", ""),
                         evals_per_walker_step=z.get("evals_per_walker_step", ""),
                         p6_40w_tau=P6.get(n, ""), p6_40w_inc=(round(P6[n] - P6.get(n - 250, 0.0), 1) if n in P6 else ""),
                         p6_40w_wall_min=(round(n * P6_SPS / 60, 1) if n in P6 else ""), p6_tau_per_wall_hour=(round(P6[n] / (n * P6_SPS / 3600), 1) if n in P6 else ""),
                         p7_128w_tau=P7.get(n, ""), p7_128w_inc=(round(P7[n] - P7.get(n - 250, 0.0), 1) if n in P7 else ""),
                         p7_128w_wall_min=(round(n * P7_SPS / 60, 1) if n in P7 else "")))
        print(f"[p8] N={n:5d} zeus tau_max {tm:6.1f} ({names[k]:14s}) +{inc:5.1f} chain/tau {n/tm:4.1f} | 40w emcee {P6.get(n, float('nan')):6.1f} | 128w emcee {P7.get(n, float('nan')):6.1f}", flush=True)
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task5_checkpoints.csv"), index=False)
    first = float(df.increment.iloc[0]); v = dict(N=N, walkers=W, s_per_step=sps, increments=df.increment.tolist())
    if N >= 1500:
        l3 = df[df.N.isin([1000, 1250, 1500])].increment.to_numpy(float); t15 = float(df[df.N == 1500].tau_max.iloc[0])
        v.update(tau_max_1500=t15, mean_inc_last3=float(l3.mean()),
                 verdict_at_1500=("MIXING" if (l3.mean() < 10 and t15 < 100) else "PARTIAL" if (l3.mean() < 20 and (l3 < first).all()) else "NOT MIXING"))
    if N >= 2500:
        l3 = df[df.N.isin([2000, 2250, 2500])].increment.to_numpy(float); t25 = float(df[df.N == 2500].tau_max.iloc[0])
        v.update(tau_max_2500=t25, mean_inc_last3_2500=float(l3.mean()),
                 verdict_at_2500=("MIXING" if (l3.mean() < 10 and t25 < 100) else "PARTIAL" if (l3.mean() < 20 and (l3 < first).all()) else "NOT MIXING"))
    json.dump(v, open(os.path.join(HERE, "task5_verdict.json"), "w"), indent=2)
    print(f"[p8] verdict: {v}")


if __name__ == "__main__":
    main()
