#!/usr/bin/env python3
"""to_strain_inputs.py -- build a strains/<name>/ input skeleton for one Candidozyma
species from the standalone Candidas `gem/` pipeline's committed tables.

This is the K1 PORT converter. It implements NOTHING of the model: it only
re-expresses the standalone's inputs in the layout `src/etcgem` already reads for
the *M. maripaludis* `smoment_gem` provider. Every choice below is the standalone's
choice, taken from `gem/18_build_etcgem_tpc.py`, and is commented as such so that
K2 (the same strains under the core's own thermal form) can change it deliberately.

Reads (all under $CANDIDAS_ROOT/gem/):
    models/<xml>                       the species' SBML (for GPRs and subsystems)
    tables/enzyme_mw_<sp>.csv          gene -> length_aa, MW_kDa (08_enzyme_mw.py)
    tables/kcat_reaction_<sp>.csv      reaction -> kcat_per_s, best_gene (11_aggregate_kcat.py)
    tables/thermal_topt.csv            "<sp>|<gene>" -> pred_topt  (14_run_seq2topt_seq2tm.sh)
    tables/thermal_tm.csv              "<sp>|<gene>" -> pred_tm    (as above)
    tables/measured_tpc_honest.csv     measured growth TPC          (17_build_measured_tpc.py)
    inputs/<medium>.csv                the YMS exchange map

Writes (under strains/<name>/):
    model/<xml>                        copied verbatim
    media/<medium>.csv                 copied verbatim (source of truth for set_medium)
    dltkcat/kcat_table.csv             rxn_id, mw_kDa, kcat_s, source, group
    thermal/enzyme_thermal_params.csv  rxn_id, Topt, Tm, Length, T90, dCpt, source, best_gene
    thermal/measured_tpc.csv           the species' rows of the measured curve
    dltkcat/converter_report.json      the counts printed below, for the record

The reaction set written is EXACTLY the standalone's `precompute()` term set:

    skip r if  r.id in EX (id starts EX_/Drain, or r.boundary)
            or 'iomass' in r.id
            or r has no genes
            or none of r's genes has a molecular weight

    mw_kDa  = MEAN MW over the reaction's genes that have one   (statistics.mean)
    kcat_s  = kcat_reaction_<sp>.csv, else 13.7 s^-1            (the standalone default)
    Topt/Tm = the best_gene's Seq2Topt/Seq2Tm prediction, else the SPECIES MEDIAN
              over every prediction for that species (not just the model's genes)

Topt and Tm are written in KELVIN because `providers.apply_thermal_params` expects
K (the MRes/methanogen convention); the predictors report degrees Celsius.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys

import pandas as pd

# The standalone's species map (gem/gempaths.py SP) plus this repository's strain
# folder name for each. Both draft models are KOfam reconstructions on the iRV973
# scaffold, not curated models -- their strain.yaml says so.
SPECIES = {
    "auris": dict(strain="cauris_iRV973", model="auris_iRV973_rekeyed.xml",
                  medium="medium_iRV973_auris.csv"),
    "haemulonii": dict(strain="chaemulonii_draft", model="haemulonii_draft.xml",
                       medium="medium_iRV973_auris.csv"),
    "duobushaemulonii": dict(strain="cduobushaemulonii_draft", model="duobushaemulonii_draft.xml",
                             medium="medium_iRV973_auris.csv"),
    "parapsilosis": dict(strain="cparapsilosis_iDC1003", model="parapsilosis_iDC1003.xml",
                         medium="medium_iDC1003_parapsilosis.csv"),
}

DEFAULT_KCAT_S = 13.7        # standalone: reactions with no DLKcat kcat
DCP_PRIOR_KJ = -4.0          # shared dCp prior (methanogen convention), kJ/mol/K
K0 = 273.15


def _git_commit(root: str) -> str:
    try:
        return subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def convert(species: str, candidas_root: str, repo_root: str, strain: str | None = None,
            copy_model: bool = True) -> dict:
    meta = SPECIES[species]
    strain = strain or meta["strain"]
    gem = os.path.join(candidas_root, "gem")
    tables = os.path.join(gem, "tables")
    sdir = os.path.join(repo_root, "strains", strain)
    for sub in ("model", "media", "thermal", "dltkcat", "outputs"):
        os.makedirs(os.path.join(sdir, sub), exist_ok=True)
        keep = os.path.join(sdir, sub, ".gitkeep")
        if not os.listdir(os.path.join(sdir, sub)) and not os.path.exists(keep):
            open(keep, "w").close()

    import cobra
    model_src = os.path.join(gem, "models", meta["model"])
    model = cobra.io.read_sbml_model(model_src)

    mw_df = pd.read_csv(os.path.join(tables, f"enzyme_mw_{species}.csv"))
    mw = {r["gene"]: float(r["MW_kDa"]) for _, r in mw_df.iterrows()}
    length = {r["gene"]: float(r["length_aa"]) for _, r in mw_df.iterrows()}
    kc = pd.read_csv(os.path.join(tables, f"kcat_reaction_{species}.csv"))
    kmap = {r["reaction"]: (float(r["kcat_per_s"]), r["best_gene"]) for _, r in kc.iterrows()}

    topt = pd.read_csv(os.path.join(tables, "thermal_topt.csv"))
    tm = pd.read_csv(os.path.join(tables, "thermal_tm.csv"))
    for df in (topt, tm):
        df["g"] = df["id"].str.split("|").str[1]
        df["sp"] = df["id"].str.split("|").str[0]
    tov = {r.g: float(r.pred_topt) for r in topt[topt.sp == species].itertuples()}
    tmv = {r.g: float(r.pred_tm) for r in tm[tm.sp == species].itertuples()}
    # species medians, over EVERY prediction for the species (standalone therm_maps)
    med_to = statistics.median(tov.values()) if tov else 35.0
    med_tm = statistics.median(tmv.values()) if tmv else 54.0

    EX = {r.id for r in model.reactions
          if r.id.startswith(("EX_", "Drain")) or r.boundary}

    kcat_rows, therm_rows = [], []
    n_total = len(model.reactions)
    n_skip_ex = n_skip_biomass = n_skip_nogene = n_skip_nomw = 0
    n_kcat = n_default = n_topt = n_tm = n_median = 0
    unmatched_best_gene = []
    for r in model.reactions:
        if r.id in EX:
            n_skip_ex += 1
            continue
        if "iomass" in r.id:
            n_skip_biomass += 1
            continue
        if not r.genes:
            n_skip_nogene += 1
            continue
        genes = [g.id for g in r.genes if g.id in mw]
        if not genes:
            n_skip_nomw += 1
            continue
        mw_mean = statistics.mean(mw[g] for g in genes)
        base = kmap.get(r.id)
        if base is not None:
            kcat_s, best_gene = base
            source = "dlkcat"
            n_kcat += 1
        else:
            kcat_s, best_gene = DEFAULT_KCAT_S, None
            source = "default_13.7"
            n_default += 1
        kcat_rows.append(dict(rxn_id=r.id, mw_kDa=round(mw_mean, 6), kcat_s=kcat_s,
                              source=source, group=(r.subsystem or "")))
        has_to = best_gene in tov
        has_tm = best_gene in tmv
        n_topt += int(has_to)
        n_tm += int(has_tm)
        if best_gene is not None and not (has_to and has_tm):
            unmatched_best_gene.append((r.id, str(best_gene)))
        t_src = "seq2topt_seq2tm" if (has_to and has_tm) else "median"
        if t_src == "median":
            n_median += 1
        # Length: the best_gene's sequence length where there is one, else the mean
        # over the reaction's genes (unused by the phenomenological form; written so
        # K2's unfolding form needs no new inputs).
        if best_gene in length:
            L = length[best_gene]
        else:
            L = statistics.mean(length[g] for g in genes)
        therm_rows.append(dict(
            rxn_id=r.id,
            Topt=round(tov.get(best_gene, med_to) + K0, 6),
            Tm=round(tmv.get(best_gene, med_tm) + K0, 6),
            Length=int(round(L)),
            T90="",
            dCpt=DCP_PRIOR_KJ * 1000.0,
            source=t_src,
            best_gene=(best_gene if best_gene is not None else ""),
        ))

    pd.DataFrame(kcat_rows).to_csv(os.path.join(sdir, "dltkcat", "kcat_table.csv"), index=False)
    pd.DataFrame(therm_rows).to_csv(
        os.path.join(sdir, "thermal", "enzyme_thermal_params.csv"), index=False)

    # measured growth TPC, taken verbatim from 17_build_measured_tpc.py's output
    hon = pd.read_csv(os.path.join(tables, "measured_tpc_honest.csv"))
    sub = hon[hon.species == species].copy().sort_values("T")
    sub = sub.rename(columns={"T": "T_C", "mu_honest": "mu"})[
        ["T_C", "mu", "n", "n_alive"]]
    sub.to_csv(os.path.join(sdir, "thermal", "measured_tpc.csv"), index=False)

    if copy_model:
        shutil.copy2(model_src, os.path.join(sdir, "model", meta["model"]))
    shutil.copy2(os.path.join(gem, "inputs", meta["medium"]),
                 os.path.join(sdir, "media", meta["medium"]))

    report = dict(
        species=species, strain=strain, model=meta["model"], medium=meta["medium"],
        candidas_commit=_git_commit(candidas_root),
        reactions_in_model=n_total,
        skipped_exchange_or_boundary=n_skip_ex, skipped_biomass=n_skip_biomass,
        skipped_no_gene=n_skip_nogene, skipped_no_mw=n_skip_nomw,
        enzyme_costed_reactions=len(kcat_rows),
        with_dlkcat_kcat=n_kcat, at_default_kcat_13_7=n_default,
        with_predicted_Topt=n_topt, with_predicted_Tm=n_tm,
        at_species_median_thermal=n_median,
        species_median_Topt_C=round(med_to, 4), species_median_Tm_C=round(med_tm, 4),
        genes_with_mw=len(mw), genes_with_Topt=len(tov), genes_with_Tm=len(tmv),
        kcat_table_rows_in_source=len(kc),
        best_gene_without_prediction=sorted({g for _, g in unmatched_best_gene}),
        measured_tpc_rows=len(sub),
    )
    with open(os.path.join(sdir, "dltkcat", "converter_report.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--species", required=True, choices=sorted(SPECIES) + ["all"])
    ap.add_argument("--candidas-root", default=os.environ.get("CANDIDAS_ROOT"),
                    help="path to the Candidas repository (default $CANDIDAS_ROOT)")
    ap.add_argument("--repo-root", default=os.getcwd())
    ap.add_argument("--strain", default=None, help="override the strain folder name")
    ap.add_argument("--no-copy-model", action="store_true")
    a = ap.parse_args(argv)
    if not a.candidas_root:
        ap.error("--candidas-root (or $CANDIDAS_ROOT) is required")
    todo = sorted(SPECIES) if a.species == "all" else [a.species]
    for sp in todo:
        rep = convert(sp, a.candidas_root, a.repo_root, a.strain,
                      copy_model=not a.no_copy_model)
        print(json.dumps(rep, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
