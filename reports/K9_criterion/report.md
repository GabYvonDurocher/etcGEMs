# K9 — which criterion should Figure 4 use, and does the common ceiling term generalise?

_2026-09-08. Branched from `main` at **450e317**, the K8 merge. **P4 had not landed**, so
*E. coli* is read from committed outputs. **No default is changed.**_

**Two answers, and both are negative.**

1. **The ceiling criterion's interspecies requirement is arithmetic, not a model constraint.**
   The prompt's headline table — "~5 °C under the ceiling criterion, within threefold of the
   measured 1.6 °C" — does not survive its own test and is corrected here.
2. **The ~5.6 K common ceiling term does not generalise.** Residuals span 0.05 to 10.48 °C
   across the strains where they can be computed. *E. coli*'s 5.6 K is real and unexplained, and
   it is a one-organism observation.

Reproduce with:

```bash
python3 reports/K9_criterion/task1_is_it_arithmetic.py
python3 reports/K9_criterion/task2_criteria.py
python3 reports/K9_criterion/task3_common_term.py
```

---

## 1. The ceiling criterion's interspecies requirement is a restatement

This gates everything else, so it is first.

An arithmetic identity does not care what the model is; a model constraint does. Recomputing the
required per-species Tm offset under five model states:

| model state | model's own CT_max spread | required-offset spread | *auris* − relatives |
|---|---|---|---|
| B3, before the K5 repair | 0.63 °C | 6.45 °C | −6.11 °C |
| B5, repaired | 1.62 °C | 6.08 °C | −5.90 °C |
| B5 + carbon cap | 1.66 °C | 6.07 °C | −5.90 °C |
| B5, ΔCp −3.0 | 1.10 °C | 6.05 °C | −5.88 °C |
| B5, ΔCp −6.0 | 2.86 °C | 6.14 °C | −5.96 °C |
| **observed thermal-limit spread** | — | **6.00 °C** | **−6.00 °C** |

The model's own ceiling spread varies **4.5-fold** across these states while the required-offset
spread moves by **±3 %**, pinned to the observed 6.00 °C throughout.

**So the "~5 °C" is the observed thermal-limit difference wearing a model's clothes.** It must
not be set beside A1's measured congeneric 1.6 °C as though the two were commensurable, and the
sentence "the requirement is within about threefold of a measured difference" is not available.

**What survives.** The ceiling criterion is a perfectly good statement about each species
*individually* — "this model's ceiling is 9.8 °C too high for *C. auris*" is a real model
statement, and TASK 3 uses it. It is only the *interspecies difference* that is arithmetic, and
that is exactly what Figure 4 is about.

## 2. Both criteria, as ranges

**Detection criterion** — the uniform downward Tm shift that first puts a relative below a
detection floor at a fixed temperature. Median over the three relatives:

| floor (h⁻¹) \ T | 38 °C | 39 °C | 40 °C | 41 °C | 42 °C |
|---|---|---|---|---|---|
| 0.010 | 15.82 | 14.80 | 13.71 | 12.70 | 11.60 |
| 0.050 | 15.59 | 14.57 | **13.55** | 12.54 | 11.45 |
| 0.100 | 15.43 | 14.41 | 13.40 | 12.30 | 11.21 |

**Range 11.21–15.82 °C.** The **floor is nearly immaterial** — a tenfold change moves the
requirement by 0.31 °C. The **temperature matters roughly one-for-one**. That is the right way
round: the floor is the arbitrary choice and it does not matter, while the temperature is
data-driven (40 °C is where the relatives measurably stop growing and *C. auris* does not).

**Ceiling criterion** — the shift that brings CT_max onto the observed limit. Across a fourfold
grid-resolution range and `crit_frac` from 0.01 to 0.10:

| species | range | spread |
|---|---|---|
| *C. auris* | 9.57–10.34 °C | 0.78 |
| *C. haemulonii* | 15.30–15.85 °C | 0.55 |
| *C. duobushaemulonii* | 15.61–16.14 °C | 0.53 |
| *C. parapsilosis* | 15.66–16.43 °C | 0.77 |

Very robust to its definitional choices.

### Recommendation

**Figure 4 should keep the detection criterion**, and should quote it as **13.6 °C, range
11.2–15.8 °C over interrogation temperatures 38–42 °C**, noting that the detection floor is
immaterial.

The reason is TASK 1, not preference. Figure 4's claim is about an **interspecies** difference,
and the ceiling criterion cannot supply one: its interspecies difference is a restatement of the
observed limits. The detection criterion asks a genuine model question — *how much would this
model's enzymes have to change before it kills this relative where the organism actually dies* —
and it is robust to the one choice inside it that is arbitrary.

**What changes under each.** Under the detection criterion the figure's claim is unchanged in
kind and gains an honest range. Under the ceiling criterion the figure would be quoting an
arithmetic identity as a model requirement, which is worse than the status quo. **No default,
criterion or figure is changed here; this is a recommendation.**

## 3. Does the ~5.6 K common term generalise? No

| strain | Tm provenance | median Tm | gap | total correction | predictor | **residual** |
|---|---|---|---|---|---|---|
| *M. maripaludis* | prior (mesophile) | 55.9 | +0.05 | 0.05 | 0 | **0.05** |
| *C. auris* | Seq2Tm | 53.7 | +9.02 | 9.81 | 5.43 | **4.38** |
| *E. coli* | **measured meltome** | 55.6 | +5.88 | 5.60 | 0 | **5.60** |
| *C. haemulonii* | Seq2Tm | 53.5 | +13.83 | 15.51 | 5.43 | **10.08** |
| *C. duobushaemulonii* | Seq2Tm | 53.5 | +13.65 | 15.76 | 5.43 | **10.33** |
| *C. parapsilosis* | Seq2Tm | 54.2 | +15.25 | 15.91 | 5.43 | **10.48** |
| *Synechocystis* | prior (mesophile) | 56.9 | +1.70 | — | 0 | — |

**There is no constant.** Residuals span **0.05 to 10.48 °C**. Only *C. auris* (4.38) sits near
*E. coli*'s 5.60; the three relatives are roughly double it and the methanogen is essentially
zero. **A common ~5–6 K term is not visible across strains**, and K8's framing of *E. coli*'s
5.6 K as "a common term" is not supported by the seven-strain data. It remains real, unexplained,
and confined to one organism.

**The three confounds, addressed.**

* *M. maripaludis*' 0.05 °C is computed **at its calibrated `kcat_scale` of 7.223**. A-priori its
  predicted TPC is identically zero, so it has no ceiling to measure and **cannot be evidence
  either way**.
* The non-Candida strains differ from the Candida strains in **both** median Tm (55.9, 56.9
  against 53.5–54.2) **and** observed limit (47, 44 against 38–44). The gap is a difference of
  two quantities and both move.
* **The mesophile prior is built on *E. coli*'s own meltome**, so the methanogen and phototroph
  are **not independent evidence** about a term observed in *E. coli* — their Tm distribution *is*
  *E. coli*'s, transplanted. That removes them as confirmation and as refutation alike.

**One reproducibility finding.** *Synechocystis*' committed ceiling (45.70 °C) is not reproducible
from a plain strain build, which gives 55.50 °C. The committed curve is **not** truncated — growth
falls to 0.2 % of peak by 50 °C — and the light-saturated medium its own script applies does not
account for the difference. Its correction is left blank rather than guessed, and the
non-reproducibility is recorded as an open item.

## 4. What a common term would mean — SPECULATION, no modelling

_Clearly labelled as speculation, per the prompt. Nothing here was modelled or tested._

If cells did reliably die several degrees below where bulk enzyme unfolding predicts — and on the
evidence above only *E. coli* clearly does — the candidates the model class cannot currently
express are: **membrane integrity and proton leak**, which fail as a bilayer property rather than
a protein one; **reactive oxygen damage**, which rises with respiratory flux and would couple the
ceiling to metabolic rate rather than to Tm; **chaperone capacity**, where the proteome keeps
enzymes folded above their in-vitro Tm until the chaperone budget is exhausted, which would make
the ceiling a *capacity* threshold rather than a thermodynamic one; and **in-vivo destabilisation
relative to in-vitro measurement**, where a crowded cytoplasm simply shifts real Tm below the
purified-protein value that a meltome reports.

The last of these is the cheapest to distinguish and the least interesting mechanistically: it
predicts a roughly uniform offset with no dependence on flux or on growth rate. Reactive oxygen
and chaperone capacity both predict a ceiling that moves with metabolic state, so a strain grown
at two different rates to the same temperature would separate them from a pure Tm offset.
Membrane and leak mechanisms predict a dependence on lipid composition, which K4's membrane work
established this framework cannot currently express.

Of these, the framework could express **chaperone capacity** with real work — it already has a
proteome sector layer and a chaperone fraction in the *E. coli* configuration — and could express
**proton leak** as temperature-dependent maintenance, which K5 showed is already wired but far too
weak. It cannot currently express membrane phase behaviour or reactive oxygen damage at all.

## 5. Verification

| check | result |
|---|---|
| K1 gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0** |
| `stamp_reports.py --check` | exit 0 |
| all three K9 scripts re-run | exit 0 |
| defaults changed | **none** |
| `strains/eciML1515/`, `reports/ecoli_*` | untouched; P4 had not landed |
