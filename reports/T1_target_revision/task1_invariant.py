#!/usr/bin/env python3
"""T1 TASK 1 -- PROVE the algebraic invariant of TARGET_REVISION_SPEC item 1.

At every registered audit point (D0): the OLD target (16 sampled coordinates, f_metab sampled) and
the REMOVAL-ONLY target (build_gasflux_specs with remove_inactive=["f_metab"], f_metab absent so
set_allocation receives None and the growth-law branch uses the nominal it equally ignores) must
give the same log L within the registered 1e-6. As a stronger check the OLD target is also
evaluated with f_metab swapped to 0.15 / 0.28 / 0.45 at the same active point: if the sampled
coordinate entered anywhere, one of these would move.

Single process, one solve at a time under a tested SIGALRM (D0 budget: 120 s per log L, 2 h per
batch), incremental CSV so a timeout loses nothing. STOPS on any violation: that would mean
f_metab enters somewhere.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ARCH = os.path.abspath(os.path.join(ROOT, "..", "etcGEMs-p17-archive"))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested"), os.path.join(ROOT, "reports", "P16_reduced"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood, build_gasflux_specs   # noqa: E402
from p6_fits import FITS                                                                                # noqa: E402
from prior_transform import transform_factory                                                           # noqa: E402
from reduced import FULL_SPECS, FREE_SPECS, FIXED_IDX, expand                                           # noqa: E402
from alarm import deadline, Deadline, self_test                                                         # noqa: E402

TOL = 1e-6; SOLVE_S = 120; BATCH_S = 2 * 3600
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
_, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAY = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
           c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
NAMES = [s.name for s in FULL_SPECS]; FM = NAMES.index("f_metab")
OUT = os.path.join(HERE, "task1_invariant.csv")
ONLY_MISSING = "--only-missing" in sys.argv        # batch 2: exactly the labels batch 1 did not reach
if ONLY_MISSING: OUT = os.path.join(HERE, "task1_invariant_batch2.csv")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def audit_points():
    """the D0-registered set, each as a 16-D sampled theta with the saved provenance"""
    pts, prov = [], {}
    pt15 = transform_factory(FREE_SPECS)
    d44 = os.path.join(ROOT, "reports/P17_inactive_prior/real_curvature_probe/evaluations.json")
    prov["d44"] = sha(d44)
    for e in json.load(open(d44)):
        pts.append(("D44:" + e["label"], expand(pt15(np.asarray(e["u"], float))), float(e["logl"])))
    npz = os.path.join(ARCH, "reports/P17_inactive_prior/validated_live_input.npz")
    prov["red2_6800"] = sha(npz)
    assert prov["red2_6800"] == "ef1c50d10a99063a9843289d08078f9fea3781b1654c43a692ad3d1e36357c1e", "red2/6800 npz hash mismatch"
    z = np.load(npz)
    for i in range(z["theta"].shape[0]):
        pts.append((f"red2_6800:{i}", expand(np.asarray(z["theta"][i], float)), float(z["stored_logl"][i])))
    p12 = os.path.join(ROOT, "reports/P12_modes/task2c_converged.csv"); prov["p12"] = sha(p12)
    d = pd.read_csv(p12)
    for _, r in d.iterrows():
        pts.append(("P12:" + r.key, r[[f"x_{n}" for n in NAMES]].to_numpy(float), float(r.logl)))
    # P13's four feasible-non-growing examples are P12 endpoints by key; tag them so the table can show them
    return pts, prov


def main():
    self_test()
    pts, prov = audit_points()
    if ONLY_MISSING:
        done = set(pd.read_csv(os.path.join(HERE, "task1_invariant.csv")).label)
        pts = [p for p in pts if p[0] not in done]
        print(f"[inv] BATCH 2: {len(pts)} labels not reached by batch 1 ({len(done)} done)", flush=True)
    print(f"[inv] {len(pts)} audit points; inputs {prov}", flush=True)
    ctx, specs_old = _build_gasflux_ctx(**PAY)
    _, specs_new = _build_gasflux_ctx(**PAY, spec_options={"remove_inactive": ["f_metab"]})
    assert len(specs_old) == 16 and len(specs_new) == 15 and "f_metab" not in [s.name for s in specs_new]
    rows = []; t0 = time.time(); worst = 0.0
    for k, (label, th, saved) in enumerate(pts):
        if time.time() - t0 > BATCH_S:
            print("[inv] BATCH DEADLINE reached -- stopping, partial results retained", flush=True); break
        row = dict(label=label, saved_logl=saved, f_metab_saved=float(th[FM]))
        try:
            with deadline(SOLVE_S, label):
                row["old"] = float(gasflux_log_likelihood(th, ctx, specs_old))
            for v in (0.15, 0.28, 0.45):
                t2 = th.copy(); t2[FM] = v
                with deadline(SOLVE_S, f"{label} f_metab={v}"):
                    row[f"old_fm_{v}"] = float(gasflux_log_likelihood(t2, ctx, specs_old))
            with deadline(SOLVE_S, label + " removal"):
                row["removal"] = float(gasflux_log_likelihood(np.delete(th, FM), ctx, specs_new))
            vals = [row["old"], row["old_fm_0.15"], row["old_fm_0.28"], row["old_fm_0.45"], row["removal"]]
            row["max_abs_diff"] = float(max(vals) - min(vals)) if all(np.isfinite(vals)) else (0.0 if all(v == -np.inf for v in vals) else float("inf"))
            row["vs_saved"] = float(abs(row["old"] - saved)) if np.isfinite(row["old"]) and np.isfinite(saved) else float("nan")
            row["status"] = "OK" if row["max_abs_diff"] <= TOL else "VIOLATION"
        except Deadline as e:
            row.update(status="UNRESOLVED_TIMEOUT", note=str(e))
        rows.append(row); worst = max(worst, row.get("max_abs_diff", 0.0))
        if k % 25 == 0 or row["status"] != "OK":
            print(f"[inv] {k+1:4d}/{len(pts)} {label:28s} old {row.get('old', float('nan')):10.4f} "
                  f"removal {row.get('removal', float('nan')):10.4f} maxdiff {row.get('max_abs_diff', float('nan')):.2e} {row['status']}", flush=True)
            pd.DataFrame(rows).to_csv(OUT, index=False)
        if row["status"] == "VIOLATION":
            print(f"[inv] *** VIOLATION at {label}: f_metab ENTERS. STOP. ***", flush=True); break
    df = pd.DataFrame(rows); df.to_csv(OUT, index=False)
    summ = dict(n_points=len(pts), n_evaluated=len(df), n_ok=int((df.status == "OK").sum()),
                n_violation=int((df.status == "VIOLATION").sum()),
                n_unresolved=int((df.status == "UNRESOLVED_TIMEOUT").sum()),
                max_abs_diff=float(df.max_abs_diff.max()) if "max_abs_diff" in df else None,
                max_vs_saved=float(df.vs_saved.max()) if "vs_saved" in df else None,
                tolerance=TOL, inputs=prov, wall_min=round((time.time() - t0) / 60, 1))
    json.dump(summ, open(os.path.join(HERE, "task1_invariant_batch2.json" if ONLY_MISSING else "task1_invariant.json"), "w"), indent=1)
    print(f"[inv] SUMMARY {summ}", flush=True)


if __name__ == "__main__":
    main()
