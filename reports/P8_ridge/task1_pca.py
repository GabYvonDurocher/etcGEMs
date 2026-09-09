#!/usr/bin/env python3
"""P8 TASK 1 -- name the ridge from the chains on disk. Rules: DECISIONS D1 (written first).

Writes task1_variance.csv, task1_loadings.csv, task1_curvature.csv, task1_branch.json and
task1_pca.png beside this file.
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

OUTS = os.path.join(ROOT, "strains", "eciML1515", "outputs")
FOUR = ["topt_scale", "dCp_scale", "sigma", "clearance_mult"]
specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); names = [s.name for s in specs]


def views():
    b = emcee.backends.HDFBackend(os.path.join(OUTS, "calibration_configD_NLDM_recipe_P7_w128", "chain.h5"), read_only=True)
    v = {"128w (P7), steps 250-1500": b.get_chain()[250:]}
    p4 = np.load(os.path.join(OUTS, "calibration_configD_NLDM_recipe_cmax120", "chain.npy"))
    cont = os.path.join(ROOT, "reports", "P6_convergence", "_scratch", "bench_stretch_p10", "chain.npy")
    hist = np.concatenate([p4, np.load(cont)], axis=0) if os.path.exists(cont) else p4
    v[f"40w (P4+P6), steps 1500-{hist.shape[0]}"] = hist[1500:]
    return v


def analyse(tag, ch):
    S, W, D = ch.shape
    X = ch.reshape(-1, D); mu, sd = X.mean(0), X.std(0)
    Z = (X - mu) / sd
    cov = np.cov(Z, rowvar=False)
    evals, evecs = np.linalg.eigh(cov); order = np.argsort(evals)[::-1]; evals, evecs = evals[order], evecs[:, order]
    frac = evals / evals.sum()
    proj = ((ch - mu) / sd) @ evecs                      # (S, W, D) in PC space
    tau = np.array(emcee.autocorr.integrated_time(proj, tol=0), float)
    # sign convention: largest |loading| positive
    for k in range(D):
        j = int(np.argmax(np.abs(evecs[:, k])))
        if evecs[j, k] < 0: evecs[:, k] *= -1; proj[..., k] *= -1
    var_rows = [dict(view=tag, pc=k + 1, variance_fraction=frac[k], cumulative=frac[:k + 1].sum(), tau=tau[k],
                     top_loading=names[int(np.argmax(np.abs(evecs[:, k])))]) for k in range(D)]
    # the ridge (D1): top-tau components until 50 % variance, capped at 3
    by_tau = np.argsort(tau)[::-1]; ridge, cum = [], 0.0
    for k in by_tau:
        ridge.append(int(k)); cum += frac[k]
        if cum >= 0.5 or len(ridge) == 3: break
    clean = (cum >= 0.5) and not ((tau.max() / tau.min() < 1.5) and (frac.max() <= 0.25))
    four_idx = [names.index(n) for n in FOUR]
    share_k = {int(k): float((evecs[four_idx, k] ** 2).sum()) for k in ridge}
    share = float(sum(frac[k] * share_k[k] for k in ridge) / sum(frac[k] for k in ridge))
    load_rows = [dict(view=tag, param=names[i], **{f"PC{k+1}": evecs[i, k] for k in range(min(D, 6))},
                      in_ridge_sq=float(sum(evecs[i, k] ** 2 for k in ridge))) for i in range(D)]
    # curvature: PC2 vs PC1 quadratic
    p1, p2 = proj[..., 0].ravel(), proj[..., 1].ravel()
    A = np.column_stack([np.ones_like(p1), p1, p1 ** 2]); coef, *_ = np.linalg.lstsq(A, p2, rcond=None)
    resid = p2 - A @ coef; s2 = resid @ resid / (len(p2) - 3)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    curv = dict(view=tag, a=coef[0], b=coef[1], c=coef[2], se_c_ols=se[2], se_c_inflated=se[2] * np.sqrt(tau[0]),
                z_inflated=coef[2] / (se[2] * np.sqrt(tau[0])), n_samples=len(p2), tau_pc1=tau[0],
                curved=bool(abs(coef[2]) > 3 * se[2] * np.sqrt(tau[0])))
    print(f"\n[pca] {tag}: {S} steps x {W} walkers")
    print("[pca]   PC  var%  cum%   tau    top loading")
    for r in var_rows[:8]:
        print(f"[pca]   {r['pc']:2d} {100*r['variance_fraction']:5.1f} {100*r['cumulative']:5.1f} {r['tau']:6.1f}  {r['top_loading']}")
    print(f"[pca]   tau range over all 16 PCs: {tau.min():.1f}-{tau.max():.1f}; max var fraction {frac.max():.3f}")
    print(f"[pca]   ridge = PC{[k+1 for k in ridge]} (var {100*cum:.1f} %, tau {[round(float(tau[k]),1) for k in ridge]}); clean direction: {clean}")
    for k in ridge:
        print(f"[pca]   PC{k+1} loadings: " + ", ".join(f"{names[i]} {evecs[i,k]:+.2f}" for i in np.argsort(np.abs(evecs[:, k]))[::-1]))
    print(f"[pca]   the four's share of squared loading on the ridge: {100*share:.1f} %  (per component {[round(100*v,1) for v in share_k.values()]})")
    print(f"[pca]   curvature: c = {coef[2]:+.4f}, SE_ols {se[2]:.4f}, SE_inflated {se[2]*np.sqrt(tau[0]):.4f}, z_inflated {coef[2]/(se[2]*np.sqrt(tau[0])):+.2f} -> {'CURVED' if curv['curved'] else 'not curved (ellipse)'}")
    return var_rows, load_rows, curv, dict(view=tag, ridge_pcs=[k + 1 for k in ridge], ridge_variance=float(cum), clean=bool(clean),
                                           four_share=share, per_component_share={f"PC{k+1}": v for k, v in share_k.items()},
                                           branch=("B (not one clean direction)" if not clean else ("A" if share >= 0.5 else "B"))), proj, evecs


def main():
    V, L, C, B, figs = [], [], [], [], {}
    for tag, ch in views().items():
        v, l, c, b, proj, evecs = analyse(tag, ch); V += v; L += l; C.append(c); B.append(b); figs[tag] = (proj, evecs)
    pd.DataFrame(V).to_csv(os.path.join(HERE, "task1_variance.csv"), index=False)
    pd.DataFrame(L).to_csv(os.path.join(HERE, "task1_loadings.csv"), index=False)
    pd.DataFrame(C).to_csv(os.path.join(HERE, "task1_curvature.csv"), index=False)
    decided = B[0]["branch"]
    json.dump(dict(views=B, deciding_view=B[0]["view"], branch=decided, four=FOUR), open(os.path.join(HERE, "task1_branch.json"), "w"), indent=2)
    print(f"\n[pca] BRANCH (decided by the 128-walker view): {decided}")
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, len(figs), figsize=(6 * len(figs), 9))
        ax = np.atleast_2d(ax).reshape(2, -1)
        for j, (tag, (proj, evecs)) in enumerate(figs.items()):
            p1, p2 = proj[..., 0].ravel(), proj[..., 1].ravel()
            ax[0, j].plot(p1[::7], p2[::7], ",", alpha=0.4); ax[0, j].set_xlabel("PC1"); ax[0, j].set_ylabel("PC2"); ax[0, j].set_title(tag, fontsize=9)
            xs = np.linspace(p1.min(), p1.max(), 100); c = [r for r in C if r["view"] == tag][0]
            ax[0, j].plot(xs, c["a"] + c["b"] * xs + c["c"] * xs ** 2, "r-", lw=1)
            ax[1, j].bar(range(16), evecs[:, 0], label="PC1"); ax[1, j].bar(range(16), evecs[:, 1], alpha=0.5, label="PC2")
            ax[1, j].set_xticks(range(16)); ax[1, j].set_xticklabels(names, rotation=90, fontsize=7); ax[1, j].legend(fontsize=7); ax[1, j].set_ylabel("loading")
        fig.tight_layout(); fig.savefig(os.path.join(HERE, "task1_pca.png"), dpi=110)
    except Exception as e:
        print(f"[pca] figure skipped: {e!r}")
    print("[pca] done")


if __name__ == "__main__":
    main()
