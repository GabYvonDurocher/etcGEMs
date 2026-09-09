#!/usr/bin/env python3
"""yeast_model.py -- load Li et al.'s deposited ecYeast7 GECKO model and present it to this
repository's audit.

Y1 PART A. Two problems stand between the deposit and cobrapy, and both are solved here.

1. THE PICKLES DO NOT LOAD. `models/aerobic.pkl` and `models/anaerobic.pkl` are cobra 0.15.3
   model objects pickled in 2020. Unpickling them under cobra 0.31 fails inside
   `Configuration.__setstate__` (no attribute `problem`, then `KeyError: 'tolerances'`) because
   the Configuration object's state changed shape. Reviving them means shimming a five-years-old
   private API, which is exactly the kind of format archaeology Y1 was told not to spend a day
   on. The deposited `.mat` files carry the same models and are used instead.

2. THE .mat FILES NEED A TRIM. Several GECKO-specific fields are sized to a SUBSET of the model
   (909 `genes` against 764 `geneNames`; `rxnECnumbers` and `rxnUniprots` shorter than `rxns`),
   and cobra zips them against the full lists and overruns. The shim keeps only the fields that
   DEFINE THE LINEAR PROGRAM and the identifiers needed to read it -- stoichiometry, bounds,
   objective, ids, names, compartments, GPR rules -- and drops GECKO's annotation extras
   (`geneNames`, `enzymes`, `genes2`, `MWs`, `sequence`, `pathways`, `rxnUniprots`,
   `rxnECnumbers`, `rxnKcats`, `concs`). None of those carries stoichiometry, a bound or an
   objective coefficient.

   `verify_fidelity` then checks everything the shim could have broken -- S, lb, ub, c and the
   reaction and metabolite id lists -- against the raw MATLAB struct, so the claim that the trim
   is inert is tested rather than asserted.

The audit takes a ProvidedModel with `.ec.model` and `.ec.table`, and uses the table only to
decide which reactions are ENZYME-COSTED. In a GECKO model that is structural rather than a
matter of bookkeeping: a reaction is costed exactly when it consumes a `prot_*` pseudo-
metabolite. `YeastPM` derives the costed set that way, so nothing about cost is asserted about
their model -- it is read off it.
"""
from __future__ import annotations

import logging
import os
import warnings
from dataclasses import dataclass

import numpy as np
import scipy.io as sio
from cobra.io.mat import from_mat_struct

logging.getLogger("cobra").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# The fields that define the LP plus the identifiers needed to read it. Everything else in the
# deposited struct is GECKO annotation, and some of it is ragged.
STRUCTURAL = ("rxns", "mets", "S", "rev", "lb", "ub", "c", "b", "rules", "genes",
              "rxnGeneMat", "grRules", "rxnNames", "metNames", "metFormulas",
              "comps", "compNames", "metComps", "description")

# The three models deposited in BayesianGEM/models/. `aerobic.pkl` and `anaerobic.pkl` are
# pickles of two of them; which is which is established in task_a_load.py, not assumed here.
DEPOSITED = ("ecYeast7_v1.0_batch.mat",
             "ecYeast7_v1.0_batch_minimal_thermo.mat",
             "ecYeast7_v1.0_batch_minimal_thermo_anaerobic.mat")


def load(path):
    """Load one deposited .mat. Returns (cobra model, raw MATLAB struct)."""
    d = sio.loadmat(path)
    # the anaerobic deposit carries a scalar `GAM` beside the model, so pick the struct
    cands = [k for k in d if not k.startswith("__") and d[k].dtype.names is not None]
    if len(cands) != 1:
        raise ValueError(f"{path}: expected one model struct, found {cands}")
    st = d[cands[0]]
    keep = [f for f in st.dtype.names if f in STRUCTURAL]
    trimmed = np.zeros((1, 1), dtype=[(f, object) for f in keep])
    for f in keep:
        trimmed[f][0, 0] = st[f][0, 0]
    m = from_mat_struct(trimmed, model_id=os.path.basename(path).replace(".mat", ""))
    return m, st


def verify_fidelity(m, st):
    """Every check the shim could have broken, against the raw MATLAB struct."""
    out = {}
    rxns = [str(x[0][0]) for x in st["rxns"][0, 0]]
    mets = [str(x[0][0]) for x in st["mets"][0, 0]]
    out["n_rxns"] = [len(m.reactions), len(rxns), len(m.reactions) == len(rxns)]
    out["n_mets"] = [len(m.metabolites), len(mets), len(m.metabolites) == len(mets)]
    out["rxn_ids_identical"] = [r.id for r in m.reactions] == rxns
    out["met_ids_identical"] = [x.id for x in m.metabolites] == mets
    lb = np.asarray(st["lb"][0, 0]).ravel()
    ub = np.asarray(st["ub"][0, 0]).ravel()
    c = np.asarray(st["c"][0, 0]).ravel()
    mlb = np.array([r.lower_bound for r in m.reactions])
    mub = np.array([r.upper_bound for r in m.reactions])
    mc = np.array([r.objective_coefficient for r in m.reactions])
    BIG = 1000.0     # cobra clamps MATLAB's +-Inf/1e30 to its own default; compare on the clip
    out["lb_max_abs_diff"] = float(np.nanmax(np.abs(np.clip(lb, -BIG, BIG) - np.clip(mlb, -BIG, BIG))))
    out["ub_max_abs_diff"] = float(np.nanmax(np.abs(np.clip(ub, -BIG, BIG) - np.clip(mub, -BIG, BIG))))
    out["c_max_abs_diff"] = float(np.nanmax(np.abs(c - mc)))
    S = st["S"][0, 0]
    out["S_nnz_struct"] = int(S.nnz if hasattr(S, "nnz") else np.count_nonzero(S))
    out["S_nnz_model"] = int(sum(len(r.metabolites) for r in m.reactions))
    out["objective_rxns_struct"] = [rxns[i] for i in np.nonzero(c)[0]]
    out["objective_rxns_model"] = sorted(r.id for r in m.reactions
                                         if abs(r.objective_coefficient) > 0)
    return out


@dataclass
class _Entry:
    rxn_id: str


class _EC:
    def __init__(self, model, costed_ids):
        self.model = model
        self.table = [_Entry(r) for r in sorted(costed_ids)]


class YeastPM:
    """Minimal ProvidedModel stand-in: model + costed table + biomass reaction.

    Costed = consumes a `prot_*` pseudo-metabolite, which is GECKO's own definition."""

    def __init__(self, model, biomass_rxn=None):
        costed = {r.id for r in model.reactions
                  if any(mm.id.startswith("prot_") and c < 0 for mm, c in r.metabolites.items())}
        self.ec = _EC(model, costed)
        self.name = model.id
        self.biomass_rxn = biomass_rxn or _guess_biomass(model)
        self.T0 = 303.15

    @property
    def costed_ids(self):
        return {e.rxn_id for e in self.ec.table}


def _guess_biomass(model):
    for r in model.reactions:
        if abs(r.objective_coefficient) > 0:
            return r.id
    return None
