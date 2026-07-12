#!/usr/bin/env python
"""Generate the per-enzyme thermal parameter table for the Synechocystis 6803 etc-GEM
(P2 thermal layer), keyed by reaction id.

Route (documented, house-consistent with the methanogen M3):
- Topt: MESOPHILE PRIOR. The Li-Engqvist per-enzyme optimum predictor is NOT runnable
  in-session and 6803 is absent from the precomputed E. coli/Li tables, so — exactly as
  for M. maripaludis — Topt is drawn from a mesophile-enzyme prior N(mean, sd). 6803 is a
  mesophile (growth optimum ~35 C, Zavrel 2015), so we reuse the SAME generic mesophile
  enzyme-Topt prior as the methanogen build (mean 39.3 C, sd 10), i.e. the enzyme optima
  sit a little above the organism's growth optimum, as for a typical mesophile. The
  rising-limb Ea, breadth and CTmax then EMERGE and are compared a-priori to Zavrel 2015.
  Li-Engqvist / a cyanobacterial Topt predictor is the stated future upgrade; P3's
  dTopt/topt_scale refine it.
- Tm: MESOPHILE PRIOR N(55.6 C, 7.59), the E. coli meltome mean + spread, INDEPENDENT of
  Topt (6803 absent from the Meltome Atlas; mesophile stability regime). P3's dTm refines.
- Length: generic bacterial-protein-length prior N(335, 134) (the methanogen UniProt-length
  distribution) — enters only the dHTH/dSTS/dCpu solve when T90 is absent; a secondary knob.
- dCpt: literature MMRT transition-state prior -4000 J/mol/K (Hobbs 2013), constant, NOT
  fitted -> the activation energy emerges.

Deterministic (fixed seed) so the committed CSV is reproducible. Keyed by rxn_id to match
the route-B cost carriers extracted from iSynCJ816_STAR by providers.from_gecko.
"""
import logging, warnings, os
logging.getLogger("cobra").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
STRAIN = os.path.dirname(HERE)
STAR = os.path.join(STRAIN, "model", "ecmodel_iSynCJ816_STAR", "iSynCJ816_STAR.xml")
OUT = os.path.join(HERE, "enzyme_thermal_params.csv")

# --- mesophile prior parameters (K), reused verbatim from the methanogen M3 build ---
TOPT_MEAN_K = 273.15 + 39.3     # generic mesophile enzyme-optimum mean
TOPT_SD_K = 10.0
TM_MEAN_K = 273.15 + 55.6       # E. coli meltome mean (independent of Topt)
TM_SD_K = 7.59
LEN_MEAN, LEN_SD = 335.0, 134.0
DCPT = -4000.0                  # J/mol/K literature MMRT prior
MIN_TM_ABOVE_TOPT = 3.0         # K, keep native fraction ~1 at Topt
SEED = 6803


def prot_pool_consumers(model, pool="prot_pool"):
    """Reaction ids that consume the sMOMENT prot_pool (the route-B cost carriers)."""
    out = []
    for r in model.reactions:
        if r.id.startswith("EX_") or r.id == "ER_pool_TG_":
            continue
        for m in r.metabolites:
            if m.id == pool and r.metabolites[m] < 0:
                out.append(r.id)
                break
    return out


def main():
    import cobra
    from src.etcgem.providers import _read_sbml_safe  # noqa
    model = _read_sbml_safe(STAR)
    rxns = prot_pool_consumers(model)
    rng = np.random.default_rng(SEED)
    n = len(rxns)
    topt = rng.normal(TOPT_MEAN_K, TOPT_SD_K, n)
    tm = rng.normal(TM_MEAN_K, TM_SD_K, n)
    length = np.clip(rng.normal(LEN_MEAN, LEN_SD, n), 80.0, 1500.0)
    # enforce Tm >= Topt + margin (native fraction ~1 at Topt)
    tm = np.maximum(tm, topt + MIN_TM_ABOVE_TOPT)
    # mild physical clip on optima (avoid pathological cold/hot enzymes)
    topt = np.clip(topt, 273.15 + 10.0, 273.15 + 55.0)
    df = pd.DataFrame({
        "rxn_id": rxns,
        "Topt": np.round(topt, 3),
        "Tm": np.round(tm, 3),
        "Length": np.round(length).astype(int),
        "T90": "",
        "dCpt": DCPT,
        "topt_source": "mesophile_prior",
    })
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {n} reactions")
    print(f"  Topt mean {topt.mean()-273.15:.2f} C (sd {topt.std():.2f}); "
          f"Tm mean {tm.mean()-273.15:.2f} C (sd {tm.std():.2f}); "
          f"Length mean {length.mean():.0f}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(STRAIN, "..", "..")))
    main()
