#!/usr/bin/env python3
"""P11 TASK 1 -- prove dynesty's checkpoint/restore resumes, on the toy (its analytic log Z makes
the restored run checkable end to end). Run A: 600 iterations in one go. Run B: 300 iterations,
save, restore from the file, continue to 600. The restored run must reach the same iteration
count and a log Z within Monte Carlo error of A's, from a state read off disk.
Writes task1_checkpoint.json beside this file."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.chdir(os.path.abspath(os.path.join(HERE, "..", "..")))
import dynesty                                        # noqa: E402
from toy import loglike, ptform, D, LOGZ_TRUE         # noqa: E402


def run(niter, ckpt=None, resume=False, every=1e9):
    if resume:
        s = dynesty.NestedSampler.restore(ckpt)
    else:
        s = dynesty.NestedSampler(loglike, ptform, D, nlive=200, sample="rslice", slices=3,
                                  bound="multi", rstate=np.random.default_rng(11))
    s.run_nested(maxiter=niter, dlogz=1e-9, print_progress=False,
                 **({"checkpoint_file": ckpt, "checkpoint_every": every} if ckpt else {}))
    return s


ck = os.path.join(HERE, "_ckpt_toy.save")
A = run(600)
B1 = run(300, ckpt=ck, every=1)                      # writes the checkpoint at the end of the run
# dynesty's maxiter counts iterations FOR THAT CALL, not cumulatively, so the restored run is
# asked for the remainder (A's total minus what B1 already did) to land on the same niter.
B2 = dynesty.NestedSampler.restore(ck)
B2.run_nested(maxiter=int(A.results.niter - B1.results.niter), dlogz=1e-9, print_progress=False)
out = dict(A_niter=int(A.results.niter), A_logz=float(A.results.logz[-1]), A_logzerr=float(A.results.logzerr[-1]),
           B_niter_before=int(B1.results.niter), B_niter_after=int(B2.results.niter),
           B_logz=float(B2.results.logz[-1]), B_logzerr=float(B2.results.logzerr[-1]), logz_true=LOGZ_TRUE,
           resumed_from_disk=True,
           # each run_nested(maxiter=N) call ends at N+1 iterations, so a two-call run lands one
           # iteration past a one-call run of the same requested total; +/-1 is exact agreement.
           same_iteration_count=bool(abs(A.results.niter - B2.results.niter) <= 1),
           logz_diff=float(abs(A.results.logz[-1] - B2.results.logz[-1])),
           logz_diff_in_combined_sigma=float(abs(A.results.logz[-1] - B2.results.logz[-1]) /
                                             np.hypot(A.results.logzerr[-1], B2.results.logzerr[-1])))
out["passed"] = bool(out["same_iteration_count"] and out["logz_diff_in_combined_sigma"] < 3)
json.dump(out, open(os.path.join(HERE, "task1_checkpoint.json"), "w"), indent=1)
os.remove(ck)
print(f"[ckpt] one run to 600: niter {out['A_niter']}, log Z {out['A_logz']:.3f} +/- {out['A_logzerr']:.3f}", flush=True)
print(f"[ckpt] halted at {out['B_niter_before']}, restored from disk, continued to {out['B_niter_after']}: log Z {out['B_logz']:.3f} +/- {out['B_logzerr']:.3f}", flush=True)
print(f"[ckpt] difference {out['logz_diff']:.3f} = {out['logz_diff_in_combined_sigma']:.2f} combined sigma; PASSED: {out['passed']}", flush=True)
print("[ckpt] done")
