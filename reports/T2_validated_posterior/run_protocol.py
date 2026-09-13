#!/usr/bin/env python3
"""T2 TASK 3/4 -- the detached batch driver for the protocol's five reserved-seed runs.

IDEMPOTENT   reads status.json and each run's run_status.json; a run complete-and-audited is skipped; a
             run with a checkpoint but no completion is RESUMED (dynesty restore, P11/P15-proven); else fresh.
SEQUENTIAL   seeds 17901..17905 in order, one at a time, 16 processes each.
SELF-AUDITING after each run: independent reconstruction from the checkpoint and saved arrays (restored
             arrays == saved; weights sum to one; ESS reproduces; unit-cube positions == inverse prior CDF;
             log Z re-derived from logl/logvol by this file's own quadrature; every hash in the manifest).
SELF-STOPPING an audit FAIL, a run reaching its alarm, an UnresolvedSolve, or any crash -> status.json
             stage driver_stopped with the reason and run number, and EXIT. No setting changes.
CHECKPOINTED every --ckpt-s seconds (default 1800) by dynesty; status.json updated after every chunk.
DETACHABLE   writes driver.pid on start, removes it on exit; logs to driver.log; asserts the Gurobi WLS
             licence before the first solve.
ALARMED      SIGALRM per run (default 16 h) and a whole-driver ceiling (default 72 h).
The driver does NOT judge the protocol checks (TASK 5 does); it runs, checkpoints, audits reproducibility
and stops on failure. --toy runs the same machinery on P17's smooth analytical target (the dry run).

    nohup ../etcGEMs-venv/bin/python reports/T2_validated_posterior/run_protocol.py > reports/T2_validated_posterior/driver.log 2>&1 &
    python run_protocol.py --toy --nlive 100 --seeds 17304 17305 --out reports/T2_validated_posterior/dryrun --ckpt-s 5 --chunk 50
"""
import argparse, os, sys, json, time, signal, hashlib, atexit, traceback, datetime, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), os.path.join(ROOT, "reports", "P11_nested"),
          os.path.join(ROOT, "reports", "P16_reduced"), os.path.join(ROOT, "reports", "P17_inactive_prior"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
os.chdir(ROOT)
import t2_status as S                                                    # noqa: E402
from t2_prior import transform_factory                                   # noqa: E402

SEEDS = [17901, 17902, 17903, 17904, 17905]
SOURCES = ["reports/T2_validated_posterior/run_protocol.py", "reports/T2_validated_posterior/t2_target.py",
           "reports/T2_validated_posterior/t2_prior.py", "src/etcgem/calibration_multi.py", "src/etcgem/gasflux.py",
           "src/etcgem/enzyme_cost.py", "src/etcgem/tpc.py", "strains/eciML1515/gas_exchange.yaml",
           "configs/experiments/gasflux_configD.yaml", "docs/VALIDATION_PROTOCOL.md"]
PID = os.path.join(HERE, "driver.pid"); LOG = None


def ts(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    line = f"{ts()}  {msg}"; print(line, flush=True)
    if LOG:
        with open(LOG, "a") as fh: fh.write(line + "\n")


def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()


def sha_arr(a): return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


class RunAlarm(Exception): pass
class DriverCeiling(Exception): pass


def _atomic_json(path, obj):
    tmp = path + f".tmp.{os.getpid()}"
    with open(tmp, "w") as fh: json.dump(obj, fh, indent=1, default=str); fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)


def run_status(run_dir): 
    p = os.path.join(run_dir, "run_status.json"); return json.load(open(p)) if os.path.exists(p) else {}


# ---------------------------------------------------------------- independent evidence quadrature ----
def integrate(logl, logvol):
    """this file's own re-implementation of the trapezoid evidence (Speagle 2020 eq. 16): NOT dynesty's helper."""
    logl = np.asarray(logl, float); logvol = np.asarray(logvol, float)
    lpad = np.concatenate([[-1e300], logl])
    dlv = np.diff(logvol, prepend=0.0)
    logdvol = logvol - dlv + np.log1p(-np.exp(dlv)) + np.log(0.5)
    logwt = np.logaddexp(lpad[1:], lpad[:-1]) + logdvol
    logz = np.logaddexp.accumulate(logwt)
    return logwt, logz


def audit_run(run_dir, ptform, toy):
    """independent reconstruction; returns (PASS bool, dict). Thresholds are the signed protocol's (f)."""
    import dynesty
    rep = dict(run_dir=run_dir, checks={})
    man = json.load(open(os.path.join(run_dir, "manifest.json"))); summ = json.load(open(os.path.join(run_dir, "summary.json")))
    ok = True
    # hashes of sources and inputs recorded at start; outputs recorded at end
    for k, v in man["hashes"].items():
        p = os.path.join(ROOT, k) if not os.path.isabs(k) else k
        h = sha(p) if os.path.exists(p) else None; good = (h == v); rep["checks"][f"hash:{k}"] = good; ok &= good
    arrs = {n: np.load(os.path.join(run_dir, f"{n}.npy")) for n in ("samples", "samples_u", "logwt", "logl", "logvol", "logz", "logzerr", "ncall")}
    # restore from the checkpoint and compare arrays
    s = dynesty.NestedSampler.restore(os.path.join(run_dir, "dynesty.save"))
    r = s.results
    for n, a in (("samples", r.samples), ("samples_u", r.samples_u), ("logwt", r.logwt), ("logl", r.logl), ("logvol", r.logvol), ("logz", r.logz)):
        good = bool(np.array_equal(arrs[n], np.asarray(a))); rep["checks"][f"restored==saved:{n}"] = good; ok &= good
    w = np.exp(arrs["logwt"] - arrs["logz"][-1]); rep["weight_sum_minus_1"] = float(abs(w.sum() - 1.0)); good = rep["weight_sum_minus_1"] <= 1e-12; rep["checks"]["weights_normalise_1e-12"] = good; ok &= good
    ess = float(w.sum() ** 2 / np.sum(w ** 2)); rep["ess_reproduced"] = ess; good = abs(ess - summ["n_eff"]) <= 1e-6 * max(1.0, ess); rep["checks"]["ess_reproduces"] = good; ok &= good
    lw2, lz2 = integrate(arrs["logl"], arrs["logvol"]); rep["logz_reconstructed"] = float(lz2[-1]); rep["logz_saved"] = float(arrs["logz"][-1])
    rep["logz_abs_err"] = float(abs(lz2[-1] - arrs["logz"][-1])); good = rep["logz_abs_err"] <= 1e-9; rep["checks"]["logz_reconstructs_1e-9"] = good; ok &= good
    rep["logwt_max_abs_err"] = float(np.max(np.abs(lw2 - arrs["logwt"])))
    if toy: cube_err = float(np.max(np.abs(arrs["samples_u"] - arrs["samples"])))
    else: cube_err = float(np.max(np.abs(ptform.inverse(arrs["samples"]) - arrs["samples_u"])))
    rep["cube_inverse_max_err"] = cube_err; good = cube_err <= 1e-14; rep["checks"]["cube_inverse_1e-14"] = good; ok &= good
    # final live points: the last nlive samples are the final live set folded in by add_final_live
    nlive = int(summ["nlive"]); rep["final_live_logl_min"] = float(arrs["logl"][-nlive:].min()); rep["final_live_all_finite"] = bool(np.all(np.isfinite(arrs["logl"][-nlive:])))
    good = rep["final_live_all_finite"]; rep["checks"]["final_live_finite"] = good; ok &= good
    for n in ("samples", "samples_u", "logwt", "logl", "logvol", "logz"):
        good = (sha_arr(arrs[n]) == man["output_hashes"][n]); rep["checks"][f"output_hash:{n}"] = good; ok &= good
    unres = os.path.join(run_dir, "unresolved.jsonl"); rep["unresolved_count"] = (sum(1 for _ in open(unres)) if os.path.exists(unres) else 0)
    rep["PASS"] = bool(ok); return bool(ok), rep


# ---------------------------------------------------------------------------- one run --------------
def one_run(k, seed, a, run_dir, loglike, ptform, D, pool_kwargs, toy):
    import dynesty
    os.makedirs(run_dir, exist_ok=True); rs = run_status(run_dir)
    if rs.get("complete") and rs.get("audit") == "PASS":
        log(f"run {k} seed {seed}: complete and audited -> skipped"); return "skipped"
    ckpt = os.path.join(run_dir, "dynesty.save"); man_p = os.path.join(run_dir, "manifest.json")
    if not os.path.exists(man_p):
        _atomic_json(man_p, dict(run=k, seed=seed, started=ts(), nlive=a.nlive, sample=a.sample, slices=a.slices, bound=a.bound, dlogz=a.dlogz,
                                 first_update={"min_eff": 30}, nproc=a.nproc, toy=toy, D=D, hashes={s_: sha(os.path.join(ROOT, s_)) for s_ in (SOURCES if not toy else SOURCES[:3])},
                                 registration_commit=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()))
    os.environ["T2_RUN_DIR"] = run_dir
    from multiprocessing import Pool
    t0 = time.time(); wall_prev = float(rs.get("wall_s", 0.0))
    def _alarm(*_): raise RunAlarm(f"run {k} reached its {a.alarm_h} h alarm")
    signal.signal(signal.SIGALRM, _alarm); remaining = max(1, int(a.alarm_h * 3600 - wall_prev)); signal.alarm(remaining)
    trace = rs.get("trace", []); unit_cube_ncall = rs.get("unit_cube_ncall")
    try:
        with Pool(a.nproc, **pool_kwargs) as pool:
            if os.path.exists(ckpt):
                s = dynesty.NestedSampler.restore(ckpt, pool=pool); log(f"run {k} seed {seed}: RESUMED from checkpoint at iteration {s.it}, ncall {s.ncall}")
            else:
                s = dynesty.NestedSampler(loglike, ptform, D, nlive=a.nlive, bound=a.bound, sample=a.sample, slices=a.slices, pool=pool, queue_size=a.nproc,
                                          first_update={"min_eff": 30}, rstate=np.random.default_rng(seed))
                log(f"run {k} seed {seed}: FRESH start, D={D}, nlive={a.nlive}")
            prev_it = s.it; converged = False
            while True:
                s.run_nested(maxiter=a.chunk, dlogz=a.dlogz, add_live=False, print_progress=False, checkpoint_file=ckpt, checkpoint_every=a.ckpt_s)
                now = time.time(); wall = wall_prev + (now - t0)
                lz = float(s.saved_run["logz"][-1]) if len(s.saved_run["logz"]) else float("nan")
                lv = float(s.saved_run["logvol"][-1]) if len(s.saved_run["logvol"]) else float("nan")
                lmax = float(np.max(s.live_logl)); dlz = float(np.logaddexp(lz, lmax + lv) - lz) if np.isfinite(lz) else float("nan")
                if unit_cube_ncall is None and not getattr(s, "unit_cube_sampling", True): unit_cube_ncall = int(s.ncall)
                trace.append(dict(t=ts(), it=int(s.it), ncall=int(s.ncall), logz=lz, dlogz=dlz, eff=float(s.eff), wall_h=round(wall / 3600, 3)))
                _atomic_json(os.path.join(run_dir, "run_status.json"), dict(run=k, seed=seed, complete=False, it=int(s.it), ncall=int(s.ncall), dlogz=dlz, logz=lz, wall_s=wall, trace=trace[-400:], unit_cube_ncall=unit_cube_ncall))
                S.write("driver_running", f"run {k}/5 seed {seed} it {s.it} dlogz {dlz:.3f}", current_run=k, iteration=int(s.it), dlogz=dlz, wall_h=round(wall / 3600, 3), ncall=int(s.ncall), unit_cube_ncall=unit_cube_ncall, driver_pid=os.getpid())
                if s.it % 250 == 0 or s.it == prev_it: log(f"run {k}  it {s.it:7d}  ncall {s.ncall:9d}  eff {s.eff:6.3f}%  logZ {lz:10.3f}  dlogz {dlz:8.3f}  wall {wall/3600:6.2f} h  unit-cube ncall {unit_cube_ncall}")
                if s.it == prev_it: converged = True; break
                prev_it = s.it
            s.add_final_live(print_progress=False); s.save(ckpt)
        signal.alarm(0)
    except RunAlarm as e:
        signal.alarm(0); log(f"ALARM: {e}"); return ("ALARM", str(e))
    r = s.results; wall = wall_prev + (time.time() - t0)
    for n in ("samples", "samples_u", "logwt", "logl", "logvol", "logz", "logzerr", "ncall"):
        np.save(os.path.join(run_dir, f"{n}.npy"), np.asarray(getattr(r, n)))
    w = np.exp(r.logwt - r.logz[-1]); n_eff = float(w.sum() ** 2 / np.sum(w ** 2))
    summ = dict(run=k, seed=seed, converged_on_dlogz=bool(converged), nlive=a.nlive, sample=a.sample, slices=a.slices, bound=a.bound, dlogz=a.dlogz, nproc=a.nproc, D=D,
                iters=int(r.niter), ncall=int(sum(r.ncall)), unit_cube_ncall=unit_cube_ncall, wall_s=round(wall, 1), wall_h=round(wall / 3600, 3),
                evals_per_s=round(sum(r.ncall) / max(1e-9, wall), 2), logz=float(r.logz[-1]), logzerr=float(r.logzerr[-1]), n_eff=n_eff, eff_percent=float(r.eff), finished=ts())
    _atomic_json(os.path.join(run_dir, "summary.json"), summ)
    man = json.load(open(man_p)); man["output_hashes"] = {n: sha_arr(np.load(os.path.join(run_dir, f"{n}.npy"))) for n in ("samples", "samples_u", "logwt", "logl", "logvol", "logz")}; man["finished"] = ts(); _atomic_json(man_p, man)
    _atomic_json(os.path.join(run_dir, "run_status.json"), dict(run=k, seed=seed, complete=True, audit=None, it=int(r.niter), ncall=int(sum(r.ncall)), wall_s=wall, trace=trace[-400:], unit_cube_ncall=unit_cube_ncall))
    log(f"run {k} COMPLETE: {summ}")
    return "complete"


def main():
    global LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--toy", action="store_true"); ap.add_argument("--nlive", type=int, default=800); ap.add_argument("--seeds", type=int, nargs="*", default=SEEDS)
    ap.add_argument("--nproc", type=int, default=16); ap.add_argument("--sample", default="rslice"); ap.add_argument("--slices", type=int, default=3); ap.add_argument("--bound", default="multi")
    ap.add_argument("--dlogz", type=float, default=0.1); ap.add_argument("--chunk", type=int, default=250); ap.add_argument("--ckpt-s", type=float, default=1800.0)
    ap.add_argument("--alarm-h", type=float, default=16.0); ap.add_argument("--ceiling-h", type=float, default=72.0)
    ap.add_argument("--out", default=os.path.join(ROOT, "strains", "eciML1515", "outputs", "calibration_configD_NLDM_recipe_T2_validated"))
    ap.add_argument("--rejection-n", type=int, default=2000)
    a = ap.parse_args()
    LOG = os.path.join(HERE, "dryrun_driver.log" if a.toy else "driver.log")
    if os.path.exists(PID):
        old = open(PID).read().strip()
        if old and subprocess.run(["ps", "-p", old], capture_output=True).returncode == 0:
            print(f"driver already running (pid {old}); refusing a duplicate launch"); sys.exit(3)
    open(PID, "w").write(str(os.getpid())); atexit.register(lambda: os.path.exists(PID) and os.remove(PID))
    log(f"driver start pid {os.getpid()} toy={a.toy} seeds={a.seeds} nlive={a.nlive} nproc={a.nproc} out={a.out}")
    # ceiling: a second timer via SIGALRM is per-run, so the ceiling is a wall-clock check between runs plus a hard kill via alarm inside runs
    t_driver0 = time.time()
    if not a.toy:
        lic = os.environ.get("GRB_LICENSE_FILE", os.path.expanduser("~/gurobi.lic"))
        assert os.path.exists(lic) and "WLSACCESSID" in open(lic).read(), f"Gurobi WLS licence not found at {lic}; set GRB_LICENSE_FILE"
        log(f"Gurobi WLS licence present at {lic}")
    # target
    if a.toy:
        import controls as c
        loglike = c.Target("smooth"); ptform = c.identity; D = 15; pool_kwargs = {}
        inv_ptform = None
    else:
        from t2_target import build, Target, payload, loglike as ll_fn
        from etcgem.calibration_multi import _gwinit, _set_default_solver
        ctx, specs = build(validation=True); tg = Target(specs); D = tg.D
        assert ctx["respiration"].get("infeasible") == "zero_lik" and "f_metab" not in tg.full_names and tg.names[-2:] == ["f_metab_diag", "beta31_diag"], tg.names
        ptform = transform_factory(tg.sampled); inv_ptform = ptform; loglike = ll_fn
        solver = _set_default_solver("gurobi"); pool_kwargs = dict(initializer=_gwinit, initargs=(dict(payload(True), solver=solver),))
        log(f"target: D={D} sampled {tg.names}; config hash {tg.config_hash()}")
    os.makedirs(a.out, exist_ok=True)
    stage = (S.read() or {}).get("stage")
    if not a.toy and stage in ("driver_finished", "task5_done", "task6_done"):
        log(f"status stage {stage}: nothing to run"); return 0
    try:
        for k, seed in enumerate(a.seeds, start=1):
            if (time.time() - t_driver0) / 3600 > a.ceiling_h: raise DriverCeiling(f"driver ceiling {a.ceiling_h} h reached before run {k}")
            run_dir = os.path.join(a.out, f"run{k}_seed{seed}")
            rs = run_status(run_dir)
            if not (rs.get("complete") and rs.get("audit") == "PASS"):
                if not a.toy and not rs.get("rejection_done"):
                    from task2_rejection import rejection
                    log(f"run {k}: prior-rejection sample (check d), 2,000 draws, rng([{seed}, 1])")
                    rej = rejection([seed, 1], a.rejection_n, a.nproc, validation=True)
                    os.makedirs(run_dir, exist_ok=True); _atomic_json(os.path.join(run_dir, "rejection.json"), rej)
                    rs = run_status(run_dir); rs.update(rejection_done=True, run=k, seed=seed); _atomic_json(os.path.join(run_dir, "run_status.json"), rs)
                    log(f"run {k}: rejection fraction {rej['fraction']:.4f} wilson {rej['wilson95']} first-T {rej['first_infeasible_T_counts']} unresolved {rej['n_unresolved']}")
                if not a.toy: S.write("driver_running", f"run {k}/5 seed {seed} starting", current_run=k, driver_pid=os.getpid())
                res = one_run(k, seed, a, run_dir, loglike, ptform, D, pool_kwargs, a.toy)
                if isinstance(res, tuple):
                    S.write("driver_stopped", f"{res[0]} on run {k}: {res[1]}", stopped_reason=res[0], stopped_run=k, driver_pid=None); return 2
            rs = run_status(run_dir)
            if rs.get("audit") != "PASS":
                ok, rep = audit_run(run_dir, inv_ptform, a.toy); _atomic_json(os.path.join(run_dir, "audit.json"), rep)
                rs.update(audit="PASS" if ok else "FAIL"); _atomic_json(os.path.join(run_dir, "run_status.json"), rs)
                log(f"run {k} AUDIT {'PASS' if ok else 'FAIL'}: {[c_ for c_, v in rep['checks'].items() if not v]} logz err {rep['logz_abs_err']:.2e} cube err {rep['cube_inverse_max_err']:.2e} weights {rep['weight_sum_minus_1']:.2e} unresolved {rep['unresolved_count']}")
                if not ok:
                    S.write("driver_stopped", f"AUDIT_FAIL on run {k}", stopped_reason="AUDIT_FAIL", stopped_run=k, driver_pid=None); return 2
                if rep["unresolved_count"] > 0:
                    S.write("driver_stopped", f"UNRESOLVED_SOLVE recorded in run {k}", stopped_reason="UNRESOLVED_SOLVE", stopped_run=k, driver_pid=None); return 2
            cur = S.read() or {}
            if not a.toy:
                S.write("driver_running", f"run {k} complete and audited", runs_complete=k, runs_audited=k, driver_pid=os.getpid())
                if k == 1:
                    summ = json.load(open(os.path.join(run_dir, "summary.json")))
                    proj = f"""

## D-driver — run 1 measured; projection for runs 2–5 (written by run_protocol.py, {ts()})

Run 1 (seed 17901): {summ['iters']} iterations, {summ['ncall']} likelihood evaluations, unit-cube draws to the first bound
{summ['unit_cube_ncall']}, {summ['wall_h']} h wall ({summ['evals_per_s']} evals/s on {summ['nproc']} processes), log Z {summ['logz']:.3f} ± {summ['logzerr']:.3f},
n_eff {summ['n_eff']:.0f}, converged on dlogz: {summ['converged_on_dlogz']}. **Projection, if runs 2–5 track run 1:** {4*summ['wall_h']:.1f} h more,
finishing about {(datetime.datetime.now()+datetime.timedelta(hours=4*summ['wall_h'])).strftime('%Y-%m-%d %H:%M')}. Each run's own 16 h alarm stands.
"""
                    with open(os.path.join(HERE, "DECISIONS.md"), "a") as fh: fh.write(proj)
        if not a.toy: S.write("driver_finished", "all five runs complete and audited", runs_complete=len(a.seeds), runs_audited=len(a.seeds), driver_pid=None)
        log("driver FINISHED: all runs complete and audited"); return 0
    except DriverCeiling as e:
        log(f"CEILING: {e}"); S.write("driver_stopped", str(e), stopped_reason="CEILING", driver_pid=None); return 2
    except Exception as e:
        tb = traceback.format_exc(); log(f"CRASH: {e}\n{tb}")
        reason = "UNRESOLVED_SOLVE" if "UnresolvedSolve" in tb or "unresolved solve" in str(e) else "CRASH"
        if not a.toy: S.write("driver_stopped", f"{reason}: {e}", stopped_reason=reason, driver_pid=None)
        return 2


if __name__ == "__main__":
    sys.exit(main())
