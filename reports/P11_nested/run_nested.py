#!/usr/bin/env python3
"""P11 TASK 2 -- nested sampling of the D NLDM posterior with dynesty.

The likelihood is P10's, with both options ON for eciML1515 (read from the strain config by
`_build_gasflux_ctx`), evaluated on a process pool whose workers each build their own provider
(`_gwinit`) -- the same pool path P4/P6/P7 used, and the same worker callable family; the only
new one is `_gwloglike`, the likelihood without the prior, which is what a sampler that handles
the prior itself needs. The prior comes in through `prior_transform.py`, the inverse CDF of
P4's priors (proven in task1_prove_transform.py).

    python run_nested.py --tag main --nlive 500 --sample rslice --slices 3 --hours 4
    python run_nested.py --tag main --resume            # from the checkpoint
    python run_nested.py --tag seed2 --nlive 250 --seed 2 --hours 1
    python run_nested.py --calibrate 120                # cost only: N iterations, no output kept
"""
import argparse, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "reports", "P6_convergence")); sys.path.insert(0, HERE)
os.chdir(ROOT)
from etcgem.calibration_multi import (_build_gasflux_ctx, _gwinit, _gwloglike, _set_default_solver,   # noqa: E402
                                      build_gasflux_specs, gasflux_log_likelihood)
from p6_fits import FITS                                                                             # noqa: E402
from prior_transform import transform_factory                                                        # noqa: E402

FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
LABEL, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAYLOAD = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
               c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P11_nested")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="main"); ap.add_argument("--nlive", type=int, default=500)
    ap.add_argument("--sample", default="rslice"); ap.add_argument("--slices", type=int, default=3)
    ap.add_argument("--bound", default="multi"); ap.add_argument("--dlogz", type=float, default=0.1)
    ap.add_argument("--hours", type=float, default=4.0); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--nproc", type=int, default=16); ap.add_argument("--resume", action="store_true")
    ap.add_argument("--calibrate", type=int, default=0)
    a = ap.parse_args()
    import dynesty
    specs = build_gasflux_specs({"use_etc": ETC is not None, "fit_clearance": FIT_K}); D = len(specs)
    ptform = transform_factory(specs)
    ctx, _ = _build_gasflux_ctx(**PAYLOAD)
    print(f"[nested] respiration options from the strain config: {ctx['respiration']}", flush=True)
    assert ctx["respiration"].get("tiebreak") == "pfba" and float(ctx["respiration"].get("log_o2_floor", 0)) > 0
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, f"dynesty_{a.tag}.save")
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(a.nproc, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        if a.resume and os.path.exists(ckpt):
            s = dynesty.NestedSampler.restore(ckpt, pool=pool)
            print(f"[nested] resumed from {os.path.basename(ckpt)} at iteration {s.results.niter}", flush=True)
        else:
            s = dynesty.NestedSampler(_gwloglike, ptform, D, nlive=a.nlive, bound=a.bound, sample=a.sample,
                                      slices=a.slices, pool=pool, queue_size=a.nproc,
                                      rstate=np.random.default_rng(a.seed))
        if a.calibrate:
            s.run_nested(maxiter=a.calibrate, dlogz=a.dlogz, print_progress=False)
            r = s.results; wall = time.time() - t0
            out = dict(iters=int(r.niter), ncall=int(sum(r.ncall)), wall_s=round(wall, 1),
                       calls_per_iter=round(sum(r.ncall) / max(1, r.niter), 1),
                       s_per_call_wall=round(wall / max(1, sum(r.ncall)), 4),
                       evals_per_s=round(sum(r.ncall) / wall, 2), dlogz_now=float(r.logzerr[-1]),
                       nlive=a.nlive, sample=a.sample, slices=a.slices, nproc=a.nproc)
            json.dump(out, open(os.path.join(HERE, f"calibrate_{a.tag}.json"), "w"), indent=1)
            print(f"[nested] CALIBRATION {out}", flush=True); return
        # The 4 h cap is enforced here, in wall clock, because dynesty has no time limit of its
        # own: the run proceeds in chunks of `chunk` iterations and stops at the deadline. A
        # chunk that adds no iterations means dynesty's own dlogz criterion was met, which is
        # the CONVERGED branch of the rule in DECISIONS D2. add_live is deferred to the end so
        # the final live points are folded in exactly once.
        deadline = t0 + a.hours * 3600.0
        chunk, prev_it, converged, trace = 100, s.it, False, []
        while True:
            s.run_nested(maxiter=chunk, dlogz=a.dlogz, add_live=False, print_progress=False,
                         checkpoint_file=ckpt, checkpoint_every=180)
            now = time.time()
            dlz = float(s.saved_run["logz"][-1]) if len(s.saved_run["logz"]) else float("nan")
            trace.append(dict(t_min=round((now - t0) / 60, 2), it=int(s.it), ncall=int(s.ncall),
                              logz=dlz, eff=float(s.eff)))
            print(f"[nested] {(now-t0)/60:7.1f} min  it {s.it:6d}  ncall {s.ncall:8d}  "
                  f"logz {dlz:10.3f}  eff {s.eff:.3f}%", flush=True)
            if s.it == prev_it:
                converged = True
                print("[nested] dynesty stopped on its own dlogz criterion", flush=True); break
            prev_it = s.it
            if now >= deadline:
                print(f"[nested] wall-clock cap of {a.hours} h reached -- stopping", flush=True); break
        s.add_final_live(print_progress=False)
        json.dump(trace, open(os.path.join(HERE, f"trace_{a.tag}.json"), "w"), indent=1)
    r = s.results; wall = time.time() - t0
    np.save(os.path.join(OUT, f"samples_{a.tag}.npy"), r.samples)
    np.save(os.path.join(OUT, f"logwt_{a.tag}.npy"), r.logwt)
    np.save(os.path.join(OUT, f"logl_{a.tag}.npy"), r.logl)
    w = np.exp(r.logwt - r.logz[-1]); n_eff = float(w.sum() ** 2 / np.sum(w ** 2))
    summ = dict(tag=a.tag, converged_on_dlogz=bool(converged), hours_cap=a.hours, nlive=a.nlive, sample=a.sample, slices=a.slices, bound=a.bound, seed=a.seed, nproc=a.nproc,
                dlogz_target=a.dlogz, iters=int(r.niter), ncall=int(sum(r.ncall)), wall_s=round(wall, 1),
                wall_h=round(wall / 3600, 3), evals_per_s=round(sum(r.ncall) / wall, 2),
                calls_per_iter=round(sum(r.ncall) / max(1, r.niter), 1), logz=float(r.logz[-1]),
                logzerr=float(r.logzerr[-1]), dlogz_final=float(r.logzerr[-1]), n_eff=n_eff,
                eff_percent=float(r.eff), respiration=ctx["respiration"])
    json.dump(summ, open(os.path.join(OUT, f"summary_{a.tag}.json"), "w"), indent=1, default=float)
    print(f"[nested] {summ}", flush=True); print("[nested] done", flush=True)


if __name__ == "__main__":
    main()
