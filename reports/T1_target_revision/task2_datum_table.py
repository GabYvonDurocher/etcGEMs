#!/usr/bin/env python3
"""T1 TASK 2 (second part) -- the DATUM-BY-DATUM TABLE the spec requires, under the current
omission and under each candidate observation model, reconciled to the total log L at every
registered point. Nothing is chosen; nothing is implemented as production; no posterior is read.

Candidates for a temperature whose prediction is missing, each derived from the MEASUREMENT:
  OMISSION  -- the current code: contribution 0 (the term is skipped).          [what exists]
  NORMAL_r0 -- y ~ Normal(r, s^2) on the ORIGINAL scale (mg O2 cell^-1 min^-1) with s the MEASURED
               replicate SD at that (medium, T), and r = 0 only where the classification is
               STRUCTURAL_ZERO on growth. Contribution -0.5*((y/s)^2 + log(2*pi*s^2)).
               The data say a non-growing cell still respires (50 C: r=1e-6 series respire at
               ~2e-12), so r=0 is NOT justified by the data for O2; the candidate is tabulated
               because the spec asks for it, with that caveat printed beside every row.
  LOGSCALE  -- the honest statement of what the EXISTING term implies if a prediction of 0 were
               scored on its own scale: log(0) = -inf, i.e. the log-scale term CANNOT score a
               zero prediction at all. A lognormal epsilon is NOT derivable from the code's use
               of a log scale (the spec's warning); so this row is reported as UNDEFINED, not
               invented.
  CENSORED  -- NOT DERIVABLE: no detection limit is documented anywhere in the respirometry record
               (README, tables, P3 gate). Reported as such.
For UNRESOLVED solves every candidate's contribution is UNDEFINED PENDING RESOLUTION, never a number.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ARCH = os.path.abspath(os.path.join(ROOT, "..", "etcGEMs-p17-archive"))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested"), os.path.join(ROOT, "reports", "P16_reduced"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, to_pert, to_natural, gasflux_log_likelihood, _MASK_G   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                                                 # noqa: E402
from etcgem import providers as _prov                                                                             # noqa: E402
from p6_fits import FITS                                                                                          # noqa: E402
from prior_transform import transform_factory                                                                     # noqa: E402
from reduced import FULL_SPECS, FREE_SPECS, expand                                                                # noqa: E402
from alarm import deadline, Deadline, self_test                                                                   # noqa: E402

FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
_, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAY = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
           c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
NAMES = [s.name for s in FULL_SPECS]
FEASIBLE_NONGROWING = ["A(b20)", "Bstar(b8)", "p81(b7)", "worst(b5)"]     # P13 addendum 1
GROWING = ["p38(b22)", "p50(b19)"]


def points():
    pt15 = transform_factory(FREE_SPECS); pts = []
    e = json.load(open("reports/P17_inactive_prior/real_curvature_probe/evaluations.json"))
    b = [x for x in e if x["label"] == "baseline_start"][0]
    pts.append(("D44:baseline_start", expand(pt15(np.asarray(b["u"], float)))))
    for st in json.load(open("reports/P17_inactive_prior/stratum_probe.json")):
        pts.append((f"stratum:{st['tag']}:{st['stored_index']}", expand(pt15(np.asarray(st["start"], float)))))
    d = pd.read_csv("reports/P12_modes/task2c_converged.csv")
    for k in FEASIBLE_NONGROWING + GROWING:
        r = d[d.key == k].iloc[0]; pts.append(("P12:" + k, r[[f"x_{n}" for n in NAMES]].to_numpy(float)))
    return pts


def main():
    self_test()
    cls = {}
    cp = os.path.join(HERE, "task2_classify_all.csv")                      # the audited merge of both batches
    if not os.path.exists(cp): cp = os.path.join(HERE, "task2_classify.csv")
    if os.path.exists(cp):
        for _, r in pd.read_csv(cp).iterrows():
            cls[r.label] = (str(r.get("rung1", "")).split(";"), str(r.get("classes", "")).split(";") if isinstance(r.get("classes"), str) else [],
                            str(r.get("nonoptimal_T", "")).split(";") if isinstance(r.get("nonoptimal_T"), str) else [])
    rows = []; totals = []
    for label, th in points():
        ctx, sp = _build_gasflux_ctx(**PAY); resp = ctx.get("respiration") or {}
        nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]
        if "clearance_mult" in nat:
            rr = ctx["recipe"]; _prov.set_medium_recipe(pm, rr["recipe_csv"], clearance_L_per_gDW_h=rr["clearance"] * float(nat["clearance_mult"]), uptake_ub=rr.get("uptake_ub", 1000.0), verbose=False)
            if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
        with deadline(300, label):
            df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")),
                          growth_tol=float(resp.get("growth_tol", 1e-6)), tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
            ll = float(gasflux_log_likelihood(th, ctx, sp))
        g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float); st = list(map(str, df["status"]))
        y = np.asarray(ctx["resp_obs"], float); s_ = np.asarray(ctx["resp_sd"], float); T = np.asarray(ctx["T"], float)
        dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
        gterm = -0.5 * ((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var))
        keep = np.isfinite(o2) & (o2 > 0) if str(resp.get("support")) == "clamp" else ((g >= _MASK_G) & (o2 > 0))
        dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"]); floor = float(resp.get("log_o2_floor", 0.0))
        gs = resp.get("alive_soft_growth"); wf = float(resp.get("weight_floor", 1.0))
        rterm_old = np.zeros_like(g); pred_cell = np.full_like(g, np.nan)
        for i in range(len(g)):
            if keep[i]:
                pred_cell[i] = o2[i] * ctx["o2_conv"] * rs
                varr = (s_[i] / y[i]) ** 2 + dr ** 2 + floor ** 2
                w = max(min(1.0, g[i] / float(gs)), wf) if gs else 1.0
                rterm_old[i] = -0.5 * w * ((np.log(y[i]) - np.log(pred_cell[i])) ** 2 / varr + np.log(2 * np.pi * varr))
        tot_old = float(gterm.sum() + rterm_old.sum()); recon = abs(tot_old - ll) < 1e-9
        # solver classification per temperature: from task2_classify if present, else from status here
        r1, cl, badT = cls.get(label, (st, [], []))
        classification = []
        for i in range(len(g)):
            if st[i] == "optimal": classification.append("OPTIMAL")
            elif badT and str(i) in badT: classification.append(cl[badT.index(str(i))])
            else: classification.append("infeasible_1st_solve(unclassified)" if st[i] == "infeasible" else f"nonoptimal:{st[i]}")
        new_normal = np.zeros_like(g); new_defined = np.ones(len(g), bool)
        for i in range(len(g)):
            if keep[i]:
                new_normal[i] = rterm_old[i]                       # scored temperatures unchanged under a missing-state-only revision
            elif classification[i] == "STRUCTURAL_ZERO":
                new_normal[i] = -0.5 * ((y[i] / s_[i]) ** 2 + np.log(2 * np.pi * s_[i] ** 2))
            else:
                new_normal[i] = np.nan; new_defined[i] = False     # UNRESOLVED / unclassified -> undefined pending resolution
            rows.append(dict(point=label, T=T[i], y_mg_cell_min=y[i], s_replicate=s_[i], y_over_s=y[i] / s_[i],
                             detection_status="no documented limit; y>0", solver_status_1st=st[i], classification=classification[i],
                             growth=g[i], o2_model=o2[i], pred_cell=pred_cell[i], scored_old=int(keep[i]),
                             growth_term=gterm[i], resp_old=rterm_old[i],
                             resp_NORMAL_r0=new_normal[i], resp_LOGSCALE=(rterm_old[i] if keep[i] else float("-inf")),
                             resp_CENSORED="NOT DERIVABLE (no documented detection limit)",
                             escapes_scoring_old=int((not keep[i]) and y[i] > 0),
                             escapes_scoring_NORMAL=int((not keep[i]) and y[i] > 0 and new_defined[i] and np.isnan(new_normal[i]))))
        totals.append(dict(point=label, logl_code=ll, sum_growth=float(gterm.sum()), sum_resp_old=float(rterm_old.sum()),
                           total_old=tot_old, reconciles=bool(recon), n_missing=int((~keep).sum()),
                           n_positive_measurements_unscored_OLD=int(((~keep) & (y > 0)).sum()),
                           total_NORMAL_r0=(float(gterm.sum() + np.nansum(new_normal)) if new_defined.all() else None),
                           NORMAL_defined=bool(new_defined.all()),
                           n_unresolved_or_unclassified=int(sum(1 for c in classification if c not in ("OPTIMAL", "STRUCTURAL_ZERO"))),
                           peak_growth=float(np.nanmax(g))))
        print(f"[tbl] {label:28s} logL {ll:10.4f} = growth {gterm.sum():9.4f} + resp {rterm_old.sum():9.4f} reconciles={recon} "
              f"missing={int((~keep).sum())} unscored+ve={totals[-1]['n_positive_measurements_unscored_OLD']} "
              f"NORMAL_total={totals[-1]['total_NORMAL_r0']}", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "task2_datum_table.csv"), index=False)
    pd.DataFrame(totals).to_csv(os.path.join(HERE, "task2_datum_totals.csv"), index=False)
    print("[tbl] done", flush=True)


if __name__ == "__main__":
    main()
