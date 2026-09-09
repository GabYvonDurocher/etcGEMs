#!/usr/bin/env python3
"""P6 addendum 6 -- why does tau track chain length? Diagnosis from chains on disk; nothing fitted.

Chains: P4's committed configuration-D NLDM chain (2000 x 40 x 16, emergent-point init) and the
two 500-step TASK 0b chains that continue from its final ensemble state with the same stretch
move (bench_stretch_p10) and with DE moves (bench_DE_p10). P4 + stretch continuation are
concatenated (2500 steps) as the longest single-history chain available.

  1. tau PER PARAMETER (emcee integrated_time, tol=0), sorted, with the gap to the next;
     also tau_max as a function of chain length (250-step prefixes) to show the linear growth.
  2. For the top parameter: per-walker means over the first and last quarter; the ensemble
     median per 250-step block; the ensemble spread per block. Drift vs excursions.
  3. Whether it is K (clearance_mult).
  4. Posterior / prior width ratio for EVERY parameter on the last half of the chain.

Writes diffusion_tau.csv, diffusion_walkers.csv, diffusion_widths.csv beside this file.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, HERE)
os.chdir(ROOT)
import emcee                                                                # noqa: E402
from etcgem.calibration_multi import build_gasflux_specs, to_natural         # noqa: E402

P4 = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_cmax120", "chain.npy")
B1 = os.path.join(HERE, "_scratch", "bench_stretch_p10", "chain.npy")
B2 = os.path.join(HERE, "_scratch", "bench_DE_p10", "chain.npy")
specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True})
names = [s.name for s in specs]


def natural(ch):
    out = np.empty_like(ch)
    for k, s in enumerate(specs):
        out[..., k] = np.exp(ch[..., k]) if s.space == "log" else ch[..., k]
    return out


def tau_per_param(ch):
    return np.array(emcee.autocorr.integrated_time(ch, tol=0), float)


def main():
    p4 = np.load(P4)
    chains = {"P4 (2000)": p4}
    if os.path.exists(B1):
        chains["P4 + stretch continuation (2500)"] = np.concatenate([p4, np.load(B1)], axis=0)
    if os.path.exists(B2):
        chains["DE continuation only (500)"] = np.load(B2)
    rows = []
    for cname, ch in chains.items():
        tau = tau_per_param(ch)
        order = np.argsort(tau)[::-1]
        print(f"\n[diff] {cname}: tau per parameter (sampled space), sorted:", flush=True)
        for r, k in enumerate(order):
            gap = (tau[k] / tau[order[r + 1]]) if r + 1 < len(order) else np.nan
            rows.append(dict(chain=cname, rank=r + 1, param=names[k], tau=round(float(tau[k]), 1),
                             ratio_to_next=round(float(gap), 2) if np.isfinite(gap) else ""))
            print(f"[diff]   {r+1:2d}. {names[k]:16s} tau {tau[k]:7.1f}" + (f"   x{gap:.2f} the next" if np.isfinite(gap) else ""), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "diffusion_tau.csv"), index=False)

    # tau_max vs chain length on the longest chain
    ch = chains[max(chains, key=lambda k: chains[k].shape[0])]
    print(f"\n[diff] tau_max vs chain length ({ch.shape[0]} steps):", flush=True)
    for n in range(250, ch.shape[0] + 1, 250):
        t = tau_per_param(ch[:n]); k = int(np.argmax(t))
        print(f"[diff]   {n:5d} steps: tau_max {t[k]:6.1f} ({names[k]}), chain/tau {n / t[k]:.1f}", flush=True)

    # the top parameter: drift vs excursions
    tau = tau_per_param(ch); k = int(np.argmax(tau)); top = names[k]
    nat = natural(ch)
    q = ch.shape[0] // 4
    first, last = nat[:q, :, k].mean(axis=0), nat[-q:, :, k].mean(axis=0)
    wrows = [dict(walker=w, first_quarter_mean=first[w], last_quarter_mean=last[w], shift=last[w] - first[w]) for w in range(ch.shape[1])]
    pd.DataFrame(wrows).to_csv(os.path.join(HERE, "diffusion_walkers.csv"), index=False)
    print(f"\n[diff] top parameter {top}: per-walker means, first quarter {first.mean():.4f} (sd across walkers {first.std():.4f}) "
          f"-> last quarter {last.mean():.4f} (sd {last.std():.4f}); walkers moving up {int((last > first).sum())} of {ch.shape[1]}, "
          f"mean |shift| {np.abs(last - first).mean():.4f}", flush=True)
    print(f"[diff] {top}: ensemble median / 5-95% per 250-step block:", flush=True)
    for b in range(0, ch.shape[0], 250):
        blk = nat[b:b + 250, :, k].ravel()
        print(f"[diff]   steps {b:5d}-{b+250:5d}: median {np.median(blk):.4f}  5-95% [{np.percentile(blk, 5):.4f}, {np.percentile(blk, 95):.4f}]", flush=True)
    # second-ranked parameter too, briefly
    k2 = int(np.argsort(tau)[-2]); print(f"[diff] second-ranked {names[k2]}: ensemble median per block:", flush=True)
    for b in range(0, ch.shape[0], 500):
        blk = nat[b:b + 500, :, k2].ravel(); print(f"[diff]   steps {b:5d}-{b+500:5d}: median {np.median(blk):.4f}  5-95% [{np.percentile(blk, 5):.4f}, {np.percentile(blk, 95):.4f}]", flush=True)

    # posterior / prior width ratio for every parameter, last half
    half = nat[ch.shape[0] // 2:].reshape(-1, ch.shape[2])
    wr = []
    print(f"\n[diff] posterior (5-95%, last half of {ch.shape[0]} steps) / prior width, every parameter:", flush=True)
    for j, s in enumerate(specs):
        lo, md, hi = np.percentile(half[:, j], [5, 50, 95])
        ratio = (hi - lo) / (s.hi - s.lo)
        wr.append(dict(param=s.name, tau=round(float(tau[j]), 1), median=md, ci90_lo=lo, ci90_hi=hi, prior_lo=s.lo, prior_hi=s.hi,
                       width_ratio_vs_prior=ratio, prior_determined=ratio > 0.5))
        print(f"[diff]   {s.name:16s} tau {tau[j]:6.1f}  median {md:8.3f}  90% [{lo:8.3f}, {hi:8.3f}]  prior [{s.lo:g}, {s.hi:g}]  width ratio {ratio:.2f}"
              + ("   <- PRIOR-DETERMINED" if ratio > 0.5 else ""), flush=True)
    pd.DataFrame(wr).to_csv(os.path.join(HERE, "diffusion_widths.csv"), index=False)
    print("[diff] done", flush=True)


if __name__ == "__main__":
    main()
