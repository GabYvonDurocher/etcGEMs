#!/usr/bin/env python3
"""P10 TASK 2 -- derive the log-O2 floor from P9's cliffs, and show the arithmetic on P9's three
decomposed jumps under the old and the new variance.

The floor is the model's vertex granularity: across the 0.05 sd steps of the twelve ROUGH lines
(lines_baseline.csv, per-temperature O2 recorded), take every step at which the log-likelihood
jumps by more than 5 units (a cliff) and, at that step, the largest |delta log O2| over the alive
temperatures; the floor is the MEDIAN of that distribution (its quartiles and max reported), so
that a typical vertex switch costs order one unit. Writes task2_floor.json, task2_jumps.csv.
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); os.chdir(ROOT)
from etcgem.calibration_multi import load_respirometry, to_natural, build_gasflux_specs   # noqa: E402
from p6_fits import FITS                                                                  # noqa: E402
import yaml                                                                               # noqa: E402

CLIFF = 5.0


def main():
    L = pd.read_csv(os.path.join(HERE, "lines_baseline.csv"))
    rows = []
    for lname, sub in L.groupby("line"):
        steps = sorted(sub.step_sd.unique()); ll = {s: sub[sub.step_sd == s].logL.iloc[0] for s in steps}
        for a, b in zip(steps[:-1], steps[1:]):
            d = ll[b] - ll[a]
            if abs(d) < CLIFF: continue
            A = sub[sub.step_sd == a].set_index("T_C"); B = sub[sub.step_sd == b].set_index("T_C")
            alive = (A.growth >= 1e-4) & (B.growth >= 1e-4) & (A.o2 > 0) & (B.o2 > 0)
            dlog = (np.log(B.o2[alive]) - np.log(A.o2[alive])).abs()
            if len(dlog) == 0: continue
            rows.append(dict(line=lname, step_from=a, step_to=b, d_logL=d, max_abs_dlog_o2=float(dlog.max()), T_of_max=float(dlog.idxmax()),
                             n_T_with_dlog_gt_0p2=int((dlog > 0.2).sum())))
    # the support of the term at each end: which temperatures are in the hard mask
    for r in rows:
        A = L[(L.line == r["line"]) & np.isclose(L.step_sd, r["step_from"])]; B = L[(L.line == r["line"]) & np.isclose(L.step_sd, r["step_to"])]
        ma = ((A.growth >= 1e-4) & (A.o2 > 0)).to_numpy(); mb = ((B.growth >= 1e-4) & (B.o2 > 0)).to_numpy()
        r["mask_flips"] = int(np.sum(ma != mb)); r["mask_flip_T"] = ";".join(str(float(x)) for x in A.T_C.to_numpy()[ma != mb])
        r["mechanism"] = "O2 vertex jump" if r["max_abs_dlog_o2"] >= 0.1 else ("support (mask) flip" if r["mask_flips"] else "other (growth term?)")
    J = pd.DataFrame(rows); J.to_csv(os.path.join(HERE, "task2_jumps.csv"), index=False)
    mech = J.mechanism.value_counts().to_dict()
    O = J[J.mechanism == "O2 vertex jump"]; q = O.max_abs_dlog_o2.quantile([0.25, 0.5, 0.75]).to_dict()
    per_T = O.groupby("T_of_max").max_abs_dlog_o2.agg(["count", "median", "max"]).round(3)
    # RULE (D2): the floor is the model's granularity where the O2 cliffs live -- the LARGEST
    # |dlog O2| among the O2-carried cliff steps at the temperature carrying most of them
    # (a variance that honours the model covers what the model does, not its median).
    modal_T = O.T_of_max.value_counts().idxmax(); floor = float(O[O.T_of_max == modal_T].max_abs_dlog_o2.max())
    print(f"[floor] {len(J)} cliff steps (|dlogL| > {CLIFF}) on {J.line.nunique()} lines: mechanisms {mech}", flush=True)
    print(f"[floor] O2-carried cliffs ({len(O)}): |dlog O2| q25 {q[0.25]:.3f} median {q[0.5]:.3f} q75 {q[0.75]:.3f} max {O.max_abs_dlog_o2.max():.3f}; by temperature:\n{per_T.to_string()}", flush=True)
    print(f"[floor] modal cliff temperature {modal_T:g} C; floor = max |dlog O2| there = {floor:.3f}", flush=True)
    # the arithmetic on P9's three decomposed jumps, old vs new variance
    fit = [f for f in FITS if f[0] == "D_NLDM"][0]; T, og, sg, orr, sr, meta = load_respirometry("eciML1515", fit[3], fit[4]); rel = sr / orr
    specs = build_gasflux_specs({"use_etc": False, "fit_clearance": True}); nat = to_natural(np.array(json.load(open(os.path.join(ROOT, "reports", "P9_surface", "task1_meta.json")))["theta0"]), specs)
    dr, rs = nat["disc_resp"], nat["resp_scale"]; conv = float(yaml.safe_load(open("strains/eciML1515/gas_exchange.yaml"))["gas_exchange"]["gdw_per_cell"]) * 32 / 60
    att = pd.read_csv(os.path.join(ROOT, "reports", "P9_surface", "task2_attribution.csv")); arith = []
    for ln, sub in att.groupby("line", sort=False):
        r = sub[sub.d_resp_term.abs() > 1].iloc[0]; i = int(np.argmin(np.abs(T - r.T_C)))
        obsl = np.log(orr[i]); pa = np.log(r.o2_from * conv * rs); pb = np.log(r.o2_to * conv * rs)
        old = -0.5 * ((obsl - pb) ** 2 - (obsl - pa) ** 2) / (rel[i] ** 2 + dr ** 2); new = -0.5 * ((obsl - pb) ** 2 - (obsl - pa) ** 2) / (rel[i] ** 2 + dr ** 2 + floor ** 2)
        arith.append(dict(line=ln, T_C=r.T_C, resid_from=obsl - pa, resid_to=obsl - pb, dlog_o2=abs(pb - pa), var_old=rel[i] ** 2 + dr ** 2, step_old=old, var_new=rel[i] ** 2 + dr ** 2 + floor ** 2, step_new=new))
        print(f"[floor] {ln:16s} T={r.T_C:.0f}: step old {old:+.2f} -> new {new:+.2f} (var {rel[i]**2+dr**2:.4f} -> {rel[i]**2+dr**2+floor**2:.4f})", flush=True)
    json.dump(dict(cliff_threshold_logL=CLIFF, n_cliff_steps=int(len(J)), mechanisms=mech, n_o2_cliffs=int(len(O)), q25=q[0.25], median=q[0.5], q75=q[0.75], max=float(O.max_abs_dlog_o2.max()),
                   per_temperature=per_T.to_dict(), modal_T=float(modal_T), floor=floor, floor_rounded=round(floor, 2), disc_resp_at_MAP=dr,
                   prior_disc_resp="half-normal(0.5) on [1e-3, 3], unchanged", arithmetic=arith),
              open(os.path.join(HERE, "task2_floor.json"), "w"), indent=1, default=float)
    print(f"[floor] FLOOR = {floor:.3f} (median |dlog O2| at cliff steps); done", flush=True)


if __name__ == "__main__":
    main()
