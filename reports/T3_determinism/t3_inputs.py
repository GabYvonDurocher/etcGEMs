#!/usr/bin/env python3
"""T3 TASK 0 -- the FIXED INPUT SET, built by registered rule from on-disk artefacts and hashed.
  (i)   run 3's crashing live point (checkpoint index 654; stored -18.480, fresh -19.7608540096);
  (ii)  the other three +1.28 points of run 3's checkpoint (indices 791, 297, 105);
  (iii) the five largest-|offset| live points of run 1 and of run 2 from T2's exhaustive audit
        (task5_livepoints_all.json `worst`), by index, at full precision from the checkpoints;
  (iv)  prior draws, seed 17401, taken in order: the first three feasible everywhere and the first two
        infeasible somewhere (feasibility by one fresh evaluation, recorded);
  (v)   Parsa's E LB MAP theta in our E LB specs (P10 D3a's route, reports/P5_lb_cmax/task1e_reoptimise.py),
        plus two E LB prior draws (seed 17402) as interleaving companions.
Writes inputs.json: label, set, space (D_NLDM_validation | E_LB), u (if any), theta (sampled vector the
likelihood takes), sha256 of theta, provenance."""
import os, sys, json, hashlib, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), os.path.join(ROOT, "reports", "T2_validated_posterior"),
          os.path.join(ROOT, "reports", "P5_lb_cmax"), os.path.join(ROOT, "reports", "P3_gate"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
import dynesty
from t2_target import build, Target
from t2_prior import transform_factory
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood
from p6_fits import FITS
OUT = "strains/eciML1515/outputs/calibration_configD_NLDM_recipe_T2_validated"


def sha(x): return hashlib.sha256(np.asarray(x, float).tobytes()).hexdigest()


def main():
    ctx, specs = build(validation=True); tg = Target(specs); pt = transform_factory(tg.sampled)
    lp = json.load(open("reports/T2_validated_posterior/task5_livepoints_all.json")); inputs = []
    def add(label, set_, space, u, th, prov, **extra):
        inputs.append(dict(label=label, set=set_, space=space, u=(None if u is None else np.asarray(u, float).tolist()), theta=np.asarray(th, float).tolist(), sha256_theta=sha(th), provenance=prov, **extra))
    s3 = dynesty.NestedSampler.restore(f"{OUT}/run3_seed17903/dynesty.save"); U3, L3 = np.asarray(s3.live_u), np.asarray(s3.live_logl)
    add("run3:654:crash", "i", "D_NLDM_validation", U3[654], tg.expand(pt(U3[654])), "run 3 checkpoint it 9288, live point 654 (the crash point)", stored_logl=float(L3[654]))
    for i in (791, 297, 105):
        add(f"run3:{i}", "ii", "D_NLDM_validation", U3[i], tg.expand(pt(U3[i])), f"run 3 checkpoint, live point {i} (+1.28 offset in T2's audit)", stored_logl=float(L3[i]))
    for k, seed in ((1, 17901), (2, 17902)):
        s = dynesty.NestedSampler.restore(f"{OUT}/run{k}_seed{seed}/dynesty.save"); U, L = np.asarray(s.live_u), np.asarray(s.live_logl)
        for w in lp[str(k)]["worst"]:
            i = int(w["i"]); add(f"run{k}:{i}", "iii", "D_NLDM_validation", U[i], tg.expand(pt(U[i])), f"run {k} final checkpoint, live point {i}; T2 audit offset {w['diff']:.3e}", stored_logl=float(L[i]), t2_offset=float(w["diff"]))
    rng = np.random.default_rng(17401); feas, infe, tried = [], [], 0
    while len(feas) < 3 or len(infe) < 2:
        u = rng.random(tg.D); th = tg.expand(pt(u)); ll = float(gasflux_log_likelihood(th, ctx, specs)); tried += 1
        if ll == -np.inf and len(infe) < 2: infe.append((u, th, ll, tried))
        elif np.isfinite(ll) and len(feas) < 3: feas.append((u, th, ll, tried))
    for u, th, ll, n in feas: add(f"prior17401:draw{n}:feasible", "iv", "D_NLDM_validation", u, th, f"prior draw {n} of seed 17401; feasible everywhere (fresh log L {ll:.6f})", fresh_at_build=ll)
    for u, th, ll, n in infe: add(f"prior17401:draw{n}:infeasible", "iv", "D_NLDM_validation", u, th, f"prior draw {n} of seed 17401; infeasible somewhere (-inf)", fresh_at_build=ll)
    # (v) E LB
    fit = [f for f in FITS if f[0] == "E_LB"][0]; _, CFG, MED, TAB, OTU, CM, ETC, PR, FK = fit
    pay_e = dict(strain="eciML1515", medium=MED, experiment=f"gasflux_config{CFG}", table=TAB, otu=OTU, c_max=CM, etc_table=ETC, apply_protons=PR, fit_clearance=FK)
    ctx_e, sp_e = _build_gasflux_ctx(**pay_e)
    from task1e_reoptimise import his_theta_in_our_specs
    cdir = os.path.join(os.environ.get("PARSA_ROOT", "/Users/g.yvon-durocher/Downloads/etcGEMs-main_3"), "strains", "eciML1515", "outputs", "calibration_configE_LB_freecmax")
    th_e, his_cap = his_theta_in_our_specs(cdir, sp_e); ll_e = float(gasflux_log_likelihood(th_e, ctx_e, sp_e))
    add("ELB:parsa_MAP", "v", "E_LB", None, th_e, f"Parsa's E LB MAP (calibration_configE_LB_freecmax) in our E LB specs [{', '.join(s.name for s in sp_e)}], c_max {CM} (his fitted cap {his_cap:.1f}); fresh log L {ll_e:.6f}", fresh_at_build=ll_e)
    pt_e = transform_factory(sp_e); rng_e = np.random.default_rng(17402)
    for n in (1, 2):
        u = rng_e.random(len(sp_e)); th = pt_e(u); ll = float(gasflux_log_likelihood(th, ctx_e, sp_e))
        add(f"ELB:prior17402:draw{n}", "v-companion", "E_LB", u, th, f"E LB prior draw {n} of seed 17402 (interleaving companion; fresh log L {ll})", fresh_at_build=ll)
    meta = dict(n_inputs=len(inputs), counts={s_: sum(1 for x in inputs if x["set"] == s_) for s_ in ("i", "ii", "iii", "iv", "v", "v-companion")},
                D_NLDM_names=tg.names, E_LB_names=[s.name for s in sp_e], E_LB_payload=pay_e, prior_draws_tried=tried,
                checkpoint_sha256={f"run{k}": hashlib.sha256(open(f"{OUT}/run{k}_seed{s}/dynesty.save", "rb").read()).hexdigest() for k, s in ((1, 17901), (2, 17902), (3, 17903))})
    json.dump(dict(meta=meta, inputs=inputs), open(os.path.join(HERE, "inputs.json"), "w"), indent=1)
    print("[inputs]", json.dumps(meta["counts"]), "| prior draws tried:", tried)
    for x in inputs: print(f"  {x['label']:32s} {x['set']:12s} {x['space']:18s} sha {x['sha256_theta'][:12]}  {x['provenance'][:90]}")
    print("[inputs] sha256(inputs.json) =", hashlib.sha256(open(os.path.join(HERE, "inputs.json"), "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
