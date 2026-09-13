#!/usr/bin/env python3
"""T2 -- the approved revised target as the sampler sees it.

Everything the strain config switches on (f_metab removed, infeasibility at -inf) is read by
`_build_gasflux_ctx` from strains/eciML1515/gas_exchange.yaml, so this module asks the CONTEXT for
its spec list rather than assembling one (unlike P16's reduced.py). It then:
  * pins dTm at 0.0 (the P16/P17 conditioning; D0) -- `expand` re-inserts it;
  * in the VALIDATION configuration appends the two diagnostic coordinates (`diagnostic_coords`),
    proven inert in TASK 3; production is the same without them;
  * defines `loglike(theta_sampled)` for the pool workers: -inf passes through to dynesty as -inf
    (the approved zero-likelihood rule), and an UnresolvedSolve is RECORDED and RE-RAISED -- never a
    number (D0).
Pool workers are initialised with `_gwinit(payload)`; the payload's `spec_options` carries the
diagnostic coordinates so every worker's _GSPECS matches this module's SPECS."""
import os, sys, json, time, hashlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "reports", "P6_convergence"), HERE):
    if p not in sys.path: sys.path.insert(0, p)
from etcgem import calibration_multi as CM                        # noqa: E402
from etcgem.calibration_multi import _build_gasflux_ctx, gasflux_log_likelihood   # noqa: E402
from etcgem.gasflux import UnresolvedSolve                        # noqa: E402
from p6_fits import FITS                                          # noqa: E402

FIT = [f for f in FITS if f[0] == "D_NLDM"][0]
LABEL, CFG, MEDIUM, TABLE, OTU, C_MAX, ETC, PROTONS, FIT_K = FIT
PAYLOAD = dict(strain="eciML1515", medium=MEDIUM, experiment=f"gasflux_config{CFG}", table=TABLE, otu=OTU,
               c_max=C_MAX, etc_table=ETC, apply_protons=PROTONS, fit_clearance=FIT_K)
# the validation configuration's two diagnostic coordinates (D0): f_metab's ORIGINAL prior, and Beta(3,1)
DIAGNOSTICS = [dict(name="f_metab_diag", space="add", prior="normal", scale=0.03, loc=0.28, lo=0.15, hi=0.45),
               dict(name="beta31_diag", space="add", prior="beta31", scale=1.0, loc=0.0, lo=0.0, hi=1.0)]
FIXED_NAME, FIXED_SAMPLED = "dTm", 0.0


def payload(validation):
    return dict(PAYLOAD, spec_options=(dict(diagnostic_coords=DIAGNOSTICS) if validation else None))


def build(validation, timeout=30):
    """(ctx, full_specs) for this process, from the strain config + (optionally) the diagnostics."""
    ctx, specs = _build_gasflux_ctx(**payload(validation), timeout=timeout)
    return ctx, specs


class Target:
    """index bookkeeping for one configuration: full specs (as the likelihood takes) vs sampled specs."""
    def __init__(self, full_specs):
        self.full = list(full_specs); self.full_names = [s.name for s in self.full]
        assert "f_metab" not in self.full_names, "f_metab is still sampled: remove_inactive is not ON"
        self.fixed_idx = self.full_names.index(FIXED_NAME)
        self.sampled = [s for i, s in enumerate(self.full) if i != self.fixed_idx]
        self.names = [s.name for s in self.sampled]; self.D = len(self.sampled)
        self.physical = [n for n in self.names if not n.endswith("_diag")]

    def expand(self, th):
        th = np.asarray(th, float); t = np.empty(len(self.full), float)
        t[:self.fixed_idx] = th[:self.fixed_idx]; t[self.fixed_idx] = FIXED_SAMPLED; t[self.fixed_idx + 1:] = th[self.fixed_idx:]
        return t

    def reduce(self, full):
        return np.delete(np.asarray(full, float), self.fixed_idx)

    def config_hash(self):
        h = hashlib.sha256()
        for s in self.full: h.update(repr((s.name, s.space, s.prior, s.scale, s.loc, s.lo, s.hi, s.pert)).encode())
        h.update(f"fixed:{FIXED_NAME}={FIXED_SAMPLED}".encode()); return h.hexdigest()


# ---- the worker-side likelihood -------------------------------------------------------------------
_COUNT = {"calls": 0, "ninf": 0, "retry": 0}
_RUN_DIR = os.environ.get("T2_RUN_DIR", "")
_TARGET = None


def _target():
    global _TARGET
    if _TARGET is None: _TARGET = Target(CM._GSPECS)
    return _TARGET


def _flush_counter(force=False):
    if _RUN_DIR and (force or _COUNT["calls"] % 200 == 0):
        p = os.path.join(_RUN_DIR, f"counter_{os.getpid()}.json"); tmp = p + ".tmp"
        json.dump(dict(_COUNT, pid=os.getpid(), t=time.time()), open(tmp, "w")); os.replace(tmp, p)


def loglike(theta_sampled):
    """called in a pool worker after _gwinit; -inf stays -inf; UnresolvedSolve is recorded and re-raised."""
    t = _target(); th = t.expand(theta_sampled); _COUNT["calls"] += 1
    try:
        ll = gasflux_log_likelihood(th, CM._GCTX, CM._GSPECS)
    except UnresolvedSolve as e:
        rec = dict(theta_sampled=np.asarray(theta_sampled, float).tolist(), theta_full=th.tolist(), pid=os.getpid(),
                   time=time.time(), temperature=getattr(e, "temperature", None), statuses=getattr(e, "statuses", None), msg=str(e))
        if _RUN_DIR:
            with open(os.path.join(_RUN_DIR, "unresolved.jsonl"), "a") as fh: fh.write(json.dumps(rec) + "\n")
        _flush_counter(True); raise
    if ll == -np.inf: _COUNT["ninf"] += 1
    _flush_counter()
    return float(ll)          # -inf is a float; dynesty 3.1 accepts it (D0)


def sha_file(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
