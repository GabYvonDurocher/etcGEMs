#!/usr/bin/env python3
"""T3 TASK 2 -- (a) the 20 highest-importance-weight posterior samples of runs 1 and 2, re-evaluated FRESH (a
new process and model per evaluation), deviation from the stored logl; (b) an order-of-magnitude accumulation
argument from the T3 measurements. No run corrected, recomputed or re-run. FILE with a __main__ guard."""
import os, sys, json, time, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), os.path.join(ROOT, "reports", "T2_validated_posterior"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from t3_battery import _init, _eval
from t2_target import payload
OUT = "strains/eciML1515/outputs/calibration_configD_NLDM_recipe_T2_validated"


def main():
    from multiprocessing import Pool
    out = {}; t0 = time.time()
    with Pool(processes=1, initializer=_init, initargs=(payload(True), "ref"), maxtasksperchild=1) as pool:
        for k, seed in ((1, 17901), (2, 17902)):
            d = f"{OUT}/run{k}_seed{seed}"; s = np.load(f"{d}/samples.npy"); lw = np.load(f"{d}/logwt.npy"); ll = np.load(f"{d}/logl.npy"); lz = np.load(f"{d}/logz.npy")
            w = np.exp(lw - lz[-1]); idx = np.argsort(-w)[:20]
            res = pool.map(_eval, [(f"run{k}:sample{i}", s[i].tolist()) for i in idx], chunksize=1)
            rows = [dict(i=int(i), weight=float(w[i]), stored=float(ll[i]), fresh=float(r["value"]), dev=float(abs(r["value"] - ll[i])), stored_minus_fresh=float(ll[i] - r["value"])) for i, r in zip(idx, res)]
            dv = np.array([r["dev"] for r in rows])
            out[f"run{k}"] = dict(n=20, weight_covered=float(w[idx].sum()), max_dev=float(dv.max()), n_gt_1e9=int((dv > 1e-9).sum()), n_gt_1e6=int((dv > 1e-6).sum()), n_gt_1e3=int((dv > 1e-3).sum()), rows=rows)
            print(f"[t2] run {k}: top-20 weight (covers {w[idx].sum():.3f} of the weight): max |stored - fresh| {dv.max():.3e}; >1e-9: {out[f'run{k}']['n_gt_1e9']}; >1e-6: {out[f'run{k}']['n_gt_1e6']}; >1e-3: {out[f'run{k}']['n_gt_1e3']}", flush=True)
            for r in sorted(rows, key=lambda r: -r["dev"])[:3]: print("    ", {a: b for a, b in r.items()}, flush=True)
    out["wall_min"] = round((time.time() - t0) / 60, 1)
    json.dump(out, open(os.path.join(HERE, "task2_highweight.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
