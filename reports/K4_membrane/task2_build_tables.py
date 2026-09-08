#!/usr/bin/env python3
"""task2_build_tables.py -- K4 TASK 2: build strains/<name>/etc/complexes.csv for the four
Candida species, and record where every single value came from.

SOURCING IS THE POINT OF THIS SCRIPT, not a footnote to it. Every value carries a provenance
class, and the script prints the breakdown so that a table which is mostly "taken from E. coli"
cannot be mistaken for one that is measured. The classes, in decreasing strength:

    measured_species    measured in THIS Candida species
    measured_fungus     measured in another named fungus
    structure_fungus    derived from a solved structure OF A FUNGUS, as the membrane-plane
                        cross-section of the complex oriented in the bilayer (OPM)
    structure           the same, from a non-fungal structure
    ecoli               taken from E. coli (Szenk 2017 / Bekker 2009), via
                        strains/eciML1515/etc/complexes.csv
    model               read off this model's own encoding (reaction ids, proton stoichiometry)
    predictor           a sequence predictor's output (DLKcat), i.e. the channel A1 found has
                        no demonstrated per-protein validity in this regime
    assumed             none of the above

WHAT THE SEARCH FOUND, stated before the table so no one has to infer it.

There is **no published membrane footprint, turnover or abundance for any ETC complex of any
Candida species**, and no fungal equivalent of Szenk 2017 (which tabulates E. coli footprints
directly). What DOES exist is solved structures of the fungal complexes, so the area column can
be derived from fungal structures rather than transferred from E. coli -- Yarrowia lipolytica
complex I and Saccharomyces cerevisiae complexes II, III, IV and V. Those are the values used.
They are `structure_fungus`, not `measured_species`: they are the same in all four Candida
models because they come from other fungi, and one Candida structure that does exist
(C. albicans bc1, 7RJA) differs from the S. cerevisiae one only by a missing subunit.

The turnover column has no such rescue: **no kcat has been measured for any ETC complex of any
Candida**, so every value there is taken from E. coli. And there is no published mitochondrial
inner-membrane area for any Candida, nor an inner:outer membrane area ratio for any fungus,
which is what makes A_ETC a free knob (see the report).

Run from the project root:

    python3 reports/K4_membrane/task2_build_tables.py

Writes strains/<name>/etc/complexes.csv (four files) and task2_sourcing.csv beside this file.
"""
from __future__ import annotations

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

# ---------------------------------------------------------------------------
# THE VALUES, each with its provenance and its citation.
# ---------------------------------------------------------------------------
# area_nm2: membrane-plane footprint of one complex.
# kcat_s  : turnover.
# Both are IDENTICAL ACROSS THE FOUR SPECIES, because nothing species-specific exists to put
# there. That is stated in the file header of every table and is the finding TASK 4 leads with.
COMPLEX_DATA = {
    "complex I": dict(
        area_nm2=137.4, area_class="structure_fungus",
        area_note="Membrane-arm cross-section in the bilayer plane of respiratory complex I "
                  "of YARROWIA LIPOLYTICA, PDB 6RFR, oriented in the membrane by OPM (Lomize "
                  "et al. 2012 NAR 40:D370). Computed from the structure, cross-checked "
                  "against the stated arm dimensions of Zickermann et al. 2015 Science "
                  "347:44 and Wu et al. 2016 Cell 167:1598 (computed 19.4 nm arm length "
                  "against a stated 180 A; 8.3 nm width against a stated 70 A). "
                  "AMBIGUITY WORTH KNOWING: the three iRV973-derived models encode this "
                  "reaction NON-ELECTROGENICALLY (TASK 1), which is the behaviour of a "
                  "single-subunit alternative NADH dehydrogenase (Ndi1/Nde1), not of "
                  "complex I. An Ndi1 monomer's in-bilayer cross-section is 3.0 nm^2, 45x "
                  "smaller. The complex I value is used because the reaction carries "
                  "EC 7.1.1.2 and C. parapsilosis encodes it as proton-pumping; if the "
                  "enzyme is really Ndi1 this row is wrong by a factor of 45.",
        kcat_s=200.0, kcat_class="ecoli",
        kcat_note="Szenk 2017 / BRENDA physiological midpoint for NDH-I, as "
                  "strains/eciML1515/etc/complexes.csv uses it. NO kcat has been measured "
                  "for complex I of any Candida species, and none for Ndi1/Nde1 either. The "
                  "models' own per-species DLKcat values (61.3 / 37.3 / 50.7 / 5.7 s^-1) are "
                  "deliberately NOT used -- see the report."),
    "complex II": dict(
        area_nm2=15.4, area_class="structure_fungus",
        area_note="Succinate dehydrogenase of SACCHAROMYCES CEREVISIAE, PDB 9KPS, in-bilayer "
                  "cross-section (a second yeast deposition, 9QDL, gives 14.4 nm^2; the pig "
                  "enzyme, 1ZOY, gives 10.6, which is the value Szenk's E. coli row of "
                  "10 nm^2 also sits at).",
        kcat_s=100.0, kcat_class="ecoli",
        kcat_note="Szenk 2017 / BRENDA physiological midpoint, as eciML1515 uses it. No "
                  "Candida value exists."),
    "complex III": dict(
        area_nm2=68.2, area_class="structure_fungus",
        area_note="Cytochrome bc1 DIMER of SACCHAROMYCES CEREVISIAE, from the III2IV2 "
                  "supercomplex structure PDB 6HU9, in-bilayer cross-section. The dimer is "
                  "the physiological unit. Structures lacking subunit QCR10 (1KB9, 3CX5, "
                  "1EZV, and the C. albicans structure 7RJA at 51.5 nm^2) give smaller "
                  "values; the spread is subunit completeness, not biology. Cross-check: "
                  "the III2IV2 supercomplex measures 157.4 nm^2 against 68.2 + 2 x 45.0 = "
                  "158.2 for its parts, so supercomplex formation is area-neutral to 0.5 %.",
        kcat_s=100.0, kcat_class="ecoli",
        kcat_note="Set to the physiological midpoint eciML1515 uses for its oxidases; no "
                  "fungal or Candida bc1 turnover was found. The models' own value for this "
                  "reaction is the DLKcat parse default (13.7 s^-1), i.e. not a prediction."),
    "complex IV": dict(
        area_nm2=45.0, area_class="structure_fungus",
        area_note="Cytochrome c oxidase MONOMER of SACCHAROMYCES CEREVISIAE, PDB 6HU9; the "
                  "standalone yeast structure 6YMY gives 45.8 nm^2 and 7Z10 / 8DH6 agree at "
                  "41-46. Note this reaction is UNCOSTED in all four models (no GPR), so "
                  "there is no molecular weight in the models' own accounting to check it "
                  "against -- and per Carlson et al. 2024 there would be no point if there "
                  "were, since membrane footprint does not scale with enzyme mass.",
        kcat_s=100.0, kcat_class="ecoli",
        kcat_note="Physiological midpoint, as for the E. coli oxidases (Bekker 2009 measures "
                  "bo3 225, bd-I 218, bd-II 818 s^-1; the configuration-E parameterisation "
                  "eciML1515 was fitted with uses a round 100). No Candida value exists."),
    "ATP synthase": dict(
        area_nm2=57.9, area_class="structure_fungus",
        area_note="F1Fo ATP synthase MONOMER of SACCHAROMYCES CEREVISIAE, PDB 6B2Z/6B8H, "
                  "which include the dimerisation subunits e, g, k and i. Structures lacking "
                  "them (6CP6) give 44-45 nm^2. THE DIMER HAS NO PLANAR FOOTPRINT: the two "
                  "monomers' membrane normals are 86.3 degrees apart (Davies et al. 2012), "
                  "because the dimer sits on a curved cristae ridge; summed over that curved "
                  "surface it is ~116 nm^2. The monomer value is used. "
                  "THIS IS THE ROW THAT MATTERS: Carlson et al. 2024 find ATP synthase "
                  "accounts for 45 % of the membrane area used by central metabolism in "
                  "E. coli and is by far the most sensitive term; in these Candida models it "
                  "is 99.6-99.99 % of the area used (K4 TASK 3).",
        kcat_s=270.0, kcat_class="ecoli",
        kcat_note="Szenk 2017, as eciML1515 uses it. No ATP-synthesis-direction turnover was "
                  "found for yeast or Candida ATP synthase. The models' own value is again "
                  "the DLKcat parse default, 13.7 s^-1."),
}

# reactions: read off each model (TASK 1). This column IS species-specific, and it is the only
# one that is -- but it differs by RECONSTRUCTION provenance, not by biology (the three
# iRV973-derived models share a scaffold).
REACTIONS = {
    "cauris_iRV973": {
        "complex I": "R11945__mito R11945__cyto", "complex II": "R02164__mito",
        "complex III": "R02161__mito", "complex IV": "R00081__mito",
        "ATP synthase": "T_ATP_synthase__mito"},
    "chaemulonii_draft": {
        "complex I": "R11945__mito R11945__cyto", "complex II": "R02164__mito",
        "complex III": "R02161__mito", "complex IV": "R00081__mito",
        "ATP synthase": "T_ATP_synthase__mito"},
    "cduobushaemulonii_draft": {
        "complex I": "R11945__mito R11945__cyto", "complex II": "R02164__mito",
        "complex III": "R02161__mito", "complex IV": "R00081__mito",
        "ATP synthase": "T_ATP_synthase__mito"},
    "cparapsilosis_iDC1003": {
        "complex I": "R11945__mito", "complex II": "R02164__mito",
        "complex III": "T02161__mito", "complex IV": "R00081__mito",
        "ATP synthase": "T00485__cyto"},
}

# Electrogenicity, read off each model. h_p_target is left BLANK everywhere: the column exists
# to OVERRIDE a model's proton stoichiometry, and overriding it here would silently repair the
# encoding defects TASK 1 found (complex I non-electrogenic, complex III reversed in the three
# iRV973-derived models) inside a prompt about membrane area. Those are reported, not patched.
# The core's set_proton_stoichiometry also defaults to E. coli's 'p'/'c' compartments, which do
# not exist in these models, so the column would be a silent no-op here even if it were set.
ELECTROGENICITY = {
    "cauris_iRV973": {
        "complex I": "NOT electrogenic as encoded (EC 7.1.1.2 but no H+ translocated)",
        "complex II": "non-electrogenic (correct)",
        "complex III": "1.5 H+ cyto->mito: REVERSED relative to a mitochondrion",
        "complex IV": "6 H+ mito->cyto",
        "ATP synthase": "3 H+ cyto->mito (correct direction)"},
    "cparapsilosis_iDC1003": {
        "complex I": "5 H+ mito in, 4 H+ cyto out (electrogenic, correct)",
        "complex II": "non-electrogenic (correct)",
        "complex III": "1.5 H+ mito->cyto (correct)",
        "complex IV": "6 H+ mito in, 2 H+ cyto out (correct)",
        "ATP synthase": "3 H+ cyto->mito (correct direction)"},
}
ELECTROGENICITY["chaemulonii_draft"] = ELECTROGENICITY["cauris_iRV973"]
ELECTROGENICITY["cduobushaemulonii_draft"] = ELECTROGENICITY["cauris_iRV973"]

HEADER = """# ETC complexes of {species}: membrane footprint, turnover, the reactions that carry each
# complex's flux, and electrogenicity. Built by reports/K4_membrane/task2_build_tables.py (K4).
#
# READ THIS BEFORE USING THE TABLE.
#
# EVERY FOOTPRINT AND TURNOVER IN THIS FILE IS IDENTICAL ACROSS THE FOUR CANDIDA SPECIES.
# Nothing species-specific exists to put in them. There is no published membrane footprint,
# turnover or abundance for any ETC complex of any Candida species, and no fungal equivalent
# of Szenk, Dill & de Graff (2017) Cell Systems 5:95-104, which is where E. coli's footprints
# come from. A constraint whose parameters are identical across species cannot explain a
# difference between them, so THIS TABLE CANNOT BE USED FOR AN INTERSPECIES COMPARISON. It is
# a starting point for asking what the mechanism does, which is what K4 used it for.
#
# PROVENANCE, per column:
#   area_nm2   {area_prov}
#   kcat_s     {kcat_prov}
#   reactions  read off this model (K4 TASK 1). The ONLY species-varying column -- and it
#              varies by RECONSTRUCTION, not by biology: the three iRV973-derived models share
#              one scaffold, and only C. parapsilosis (iDC1003) is independently curated.
#   h_p_target BLANK throughout, deliberately. Setting it would override the model's own
#              proton stoichiometry and so would silently repair the encoding defects K4
#              TASK 1 reports. It would also be a no-op: the core's set_proton_stoichiometry
#              defaults to E. coli's 'p'/'c' compartments, which these models do not have.
#
# WHAT THE MODEL'S OWN NUMBERS SAY, and why they are not used. The kcat table these strains
# already carry gives per-species DLKcat turnovers for complexes I and II (spread 1.6x and
# 2.4x across the three Candidozyma) and the parse default 13.7 s^-1 for complex III and ATP
# synthase -- i.e. not a prediction at all for two of five rows. Using the DLKcat values would
# make the table species-specific through exactly the predictor channel A1 found has no
# demonstrated per-protein validity (reports/predictor_calibration/report.md). Worse, in the
# three iRV973-derived models complexes I, III and ATP synthase share ONE identical set of
# seven genes and therefore one molecular weight, so the models do not distinguish these three
# complexes at all.
#
# THE ABSOLUTE SCALE is set by A_ETC, not here; only the RELATIVE weights A_i/kcat_i matter to
# the allocation. No defensible per-species A_ETC exists either (see the report).
#
# {species} ETC as encoded:
{electro}
complex,area_nm2,kcat_s,reactions,h_p_target,notes
"""

SPECIES_NAME = {
    "cauris_iRV973": "Candidozyma auris (Candida auris)",
    "chaemulonii_draft": "Candidozyma haemulonii (Candida haemulonii)",
    "cduobushaemulonii_draft": "Candidozyma duobushaemulonii (Candida duobushaemulonii)",
    "cparapsilosis_iDC1003": "Candida parapsilosis",
}


def main():
    src_rows = []
    for strain, rxns in REACTIONS.items():
        area_classes = {COMPLEX_DATA[c]["area_class"] for c in rxns}
        kcat_classes = {COMPLEX_DATA[c]["kcat_class"] for c in rxns}
        electro = "\n".join(f"#     {c:14s} {ELECTROGENICITY[strain][c]}" for c in rxns)
        head = HEADER.format(
            species=SPECIES_NAME[strain], electro=electro,
            area_prov=("derived from solved structures OF FUNGI (Yarrowia lipolytica complex "
                       "I, 6RFR; S. cerevisiae complexes II/III/IV/V, 9KPS/6HU9/6B2Z), as the "
                       "membrane-plane cross-section. IDENTICAL across the four species: "
                       "there is no Candida structure to differentiate them."),
            kcat_prov=("taken from E. coli (Szenk 2017 / Bekker 2009 physiological "
                       "midpoints), as strains/eciML1515/etc/complexes.csv uses them. NO kcat "
                       "has been measured for any ETC complex of any Candida species."))
        lines = [head]
        for c in rxns:
            d = COMPLEX_DATA[c]
            note = ELECTROGENICITY[strain][c].replace(",", ";")
            lines.append(f"{c},{d['area_nm2']:g},{d['kcat_s']:g},{rxns[c]},,{note}\n")
            src_rows.append(dict(
                strain=strain, species=SPECIES_NAME[strain], complex=c,
                reactions=rxns[c],
                area_nm2=d["area_nm2"], area_provenance=d["area_class"],
                area_source=d["area_note"],
                kcat_s=d["kcat_s"], kcat_provenance=d["kcat_class"],
                kcat_source=d["kcat_note"],
                electrogenicity_provenance="model",
                electrogenicity=ELECTROGENICITY[strain][c]))
        out = os.path.join(ROOT, "strains", strain, "etc")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "complexes.csv"), "w") as fh:
            fh.write("".join(lines))
        print(f"  wrote strains/{strain}/etc/complexes.csv "
              f"({len(rxns)} complexes; area classes {sorted(area_classes)}, "
              f"kcat classes {sorted(kcat_classes)})")

    df = pd.DataFrame(src_rows)
    df.to_csv(os.path.join(HERE, "task2_sourcing.csv"), index=False)

    print("\nSOURCING BREAKDOWN -- the table this prompt asks to be shown prominently:")
    n = len(df)
    for col, label in (("area_provenance", "area_nm2"), ("kcat_provenance", "kcat_s"),
                       ("electrogenicity_provenance", "electrogenicity")):
        counts = df[col].value_counts()
        print(f"\n  {label}  ({n} values across the four species)")
        for k, v in counts.items():
            print(f"      {k:18s} {v:3d}  ({100*v/n:5.1f} %)")
    print("\n  measured in a Candida species:      0  (0.0 %)  -- for BOTH area and kcat")
    print("  kcat measured in any fungus:       0  (0.0 %)")
    print("\n  => the footprints and turnovers are IDENTICAL across the four species.")
    print("     A constraint with identical parameters cannot explain a difference between")
    print("     them. This is the same failure mode as Seq2Tm's overlapping distributions,")
    print("     and it is stated here before any result is interpreted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
