#!/usr/bin/env python3
"""T2 TASK 5 -- judge the five runs against docs/VALIDATION_PROTOCOL.md (frozen). Every statistic from
saved arrays; the driver's audit verdicts are re-derived here, not trusted. Writes task5_checks.json,
task5_marginals.csv, task5_eigen.csv, task5_predictive.csv and prints PASS/FAIL per check per run.
Predictive draws (check e) are FRESH evaluations under the registered ladder in a 16-process pool; this
file has a __main__ guard (OPEN_ITEMS section 4). Development seed for the predictive resampling: 17306."""
import os, sys, json, time, hashlib, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from scipy.stats import truncnorm
from t2_target import build, Target, payload            # noqa: E402
from t2_prior import transform_factory                  # noqa: E402
from run_protocol import audit_run, integrate           # noqa: E402  (the driver's independent reconstruction, re-run here)
from etcgem import calibration_multi as CM              # noqa: E402
from etcgem.calibration_multi import _gwinit, _set_default_solver, to_pert, to_natural   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint, UnresolvedSolve   # noqa: E402
from etcgem import providers as _prov                   # noqa: E402
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_T2_validated")
SEEDS = [17901, 17902, 17903, 17904, 17905]; PEAK_OBS = 2.0761
TH = dict(a_dist=0.05, a_mean=0.05, b_correct=0.05, b_wrong=0.30, c_mc=2.0, c_cos=0.9, c_width=0.1, d_se=2.0, e_unres=0.01, e_cover=10, f_logz=1e-9, f_w=1e-12, f_cube=1e-14)


def ecdf_dist(x, w):
    ii = np.argsort(x); xs = x[ii]; cs = np.cumsum(w[ii]); return float(max(np.max(cs - xs), np.max(xs - (cs - w[ii]))))


def wq(x, w, q):
    ii = np.argsort(x); cs = np.cumsum(w[ii]); return float(x[ii][np.searchsorted(cs, q * cs[-1])])


def load_run(k, seed):
    d = os.path.join(OUT, f"run{k}_seed{seed}")
    a = {n: np.load(os.path.join(d, f"{n}.npy")) for n in ("samples", "samples_u", "logwt", "logl", "logz", "logzerr")}
    a["summary"] = json.load(open(os.path.join(d, "summary.json"))); a["dir"] = d
    a["rejection"] = json.load(open(os.path.join(d, "rejection.json"))) if os.path.exists(os.path.join(d, "rejection.json")) else None
    w = np.exp(a["logwt"] - a["logz"][-1]); a["w"] = w / w.sum(); return a


_TG = None


def _predict(th_s):
    global _TG
    if _TG is None: _TG = Target(CM._GSPECS)
    th = _TG.expand(np.asarray(th_s, float)); ctx, specs = CM._GCTX, CM._GSPECS; resp = ctx["respiration"]
    nat = to_natural(th, specs); pert = to_pert(th, specs); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
    try:
        df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")), growth_tol=float(resp.get("growth_tol", 1e-6)),
                      tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)), stop_on_infeasible=False, retry_ladder=True)
    except UnresolvedSolve as e:
        return dict(unresolved=12, msg=str(e))
    g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float); st = list(map(str, df["status"]))
    resp_pred = o2 * ctx["o2_conv"] * float(nat["resp_scale"])
    return dict(unresolved=0, growth=g.tolist(), resp=resp_pred.tolist(), status=st, scored=(np.isfinite(o2) & (o2 > 0)).astype(int).tolist(), infeasible=int(sum(s == "infeasible" for s in st)))


def main():
    t0 = time.time(); ctx, specs = build(validation=True); tg = Target(specs); pt = transform_factory(tg.sampled)
    phys = [i for i, n in enumerate(tg.names) if not n.endswith("_diag")]; i_fm = tg.names.index("f_metab_diag"); i_b = tg.names.index("beta31_diag")
    T = np.asarray(ctx["T"], float); gobs = np.asarray(ctx["growth_obs"], float); robs = np.asarray(ctx["resp_obs"], float)
    ref = json.load(open(os.path.join(HERE, "task2_rejection.json")))
    runs = [load_run(k, s) for k, s in enumerate(SEEDS, start=1)]
    checks = {}; marg = []; eig = []; pred_rows = []
    # ---- (f) re-derived audits + logZ agreement ----
    for k, a in enumerate(runs, start=1):
        ok, rep = audit_run(a["dir"], pt, False); json.dump(rep, open(os.path.join(HERE, f"task5_audit_run{k}.json"), "w"), indent=1)
        checks[f"f:run{k}:audit"] = dict(PASS=bool(ok), logz_err=rep["logz_abs_err"], weights=rep["weight_sum_minus_1"], cube=rep["cube_inverse_max_err"], failed=[c for c, v in rep["checks"].items() if not v])
    for i in range(5):
        for j in range(i + 1, 5):
            dz = abs(runs[i]["logz"][-1] - runs[j]["logz"][-1]); ce = float(np.hypot(runs[i]["logzerr"][-1], runs[j]["logzerr"][-1]))
            checks[f"f:logz:{i+1}v{j+1}"] = dict(PASS=bool(dz <= ce), dz=float(dz), combined_err=ce)
    # ---- (a), (b) ----
    for k, a in enumerate(runs, start=1):
        s, w = a["samples"], a["w"]
        u_fm = truncnorm.cdf(s[:, i_fm], (0.15 - 0.28) / 0.03, (0.45 - 0.28) / 0.03, loc=0.28, scale=0.03)
        da = ecdf_dist(u_fm, w); ma = float(np.sum(w * u_fm))
        checks[f"a:run{k}"] = dict(PASS=bool(da <= TH["a_dist"] and abs(ma - 0.5) <= TH["a_mean"]), cdf_distance=da, cdf_mean=ma)
        b = s[:, i_b]; dc = ecdf_dist(b ** 3, w); dw = ecdf_dist(b, w)
        checks[f"b:run{k}"] = dict(PASS=bool(dc <= TH["b_correct"] and dw >= TH["b_wrong"]), correct_b3_distance=dc, wrong_uniform_distance=dw)
    # ---- (c) medians + MC errors; eigendecomposition in the unit cube (physical coords) ----
    rng = np.random.default_rng(0); med = {}; mc = {}; V = {}; width = {}
    for k, a in enumerate(runs, start=1):
        s, w, u = a["samples"], a["w"], a["samples_u"]
        idx = rng.choice(len(s), size=(200, len(s)), p=w); mc[k] = np.std(np.median(s[idx], axis=1), axis=0); med[k] = np.array([wq(s[:, j], w, .5) for j in range(s.shape[1])])
        up = u[:, phys]; mu = w @ up; X = up - mu; C = np.einsum("ni,n,nj->ij", X, w, X) / (1 - np.sum(w * w)); ev, Vk = np.linalg.eigh(C); order = np.argsort(-ev); ev, Vk = ev[order], Vk[:, order]
        for c in range(Vk.shape[1]):
            if Vk[np.argmax(np.abs(Vk[:, c])), c] < 0: Vk[:, c] *= -1
        V[k] = Vk; width[k] = np.sqrt(12 * ev)
        for c in range(len(ev)):
            row = dict(run=k, direction=c + 1, eigenvalue=float(ev[c]), width_ratio=float(width[k][c])); row.update({tg.names[phys[j]]: float(Vk[j, c]) for j in range(len(phys))}); eig.append(row)
        for j in phys:
            sp = tg.sampled[j]; nat = s[:, j] if sp.space == "add" else np.exp(s[:, j]) * (sp.emergent if getattr(sp, "emergent", None) is not None else 1.0)
            marg.append(dict(run=k, parameter=sp.name, lo5=wq(nat, w, .05), median=wq(nat, w, .5), hi95=wq(nat, w, .95), median_sampled=float(med[k][j]), mc_sampled=float(mc[k][j])))
    c_med = []; c_cos = []; c_w = []
    for i in range(1, 6):
        for j in range(i + 1, 6):
            for p in phys:
                err = float(np.hypot(mc[i][p], mc[j][p])); diff = float(abs(med[i][p] - med[j][p])); c_med.append(dict(pair=f"{i}v{j}", parameter=tg.names[p], diff=diff, err=err, mc=(diff / err if err > 0 else float("inf")), ok=bool(diff <= TH["c_mc"] * err)))
            for c in range(3):
                cos = float(abs(V[i][:, c] @ V[j][:, c])); c_cos.append(dict(pair=f"{i}v{j}", direction=c + 1, abs_cos=cos, ok=bool(cos >= TH["c_cos"])))
            for c in range(len(phys)):
                d = float(abs(width[i][c] - width[j][c])); c_w.append(dict(pair=f"{i}v{j}", direction=c + 1, width_diff=d, ok=bool(d <= TH["c_width"])))
    checks["c:medians"] = dict(PASS=bool(all(r["ok"] for r in c_med)), n_fail=int(sum(not r["ok"] for r in c_med)), worst=max(c_med, key=lambda r: r["mc"]))
    checks["c:eigenvectors"] = dict(PASS=bool(all(r["ok"] for r in c_cos)), n_fail=int(sum(not r["ok"] for r in c_cos)), min_abs_cos=min(r["abs_cos"] for r in c_cos))
    checks["c:widths"] = dict(PASS=bool(all(r["ok"] for r in c_w)), n_fail=int(sum(not r["ok"] for r in c_w)), max_width_diff=max(r["width_diff"] for r in c_w))
    pd.DataFrame(c_med).to_csv(os.path.join(HERE, "task5_c_medians.csv"), index=False); pd.DataFrame(c_cos + c_w).to_csv(os.path.join(HERE, "task5_c_directions.csv"), index=False)
    # ---- (d) amended: prior rejection per run vs TASK 2's reference; infeasible posterior mass 0 ----
    p0, n0 = ref["fraction"], ref["n_evaluated"]
    for k, a in enumerate(runs, start=1):
        r = a["rejection"]; p1, n1 = r["fraction"], r["n_evaluated"]; pp = (p0 * n0 + p1 * n1) / (n0 + n1); se = float(np.sqrt(pp * (1 - pp) * (1 / n0 + 1 / n1)))
        finite = np.isfinite(a["logl"]) & (a["logl"] > -1e299); n_inf_w = int(np.sum((~finite) & (a["w"] > 0)))
        checks[f"d:run{k}"] = dict(PASS=bool(abs(p1 - p0) <= TH["d_se"] * se and n_inf_w == 0), run_fraction=p1, reference_fraction=p0, diff=float(p1 - p0), se_diff=se, infeasible_with_weight=n_inf_w, first_T=r["first_infeasible_T_counts"])
    # ---- (e) fresh feasibility-aware predictive checks: 500 weighted draws per run ----
    from multiprocessing import Pool
    solver = _set_default_solver("gurobi"); rng_e = np.random.default_rng(17306); living = {}
    with Pool(16, initializer=_gwinit, initargs=(dict(payload(True), solver=solver),)) as pool:
        for k, a in enumerate(runs, start=1):
            idx = rng_e.choice(len(a["samples"]), size=500, p=a["w"]); draws = [a["samples"][i] for i in idx]
            out = pool.map(_predict, draws, chunksize=4)
            unres = sum(o["unresolved"] for o in out); okd = [o for o in out if not o["unresolved"]]
            G = np.array([o["growth"] for o in okd]); R = np.array([o["resp"] for o in okd]); Sc = np.array([o["scored"] for o in okd])
            n_infe = int(sum(o["infeasible"] for o in okd)); unscored_pos = int(np.sum(Sc == 0))
            lo_g, hi_g = np.percentile(G, [2.5, 97.5], axis=0); lo_r, hi_r = np.percentile(R, [2.5, 97.5], axis=0)
            cov_g = int(np.sum((gobs >= lo_g) & (gobs <= hi_g))); cov_r = int(np.sum((robs >= lo_r) & (robs <= hi_r)))
            living[k] = float(np.mean(np.nanmax(G, axis=1) >= 0.5 * PEAK_OBS))
            for t in range(len(T)):
                pred_rows.append(dict(run=k, T=T[t], growth_obs=gobs[t], growth_lo=lo_g[t], growth_med=float(np.median(G[:, t])), growth_hi=hi_g[t], resp_obs=robs[t], resp_lo=lo_r[t], resp_med=float(np.median(R[:, t])), resp_hi=hi_r[t], growth_in=bool(lo_g[t] <= gobs[t] <= hi_g[t]), resp_in=bool(lo_r[t] <= robs[t] <= hi_r[t])))
            rate = unres / (500 * 12)
            checks[f"e:run{k}"] = dict(PASS=bool(rate <= TH["e_unres"] and cov_g >= TH["e_cover"] and cov_r >= TH["e_cover"] and unscored_pos == 0), unresolved_rate=rate, coverage_growth=cov_g, coverage_resp=cov_r, unscored_positive=unscored_pos, infeasible_temps_in_draws=n_infe, living_fraction=living[k])
            print(f"[e] run {k}: unresolved {unres} draws, coverage growth {cov_g}/12 resp {cov_r}/12, unscored {unscored_pos}, living {living[k]:.3f}", flush=True)
    pd.DataFrame(marg).to_csv(os.path.join(HERE, "task5_marginals.csv"), index=False); pd.DataFrame(eig).to_csv(os.path.join(HERE, "task5_eigen.csv"), index=False); pd.DataFrame(pred_rows).to_csv(os.path.join(HERE, "task5_predictive.csv"), index=False)
    allpass = all(v["PASS"] for v in checks.values()); verdict = "R1 CLOSED" if allpass else "R1 OPEN"
    summ = dict(verdict=verdict, all_pass=allpass, thresholds=TH, checks=checks, failed=[k for k, v in checks.items() if not v["PASS"]], living_fraction=living,
                runs={k: dict(seed=a["summary"]["seed"], iters=a["summary"]["iters"], ncall=a["summary"]["ncall"], unit_cube_ncall=a["summary"]["unit_cube_ncall"], wall_h=a["summary"]["wall_h"], logz=a["summary"]["logz"], logzerr=a["summary"]["logzerr"], n_eff=a["summary"]["n_eff"]) for k, a in enumerate(runs, start=1)},
                wall_min=round((time.time() - t0) / 60, 1))
    if allpass:
        # the posterior as the protocol prescribes: MAP, pooled weighted marginals (never the componentwise median as a point), eigen-directions labelled
        best = max(runs, key=lambda a: float(np.max(a["logl"]))); i = int(np.argmax(best["logl"])); summ["MAP"] = dict(run_seed=best["summary"]["seed"], logl=float(best["logl"][i]), theta_sampled=best["samples"][i].tolist(), names=tg.names)
    json.dump(summ, open(os.path.join(HERE, "task5_checks.json"), "w"), indent=1, default=float)
    for k, v in checks.items(): print(f"[judge] {k:22s} {'PASS' if v['PASS'] else 'FAIL'}  {json.dumps({a: b for a, b in v.items() if a != 'PASS'}, default=float)[:160]}")
    print("[judge] VERDICT", verdict, "| failed:", summ["failed"])


if __name__ == "__main__":
    main()
