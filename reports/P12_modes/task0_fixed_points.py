#!/usr/bin/env python3
"""P12 TASK 0 -- the three fixed points decomposed, and the cost of one evaluation.

(1) log-likelihood at theta_A (P11 main median), theta_B (P11 seed-2 median), theta_P4, fresh
    model per point, single process, with the per-temperature per-term decomposition: which
    data points prefer A over B and by how much.
(2) A profile of one evaluation: LP solve against model preparation, the split Pettersen &
    Almaas measured at 20/80 and cut 8.5x.
Writes task0_decomposition.csv, task0_profile.json beside this file."""
import json, os, sys, time
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common import (build, decompose, fixed_points, SPECS, NAMES, to_natural, to_pert,   # noqa: E402
                    flux_tpc, add_total_carbon_constraint, _prov, ROOT)
from etcgem.tpc import apply_state                                                        # noqa: E402


def profile_one(th, ctx, sp, reps=3):
    """time the pieces of one likelihood evaluation, as the likelihood itself does them"""
    nat = to_natural(th, sp); pert = to_pert(th, sp); pm = ctx["pm"]; m = pm.ec.model
    r = ctx["recipe"]; out = dict(n_temps=len(ctx["T"]))
    t = time.perf_counter()
    for _ in range(reps):
        _prov.set_medium_recipe(pm, r["recipe_csv"], clearance_L_per_gDW_h=r["clearance"] * float(nat["clearance_mult"]),
                                uptake_ub=r.get("uptake_ub", 1000.0), verbose=False)
    out["medium_s"] = (time.perf_counter() - t) / reps
    t = time.perf_counter()
    for _ in range(reps):
        add_total_carbon_constraint(pm, float(ctx["c_max"]))
    out["carbon_cap_s"] = (time.perf_counter() - t) / reps
    t_state = t_growth = t_tie = t_read = 0.0
    for T in ctx["T"]:
        t = time.perf_counter(); apply_state(pm.ec, float(T), pert); t_state += time.perf_counter() - t
        t = time.perf_counter(); g = m.slim_optimize(); t_growth += time.perf_counter() - t
        if g is not None and np.isfinite(g) and g >= 1e-6:
            t = time.perf_counter()
            from etcgem.gasflux import _tiebroken_solve
            with m:
                gp = m.solver.problem
                keep = {k: gp.getParamInfo(k)[2] for k in ("OptimalityTol", "FeasibilityTol")}
                for k in keep: gp.setParam(k, 1e-9)
                _tiebroken_solve(m, g, "pfba", 1e-6)
                t_tie += time.perf_counter() - t
                t = time.perf_counter()
                _ = float(m.reactions.get_by_id("EX_o2_e_REV").flux - m.reactions.get_by_id("EX_o2_e").flux)
                t_read += time.perf_counter() - t
                for k, v in keep.items(): gp.setParam(k, v)
    out.update(apply_state_s=t_state, growth_lp_s=t_growth, tiebreak_lp_s=t_tie, flux_read_s=t_read)
    t = time.perf_counter(); flux_tpc(pm, ctx["T"], pert, metabolites=("o2",), tiebreak="pfba", tiebreak_tol=1e-9)
    out["flux_tpc_total_s"] = time.perf_counter() - t
    out["total_s"] = out["medium_s"] + out["carbon_cap_s"] + out["flux_tpc_total_s"]
    prep = out["medium_s"] + out["carbon_cap_s"] + out["apply_state_s"]
    lp = out["growth_lp_s"] + out["tiebreak_lp_s"]
    out["preparation_s"] = prep; out["lp_solve_s"] = lp
    out["percent_in_lp"] = 100 * lp / (prep + lp + out["flux_read_s"])
    out["percent_in_preparation"] = 100 * prep / (prep + lp + out["flux_read_s"])
    return out


def main():
    fp = fixed_points(); rows = []; tot = {}
    for name, th in fp.items():
        ctx, sp = build()
        d = decompose(th, ctx, sp)
        tot[name] = d
        print(f"[t0] theta_{name}: log-likelihood {d['logl']:9.3f}  (growth terms {d['growth_term'].sum():8.3f} + "
              f"respiration {d['resp_term'].sum():8.3f}); log-prior {d['logprior']:8.3f}", flush=True)
        for i, T in enumerate(d["T"]):
            rows.append(dict(point=name, T_C=float(T), growth_obs=d["growth_obs"][i], growth_pred=d["growth"][i],
                             o2_pred=d["o2"][i], resp_obs=d["resp_obs"][i], weight=d["weight"][i],
                             growth_term=d["growth_term"][i], resp_term=d["resp_term"][i]))
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "task0_decomposition.csv"), index=False)
    # which data points prefer A over B
    a = df[df.point == "A"].set_index("T_C"); b = df[df.point == "B"].set_index("T_C")
    d_g = a.growth_term - b.growth_term; d_r = a.resp_term - b.resp_term
    print(f"\n[t0] A - B by temperature (positive = A fits better):", flush=True)
    print(f"[t0]   {'T':>5s} {'growth A-B':>11s} {'resp A-B':>10s} {'total':>8s}   growth pred A / B / obs      O2 A / B", flush=True)
    for T in a.index:
        print(f"[t0]   {T:5.0f} {d_g[T]:11.2f} {d_r[T]:10.2f} {d_g[T]+d_r[T]:8.2f}   "
              f"{a.growth_pred[T]:.3f} / {b.growth_pred[T]:.3f} / {a.growth_obs[T]:.3f}   {a.o2_pred[T]:7.2f} / {b.o2_pred[T]:7.2f}", flush=True)
    print(f"[t0] totals: growth {d_g.sum():+.2f}, respiration {d_r.sum():+.2f}, overall {d_g.sum()+d_r.sum():+.2f}", flush=True)
    ctx, sp = build(); prof = profile_one(fp["A"], ctx, sp)
    json.dump(prof, open(os.path.join(HERE, "task0_profile.json"), "w"), indent=1)
    print(f"\n[t0] one evaluation = {prof['total_s']:.2f} s: LP solves {prof['lp_solve_s']:.2f} s "
          f"({prof['percent_in_lp']:.0f} %), preparation {prof['preparation_s']:.2f} s ({prof['percent_in_preparation']:.0f} %) "
          f"[medium {prof['medium_s']:.3f}, carbon cap {prof['carbon_cap_s']:.3f}, apply_state {prof['apply_state_s']:.2f}], "
          f"flux reads {prof['flux_read_s']:.3f} s; growth LP {prof['growth_lp_s']:.2f} vs tie-break LP {prof['tiebreak_lp_s']:.2f}", flush=True)
    print("[t0] done", flush=True)


if __name__ == "__main__":
    main()
