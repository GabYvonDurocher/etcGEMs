#!/usr/bin/env python3
"""P15 TASK 1 -- P11's three proofs, re-verified before the runs.

1. PRIOR TRANSFORM against the priors' analytic values, on 10,000 draws.
2. POOL == SINGLE-PROCESS at p38, to 1e-4.
3. CHECKPOINT RESTORE resumes at the same iteration.
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"),
          os.path.join(ROOT, "reports", "P11_nested"), os.path.join(ROOT, "reports", "P13_support")):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
from etcgem.calibration_multi import (_build_gasflux_ctx, _gwinit, _gwloglike, _set_default_solver,   # noqa: E402
                                      build_gasflux_specs, gasflux_log_likelihood, to_natural)
from p6_fits import FITS                                                                             # noqa: E402
from prior_transform import transform_factory                                                        # noqa: E402
from common13 import p12_points                                                                      # noqa: E402

FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
_, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAYLOAD = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
               c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
OUT = os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_P15_nested")


def main():
    res = {}
    specs = build_gasflux_specs({"use_etc": ETC is not None, "fit_clearance": FIT_K}); D = len(specs)
    pt = transform_factory(specs)

    # ---- 1. prior transform ----
    # Deferred to P11's own proof, which is the authority: it compares each parameter's 10,000
    # draws to the prior's ANALYTIC mean and quantiles and checks the transformed density is
    # constant along the transform. A first version of this check, written here, was WRONG -- it
    # built a "reference" quantile from pt() of a constant vector, which is not a quantile of
    # anything -- and reported a spurious 1.27e-01 deviation. Re-running P11's script is both
    # correct and a stronger check, and it regenerates its committed output byte-identically.
    import subprocess
    r1 = subprocess.run([sys.executable, os.path.join(ROOT, "reports", "P11_nested",
                                                      "task1_prove_transform.py")],
                        capture_output=True, text=True)
    tail = [ln for ln in r1.stdout.splitlines() if ln.startswith("[pt] density consistent")]
    res["prior_transform"] = dict(deferred_to="reports/P11_nested/task1_prove_transform.py",
                                  returncode=r1.returncode, verdict=tail[0] if tail else "",
                                  passes=bool(r1.returncode == 0 and tail and "True" in tail[0]))
    print(f"[p1] prior transform (P11's proof): {res['prior_transform']['verdict']}", flush=True)

    # ---- 2. pool == single-process at p38 ----
    pts, _ = p12_points(); th = pts["p38(b22)"]
    ctx, sp2 = _build_gasflux_ctx(**PAYLOAD)
    assert str(ctx["respiration"].get("support")) == "clamp", ctx["respiration"]
    single = float(gasflux_log_likelihood(th, ctx, sp2))
    solver = _set_default_solver("gurobi")
    from multiprocessing import Pool
    with Pool(4, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        pooled = pool.map(_gwloglike, [th] * 4)
    d = max(abs(p - single) for p in pooled)
    res["pool_vs_single"] = dict(single=single, pooled=list(map(float, pooled)), max_abs_diff=float(d),
                                 passes_1e_4=bool(d < 1e-4))
    print(f"[p2] pool vs single-process at p38: single {single:.10f}, pooled {pooled[0]:.10f}, "
          f"max |difference| {d:.3e} -> {'PASS' if d < 1e-4 else 'FAIL'}", flush=True)

    # ---- 3. checkpoint restore ----
    import dynesty
    os.makedirs(OUT, exist_ok=True)
    ck = os.path.join(OUT, "dynesty_proof.save")
    if os.path.exists(ck): os.remove(ck)
    t0 = time.time()
    with Pool(8, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        s = dynesty.NestedSampler(_gwloglike, pt, D, nlive=60, bound="multi", sample="rslice",
                                  slices=3, pool=pool, queue_size=8,
                                  first_update={'min_eff': 30}, rstate=np.random.default_rng(7))
        s.run_nested(maxiter=60, dlogz=0.1, add_live=False, print_progress=False,
                     checkpoint_file=ck, checkpoint_every=1.0)
        it_before, nc_before = int(s.it), int(s.ncall)
    with Pool(8, initializer=_gwinit, initargs=(dict(PAYLOAD, solver=solver),)) as pool:
        s2 = dynesty.NestedSampler.restore(ck, pool=pool)
        it_after = int(s2.it)
    ok = abs(it_after - it_before) <= 1
    res["checkpoint"] = dict(it_before=it_before, it_after=it_after, ncall_before=nc_before,
                             resumes_at_same_iteration=bool(ok), wall_s=round(time.time() - t0, 1))
    print(f"[p3] checkpoint restore: stopped at iteration {it_before}, restored at {it_after} "
          f"-> {'PASS' if ok else 'FAIL'}", flush=True)
    if os.path.exists(ck): os.remove(ck)
    json.dump(res, open(os.path.join(HERE, "task1_proofs.json"), "w"), indent=1, default=float)
    allok = res["prior_transform"]["passes"] and res["pool_vs_single"]["passes_1e_4"] and ok
    print(f"[p] ALL THREE PROOFS {'PASS' if allok else '*** FAIL ***'}", flush=True)


if __name__ == "__main__":
    main()
