#!/usr/bin/env python3
"""P12 TASK 2 -- local optimisation from the prior, to count the basins.

N starts drawn from the prior through P11's proven transform (seed recorded), plus theta_A,
theta_B, theta_B* and theta_P4 so their basins are in the same set. Powell on the log-posterior
in each worker (optimise_worker.py), 16 processes. Endpoints are then clustered by Pettersen &
Almaas's convention: each parameter standardised by the population sd, pairwise Euclidean
distance, agglomerative SINGLE linkage (their Methods, "Hierarchical clustering"), at a stated
threshold, with stability checked at half and double it.

    python task2_basins.py --n 96 --seed 21
"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import fixed_points, PAYLOAD, SPECS, NAMES, ROOT, NEST                 # noqa: E402
from etcgem.calibration_multi import _gwinit, _set_default_solver                  # noqa: E402
from prior_transform import transform_factory                                      # noqa: E402
from optimise_worker import optimise, MAXFEV, XTOL, FTOL                           # noqa: E402
THRESH = 2.0     # standardised Euclidean distance for single linkage; stability at 1.0 and 4.0


def cluster(X, thresh):
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import pdist
    sd = X.std(axis=0); sd[sd == 0] = 1.0
    Z = (X - X.mean(axis=0)) / sd
    return fcluster(linkage(pdist(Z, metric="euclidean"), method="single"), t=thresh, criterion="distance")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=96); ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--nproc", type=int, default=16); a = ap.parse_args()
    fp = fixed_points()
    s2 = np.load(os.path.join(NEST, "samples_seed2.npy")); l2 = np.load(os.path.join(NEST, "logl_seed2.npy"))
    fp["Bstar"] = s2[int(np.nanargmax(l2))]
    pt = transform_factory(SPECS); rng = np.random.default_rng(a.seed)
    starts = [pt(u) for u in rng.random((a.n, len(SPECS)))]
    named = [("prior", i, x) for i, x in enumerate(starts)] + [(k, -1, v) for k, v in fp.items()]
    print(f"[t2] {len(named)} starts: {a.n} from the prior (seed {a.seed}) + {len(fp)} fixed points; "
          f"Powell maxfev {MAXFEV}, xtol {XTOL}, ftol {FTOL}; {a.nproc} processes", flush=True)
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(a.nproc, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        out = pool.map(optimise, [(i, x) for i, (_, _, x) in enumerate(named)], chunksize=1)
    wall = time.time() - t0
    rows = []
    for (kind, idx, _), r in zip(named, out):
        rows.append(dict(kind=kind, idx=idx, ok=r["ok"], logpost=r["logpost"], logl=r["logl"],
                         nfev=r["nfev"], wall_s=r["wall_s"], **{f"x_{n}": v for n, v in zip(NAMES, r["x"])}))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task2_endpoints.csv"), index=False)
    good = df[df.ok & np.isfinite(df.logpost)].reset_index(drop=True)
    X = good[[f"x_{n}" for n in NAMES]].to_numpy(float)
    lab = {}
    for th in (THRESH / 2, THRESH, THRESH * 2):
        lab[th] = cluster(X, th)
        print(f"[t2] single-linkage threshold {th:.1f}: {len(set(lab[th]))} clusters "
              f"(sizes {sorted(np.bincount(lab[th])[1:], reverse=True)[:8]})", flush=True)
    good["basin"] = lab[THRESH]
    good.to_csv(os.path.join(HERE, "task2_endpoints_clustered.csv"), index=False)
    print(f"\n[t2] basins at threshold {THRESH} ({len(good)} endpoints, {a.n} of them from the prior):", flush=True)
    summ = []
    for b in sorted(set(good.basin)):
        g = good[good.basin == b]; npri = int((g.kind == "prior").sum())
        holds = sorted(set(g.kind) - {"prior"})
        best = g.loc[g.logl.idxmax()]
        summ.append(dict(basin=int(b), n=len(g), n_from_prior=npri, prior_volume_fraction=npri / a.n,
                         best_logl=float(g.logl.max()), best_logpost=float(g.logpost.max()),
                         median_logl=float(g.logl.median()), holds=",".join(holds),
                         **{f"c_{n}": float(g[f"x_{n}"].median()) for n in NAMES}))
        print(f"[t2]   basin {b:2d}: {len(g):3d} endpoints ({npri:3d} from the prior = {100*npri/a.n:5.1f} % of prior volume)  "
              f"best logL {g.logl.max():8.3f}  median logL {g.logl.median():8.3f}  holds: {','.join(holds) or '-'}", flush=True)
    pd.DataFrame(summ).to_csv(os.path.join(HERE, "task2_basins.csv"), index=False)
    json.dump(dict(n_prior_starts=a.n, seed=a.seed, optimiser="Powell", maxfev=MAXFEV, xtol=XTOL, ftol=FTOL,
                   threshold=THRESH, n_clusters={str(k): int(len(set(v))) for k, v in lab.items()},
                   wall_h=round(wall / 3600, 2), n_ok=int(len(good)), n_failed=int((~df.ok).sum())),
              open(os.path.join(HERE, "task2_meta.json"), "w"), indent=1)
    print(f"\n[t2] {len(named)} optimisations in {wall/3600:.2f} h; failures {int((~df.ok).sum())}", flush=True)
    print("[t2] done", flush=True)


if __name__ == "__main__":
    main()
