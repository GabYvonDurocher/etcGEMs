#!/usr/bin/env python3
"""P10 TASK 4 -- INFORMATION ONLY: do the K5 proton-supply figures for the four Candida strains
change if the audited solution is the pfba vertex instead of the solver's growth-optimal one?
K5's construction exactly (candida_B5_respire, 40 C, kcat_scale 1), the audit run on (a) the
plain optimum, as K5 did, and (b) cobra's pfba solution at the same optimum. Nothing adopted;
the tie-break stays OFF for these strains. Writes task4_candida_pfba.csv beside this file."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); os.chdir(ROOT)
from etcgem.config import build_provider, resolve          # noqa: E402
from etcgem.sink_audit import audit_coupling_ion           # noqa: E402
from etcgem.tpc import apply_state                         # noqa: E402
from etcgem.enzyme_cost import Perturbation                # noqa: E402
from cobra.flux_analysis import pfba                       # noqa: E402

STRAINS = [("cauris_iRV973", "candida_B5_respire", 40.0), ("chaemulonii_draft", "candida_B5_respire", 40.0),
           ("cduobushaemulonii_draft", "candida_B5_respire", 40.0), ("cparapsilosis_iDC1003", "candida_B5_respire", 40.0)]
KEYS = ("growth", "atp_synthase_draw", "redox_translocated", "redox_in_compartment", "chain_supplies_fraction", "chain_supplies_fraction_incl_chemistry", "carrier_supplies_fraction")
rows = []
for strain, exp, T in STRAINS:
    cfg = resolve(strain, exp); pm = build_provider(cfg); m = pm.ec.model
    apply_state(pm.ec, T, Perturbation())
    sol = m.optimize(); a = audit_coupling_ion(pm, sol)
    with m:
        sol_p = pfba(m)
    b = audit_coupling_ion(pm, sol_p)
    for k in KEYS:
        rows.append(dict(strain=strain, quantity=k, plain_optimum=a.get(k), pfba=b.get(k), delta=(b.get(k) - a.get(k)) if isinstance(a.get(k), (int, float)) and isinstance(b.get(k), (int, float)) else None))
    print(f"[candida] {strain:24s} growth {a['growth']:.4f} -> {b['growth']:.4f}; chain_supplies_fraction {a['chain_supplies_fraction']:.3f} -> {b['chain_supplies_fraction']:.3f}; incl. chemistry {a['chain_supplies_fraction_incl_chemistry']:.3f} -> {b['chain_supplies_fraction_incl_chemistry']:.3f}", flush=True)
pd.DataFrame(rows).to_csv(os.path.join(HERE, "task4_candida_pfba.csv"), index=False); print("[candida] done")
