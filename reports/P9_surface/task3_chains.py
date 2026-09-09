#!/usr/bin/env python3
"""P9 TASK 3 -- what the existing chains say, free. P7's 128-walker chain (steps 250-1500) and
the 40-walker P4+P6 history (steps 1500-2500), post-burn-in:
  * per-walker acceptance fraction (a walker "accepted" at step t if its position changed),
    with min / quartiles / max and the count below 5 %;
  * frozen walkers: runs of >= 50 consecutive steps at a constant log-posterior, per walker;
  * accepted step lengths in standardised units against the stretch-move PROPOSAL lengths,
    reconstructed from the ensemble geometry: |Z - 1| * |X_k - X_j| with Z ~ g(z) on [1/2, 2]
    (emcee's a = 2), sampled over random walker pairs at random steps.
Writes task3_acceptance.csv, task3_steps.csv, task3_summary.json beside this file.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
import emcee                                                     # noqa: E402

OUTS = os.path.join(ROOT, "strains", "eciML1515", "outputs")


def views():
    b = emcee.backends.HDFBackend(os.path.join(OUTS, "calibration_configD_NLDM_recipe_P7_w128", "chain.h5"), read_only=True)
    v = {"128w (P7) 250-1500": (b.get_chain()[250:], b.get_log_prob()[250:])}
    d = os.path.join(OUTS, "calibration_configD_NLDM_recipe_cmax120")
    ch = np.load(os.path.join(d, "chain.npy")); lp = np.load(os.path.join(d, "log_prob.npy"))
    cont = os.path.join(ROOT, "reports", "P6_convergence", "_scratch", "bench_stretch_p10")
    if os.path.exists(os.path.join(cont, "chain.npy")):
        ch = np.concatenate([ch, np.load(os.path.join(cont, "chain.npy"))]); lp = np.concatenate([lp, np.load(os.path.join(cont, "log_prob.npy"))])
    v[f"40w (P4+P6) 1500-{ch.shape[0]}"] = (ch[1500:], lp[1500:])
    return v


def stretch_z(rng, n, a=2.0):
    # emcee's stretch: z = ((a - 1) u + 1)^2 / a, u ~ U(0,1)
    return ((a - 1.0) * rng.random(n) + 1.0) ** 2 / a


def main():
    rng = np.random.default_rng(3); acc_rows, step_rows, summary = [], [], {}
    for tag, (ch, lp) in views().items():
        S, W, D = ch.shape
        X = ch.reshape(-1, D); mu, sd = X.mean(0), X.std(0); Zc = (ch - mu) / sd
        moved = np.any(np.diff(ch, axis=0) != 0, axis=2)                    # (S-1, W)
        acc = moved.mean(axis=0)
        # frozen runs: constant log-prob for >= 50 steps
        frozen = np.zeros(W, int); longest = np.zeros(W, int)
        for w in range(W):
            same = np.diff(lp[:, w]) == 0; run = 0; best = 0; n50 = 0
            for s_ in same:
                run = run + 1 if s_ else 0
                best = max(best, run)
                if run == 49: n50 += 1
            frozen[w] = n50; longest[w] = best + 1
        for w in range(W):
            acc_rows.append(dict(view=tag, walker=w, acceptance=acc[w], frozen_runs_ge50=int(frozen[w]), longest_constant_run=int(longest[w])))
        # accepted step lengths (standardised) vs proposal lengths
        disp = np.linalg.norm(np.diff(Zc, axis=0), axis=2)                     # (S-1, W)
        accepted_len = disp[moved]
        n = 20000; t = rng.integers(0, S, n); j = rng.integers(0, W, n); k = (j + rng.integers(1, W, n)) % W
        prop_len = np.abs(stretch_z(rng, n) - 1.0) * np.linalg.norm(Zc[t, k] - Zc[t, j], axis=1)
        q = lambda x: np.percentile(x, [5, 25, 50, 75, 95]).round(3).tolist()
        step_rows.append(dict(view=tag, kind="accepted", n=int(accepted_len.size), q5_25_50_75_95=q(accepted_len), mean=float(accepted_len.mean())))
        step_rows.append(dict(view=tag, kind="proposed (reconstructed)", n=n, q5_25_50_75_95=q(prop_len), mean=float(prop_len.mean())))
        summary[tag] = dict(walkers=W, steps=S, acceptance_min=float(acc.min()), acceptance_q25=float(np.percentile(acc, 25)),
                            acceptance_median=float(np.median(acc)), acceptance_q75=float(np.percentile(acc, 75)), acceptance_max=float(acc.max()),
                            walkers_below_5pct=int((acc < 0.05).sum()), walkers_with_frozen_run_ge50=int((frozen > 0).sum()),
                            longest_constant_run_max=int(longest.max()), longest_constant_run_median=float(np.median(longest)),
                            accepted_step_median=float(np.median(accepted_len)), proposed_step_median=float(np.median(prop_len)),
                            accepted_over_proposed_median=float(np.median(accepted_len) / np.median(prop_len)),
                            sqrt_dim=float(np.sqrt(D)))
        print(f"[chains] {tag}: acceptance min {acc.min():.3f} q25 {np.percentile(acc,25):.3f} median {np.median(acc):.3f} q75 {np.percentile(acc,75):.3f} max {acc.max():.3f}; "
              f"<5 %: {(acc<0.05).sum()} of {W}; walkers with a >=50-step constant run: {(frozen>0).sum()} (longest {longest.max()}, median longest {np.median(longest):.0f}); "
              f"accepted step median {np.median(accepted_len):.3f} vs proposed {np.median(prop_len):.3f} (ratio {np.median(accepted_len)/np.median(prop_len):.2f}; sqrt(16)=4 is one sd in every parameter)", flush=True)
    pd.DataFrame(acc_rows).to_csv(os.path.join(HERE, "task3_acceptance.csv"), index=False)
    pd.DataFrame(step_rows).to_csv(os.path.join(HERE, "task3_steps.csv"), index=False)
    json.dump(summary, open(os.path.join(HERE, "task3_summary.json"), "w"), indent=2)
    print("[chains] done")


if __name__ == "__main__":
    main()
