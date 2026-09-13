#!/usr/bin/env python3
"""T1 TASK 3 -- trace the seven curvature-sensitive axes. TRACE ONLY: new log L == old log L at
every point by construction; nothing is smoothed, no value changes.

At D44's saved parent and its 56 stencils first, then at the five diverse points registered in
D1 (p38, P4's MAP, the red2/6800 living median, the highest-weight and weighted-median-log-L
living samples of P16's red2 posterior), for each of dTopt, topt_scale, dCp_scale, tm_scale,
kcat_scale, sigma, clearance_mult at offsets +/-0.02 and +/-0.04 group SD (D44's saved `scale`),
capture and save per evaluation:
  * every observation's individual growth-term and respiration-term contribution (the exact
    arithmetic of gasflux_log_likelihood, reproduced datum by datum and reconciled to the total);
  * the enzyme thermal-response state at every temperature: counts of enzymes above their
    effective Topt, past their (shifted) Tm, and CLIPPED at the 1e-6 floor of
    np.clip(rk*fN, 1e-6, 1e6) -- the candidate mechanism registered in D1;
  * the LP status per temperature and whether the solve was fresh (always fresh here);
  * sha256 of the input theta and of the output row.
Then P14's refinement instrument on each axis's larger-step side (h, h/2, h/4) and a decomposition
of each axis's curvature difference by observation and by mechanism. Single process, alarm per
evaluation (D0: 300 s), one job at a time, incremental JSON.
"""
import os, sys, json, time, hashlib
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ARCH = os.path.abspath(os.path.join(ROOT, "..", "etcGEMs-p17-archive"))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested"), os.path.join(ROOT, "reports", "P16_reduced"),
          os.path.join(ROOT, "reports", "P13_support"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import _build_gasflux_ctx, to_pert, to_natural, gasflux_log_likelihood, _MASK_G   # noqa: E402
from etcgem.gasflux import flux_tpc, add_total_carbon_constraint                                                 # noqa: E402
from etcgem import providers as _prov, unfolding as U                                                             # noqa: E402
from p6_fits import FITS                                                                                          # noqa: E402
from prior_transform import transform_factory                                                                     # noqa: E402
from reduced import FULL_SPECS, FREE_SPECS, FIXED_IDX, expand                                                     # noqa: E402
from alarm import deadline, Deadline, self_test                                                                   # noqa: E402

AXES = ["dTopt", "topt_scale", "dCp_scale", "tm_scale", "kcat_scale", "sigma", "clearance_mult"]
OFFS = [-0.04, -0.02, 0.02, 0.04]
SOLVE_S, BATCH_S = 300, 4 * 3600
FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
_, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAY = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
           c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
NAMES = [s.name for s in FULL_SPECS]; FREE = [s.name for s in FREE_SPECS]
OUT = os.path.join(HERE, "task3_trace.json")
LIVING_FRAC, PEAK_OBS = 0.5, 2.0761


def sha(x): return hashlib.sha256(np.asarray(x, float).tobytes()).hexdigest()


def evaluate(th16):
    """one FRESH evaluation: per-datum contributions, enzyme state, statuses; reconciled."""
    ctx, sp = _build_gasflux_ctx(**PAY); resp = ctx.get("respiration") or {}
    nat = to_natural(th16, sp); pert = to_pert(th16, sp); pm = ctx["pm"]
    if "clearance_mult" in nat:
        r = ctx["recipe"]
        _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
        if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
    df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")),
                  growth_tol=float(resp.get("growth_tol", 1e-6)), tiebreak_tol=float(resp.get("tiebreak_tol", 1e-9)))
    g = df["growth"].to_numpy(float); o2 = df["o2_uptake"].to_numpy(float); st = list(map(str, df["status"]))
    # --- the exact per-datum arithmetic of gasflux_log_likelihood ---
    dg = float(nat["disc_growth"]); var = ctx["growth_sd"] ** 2 + dg ** 2
    gterm = -0.5 * ((ctx["growth_obs"] - g) ** 2 / var + np.log(2 * np.pi * var))
    keep = np.isfinite(o2) & (o2 > 0) if str(resp.get("support")) == "clamp" else ((g >= _MASK_G) & (o2 > 0))
    rterm = np.zeros_like(g)
    if keep.any():
        dr = float(nat["disc_resp"]); rs = float(nat["resp_scale"]); floor = float(resp.get("log_o2_floor", 0.0))
        pred = np.log(o2[keep] * ctx["o2_conv"] * rs); obsl = np.log(ctx["resp_obs"][keep])
        rel = ctx["resp_sd"][keep] / ctx["resp_obs"][keep]; varr = rel ** 2 + dr ** 2 + floor ** 2
        gs = resp.get("alive_soft_growth"); wf = float(resp.get("weight_floor", 1.0))
        w = np.maximum(np.minimum(1.0, g[keep] / float(gs)), wf) if gs else np.ones(int(keep.sum()))
        rterm[keep] = -0.5 * w * ((obsl - pred) ** 2 / varr + np.log(2 * np.pi * varr))
    total = float(np.sum(gterm) + np.sum(rterm)); ll = float(gasflux_log_likelihood(th16, ctx, sp))
    # --- enzyme thermal state, per temperature, from the same arrays the cost uses ---
    ec = pm.ec; Tk = np.asarray(ctx["T"], float) + 273.15
    Topt_eff = ec._T0 + pert.topt_scale * (ec._Topt - ec._T0) + pert.dTopt
    Tm_shift = pert.dTm + (pert.tm_scale - 1.0) * (ec._Tm - np.mean(ec._Tm))
    enz = []
    for T in Tk:
        rk = U.rel_kcat(T, ec._uHTH, ec._uSTS, ec._uCpu, ec._uCpt * pert.dCp_scale, Topt_eff)
        fN = U.native_fraction(T - Tm_shift, ec._uHTH, ec._uSTS, ec._uCpu)
        prod = np.nan_to_num(rk * fN, nan=1e-6, posinf=1e6, neginf=1e-6)
        enz.append(dict(above_Topt=int(np.sum(T > Topt_eff)), past_Tm=int(np.sum(T - Tm_shift > ec._Tm)),
                        clipped_low=int(np.sum(prod <= 1e-6)), clipped_high=int(np.sum(prod >= 1e6)),
                        nonfinite=int(np.sum(~np.isfinite(rk * fN)))))
    return dict(logl=ll, total_from_terms=total, reconciles=bool(abs(ll - total) < 1e-9),
                growth_term=gterm.tolist(), resp_term=rterm.tolist(), growth=g.tolist(), o2=o2.tolist(),
                status=st, scored=keep.astype(int).tolist(), enzyme_state=enz, fresh=True,
                sha_theta=sha(th16))


def diverse_points():
    """D1's registered rule; every choice recorded with its provenance."""
    out = []
    d = pd.read_csv("reports/P12_modes/task2c_converged.csv"); r = d[d.key == "p38(b22)"].iloc[0]
    out.append(("p38", r[[f"x_{n}" for n in NAMES]].to_numpy(float), "P12 task2c_converged.csv key p38(b22)"))
    p4 = "strains/eciML1515/outputs/calibration_configD_NLDM_recipe_cmax120"
    ch = np.load(os.path.join(p4, "chain.npy")); lp = np.load(os.path.join(p4, "log_prob.npy"))
    k = np.unravel_index(int(np.argmax(lp)), lp.shape); out.append(("P4_MAP", np.asarray(ch[k], float), f"argmax log_prob.npy at {k}"))
    z = np.load(os.path.join(ARCH, "reports/P17_inactive_prior/validated_live_input.npz"))
    th800 = np.array([expand(np.asarray(t, float)) for t in z["theta"]]); ll800 = np.asarray(z["stored_logl"], float)
    out.append(("red2_6800_living_median", None, "living subset of the 800 by peak growth >= 50 % of 2.0761; weighted-median stored_logl"))
    s = np.load("strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/samples_red2.npy")
    lw = np.load("strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/logwt_red2.npy")
    lg = np.load("strains/eciML1515/outputs/calibration_configD_NLDM_recipe_P16_reduced/logl_red2.npy")
    out.append(("red2_top_weight_living", None, "P16 red2 posterior; highest importance weight among living samples"))
    out.append(("red2_wmedian_logl_living", None, "P16 red2 posterior; weighted-median log L among living samples"))
    return out, (th800, ll800), (s, lw, lg)


def living(th16, cache):
    k = sha(th16)
    if k not in cache:
        ctx, sp = _build_gasflux_ctx(**PAY); resp = ctx.get("respiration") or {}
        nat = to_natural(th16, sp); pert = to_pert(th16, sp); pm = ctx["pm"]
        if "clearance_mult" in nat:
            r = ctx["recipe"]; _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]), uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
            if ctx.get("c_max") is not None: add_total_carbon_constraint(pm, float(ctx["c_max"]))
        df = flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak=str(resp.get("tiebreak", "none")))
        cache[k] = float(np.nanmax(df["growth"].to_numpy(float))) >= LIVING_FRAC * PEAK_OBS
    return cache[k]


def main():
    self_test(); t0 = time.time()
    plan = json.load(open("reports/P17_inactive_prior/real_curvature_probe/plan.json"))
    scale = np.asarray(plan["scale"], float); parent15 = np.asarray(plan["parent"], float)
    pt15 = transform_factory(FREE_SPECS)
    rec = dict(scale=scale.tolist(), axes=AXES, offsets=OFFS, evaluations=[], refinements=[], diverse=[])
    print("[t3] D44 parent + stencils (58, from the saved u), fresh each", flush=True)
    for e in json.load(open("reports/P17_inactive_prior/real_curvature_probe/evaluations.json")):
        if time.time() - t0 > BATCH_S: print("[t3] BATCH DEADLINE", flush=True); break
        th = expand(pt15(np.asarray(e["u"], float)))
        try:
            with deadline(SOLVE_S, e["label"]): r = evaluate(th)
            r.update(point="D44", label=e["label"], saved_logl=float(e["logl"]), vs_saved=abs(r["logl"] - float(e["logl"])))
        except Deadline as ex:
            r = dict(point="D44", label=e["label"], status="UNRESOLVED_TIMEOUT", note=str(ex))
        rec["evaluations"].append(r)
        if len(rec["evaluations"]) % 10 == 0:
            json.dump(rec, open(OUT, "w")); print(f"[t3] {len(rec['evaluations'])} evals; last {e['label']} logL {r.get('logl', float('nan')):.4f} vs saved {r.get('vs_saved', float('nan')):.2e} reconciles={r.get('reconciles')}", flush=True)
    # --- refinement (P14's instrument) on the parent along each axis's larger-step side ---
    base = [r for r in rec["evaluations"] if r.get("label") == "baseline_start"][0]
    parent16 = expand(pt15(parent15)); u0 = parent15.copy()
    for ax in AXES:
        j = FREE.index(ax); ser = []
        for h in (0.04, 0.02, 0.01, 0.005):
            if time.time() - t0 > BATCH_S: break
            u = u0.copy(); u[j] = u0[j] + h * scale[j]
            try:
                with deadline(SOLVE_S, f"refine {ax} {h}"): r = evaluate(expand(pt15(u)))
                ser.append(dict(h=h, logl=r["logl"], delta=r["logl"] - base["logl"], clipped_low=[x["clipped_low"] for x in r["enzyme_state"]], status=r["status"]))
            except Deadline as ex:
                ser.append(dict(h=h, status="UNRESOLVED_TIMEOUT", note=str(ex)))
        rec["refinements"].append(dict(axis=ax, series=ser)); json.dump(rec, open(OUT, "w"))
        print(f"[t3] refine {ax}: " + " -> ".join(f"{s.get('delta', float('nan')):+.4f}" for s in ser), flush=True)
    # --- the five diverse points ---
    dp, (th800, ll800), (s, lw, lg) = diverse_points(); cache = {}
    w = np.exp(lw - lw.max()); w /= w.sum()
    rng = np.random.default_rng(17201)
    liv800 = np.array([living(t, cache) for t in th800]) if time.time() - t0 < BATCH_S else np.zeros(len(th800), bool)
    if liv800.any():
        i = np.argsort(ll800[liv800]); k = int(np.where(liv800)[0][i][len(i) // 2]); dp[2] = ("red2_6800_living_median", th800[k], f"index {k} of 800; {int(liv800.sum())} living")
    order = np.argsort(-w); cand = [int(i) for i in order[:400]]
    livs = [i for i in cand if time.time() - t0 < BATCH_S and living(expand(np.asarray(s[i], float)), cache)]
    if livs:
        dp[3] = ("red2_top_weight_living", expand(np.asarray(s[livs[0]], float)), f"sample {livs[0]}, weight rank {cand.index(livs[0])}")
        ws = w[livs]; ls = lg[livs]; o = np.argsort(ls); c = np.cumsum(ws[o]) / ws.sum(); m = livs[o[int(np.searchsorted(c, 0.5))]]
        dp[4] = ("red2_wmedian_logl_living", expand(np.asarray(s[m], float)), f"sample {m} among {len(livs)} living of the top-400-weight")
    for name, th, prov in dp:
        if th is None or time.time() - t0 > BATCH_S: rec["diverse"].append(dict(point=name, provenance=prov, status="NOT_EVALUATED")); continue
        try:
            with deadline(SOLVE_S, name): b = evaluate(th)
        except Deadline as ex:
            rec["diverse"].append(dict(point=name, provenance=prov, status="UNRESOLVED_TIMEOUT", note=str(ex))); continue
        d = dict(point=name, provenance=prov, sha_theta=sha(th), base=b, stencils=[])
        u_c = np.delete(th, FIXED_IDX)
        for ax in AXES:
            j = FREE.index(ax)
            for off in OFFS:
                if time.time() - t0 > BATCH_S: break
                # move in the SAMPLED coordinate by off * group SD (D44's scale is in the unit cube; use the same
                # cube step by pushing through the transform from the point's own cube coordinate)
                try:
                    with deadline(SOLVE_S, f"{name} {ax} {off}"):
                        u_pt = None
                        r = evaluate(expand(_shift_sampled(u_c, j, off * scale[j], pt15)))
                    d["stencils"].append(dict(axis=ax, off=off, logl=r["logl"], delta=r["logl"] - b["logl"], growth_term=r["growth_term"], resp_term=r["resp_term"], enzyme_state=r["enzyme_state"], status=r["status"]))
                except Deadline as ex:
                    d["stencils"].append(dict(axis=ax, off=off, status="UNRESOLVED_TIMEOUT", note=str(ex)))
        rec["diverse"].append(d); json.dump(rec, open(OUT, "w")); print(f"[t3] diverse {name} done ({len(d['stencils'])} stencils)", flush=True)
    rec["wall_min"] = round((time.time() - t0) / 60, 1); json.dump(rec, open(OUT, "w"))
    print(f"[t3] done in {rec['wall_min']} min", flush=True)


def _shift_sampled(u_c, j, du, pt15):
    """shift a 15-D SAMPLED point by du along axis j via the cube: invert numerically."""
    from scipy.optimize import brentq
    # find cube coordinate u_j such that pt15 maps it to the sampled value, then add du in cube
    def f(uj):
        v = np.full(15, 0.5); v[j] = uj; return pt15(v)[j] - u_c[j]
    uj = brentq(f, 1e-9, 1 - 1e-9); v = np.full(15, 0.5); v[j] = min(max(uj + du, 1e-9), 1 - 1e-9)
    out = u_c.copy(); out[j] = pt15(v)[j]; return out


if __name__ == "__main__":
    main()
