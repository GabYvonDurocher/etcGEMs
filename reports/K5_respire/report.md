# K5 — making the *Candida* models respire, and testing them against measured respiration

_2026-09-08. Branched from `main` at **c094bf0** (the K4 merge). P4 had **not** landed when this
started, so `strains/eciML1515/` and `reports/ecoli_*` are audited read-only and never written._

K4 found that the respiratory chain in the three *Candidozyma* models supplies 0.02–0.05 % of
the protons ATP synthase consumes. K5 repairs that, and then does something these models have
never had: it compares their predicted respiration against Ilgaz's measured O₂ assay.

**Four results, in the order they matter.**

1. **The defect is specific to one reconstruction.** *E. coli* does not have it, so Parsa's
   configuration E and F respiration R² values are not undermined.
2. **Costing the transport does not fix it; constraining the direction does**, at a cost of
   36–38 % of predicted growth.
3. **The repaired model does not respire like the organism.** It gets the level right and the
   temperature dependence wrong, and the sign of E_resp − E_growth is inverted.
4. **The membrane constraint, re-tested with both escape routes closed, now has an answer —
   122-fold — and still pushes in the wrong direction.**

Reproduce with:

```bash
python3 reports/K5_respire/task1_coupling_audit.py                       # all seven strains
python3 reports/K5_respire/task2_fix.py                                  # the three candidate fixes
CANDIDAS_ROOT=... python3 reports/K5_respire/task3_respiration_test.py   # against measurement
python3 reports/K5_respire/task3b_membrane_retest.py                     # the membrane re-test
python3 reports/K5_respire/task4_required_separation.py                  # Figure 4's arithmetic
etcgem transfer --experiment candida_B5_respire                          # the repaired model
```

Detail is in `task1_audit.md`, `task2_fix.md`, `task3_respiration.md`,
`task3b_membrane_retest.md` and `task4_required_separation.md`; this file is the summary.

---

## 1. The audit, extended to the coupling ion, on all seven strains

Classes A–D of `etcgem audit-sinks` watch chemical carriers and terminal acceptors. None
watches the **ion** ATP synthase runs on, which is why a free proton circuit passed an audit
reporting 44–47 class-A hits in the same models. Class E is that check.

| strain | ion | chain supplies (translocated) | incl. in-compartment chemistry |
|---|---|---|---|
| *C. auris* | H⁺ | **0.05 %** | 16 % |
| *C. haemulonii* | H⁺ | **0.05 %** | 15 % |
| *C. duobushaemulonii* | H⁺ | **0.04 %** | 11 % |
| *C. parapsilosis* | H⁺ | 112 % | 139 % |
| *E. coli* | H⁺ | **124 %** | 124 % |
| *M. maripaludis* | **Na⁺** | 105 % | 105 % |
| *Synechocystis* | H⁺ | 19 % | **100 %** |

**Only the three *Candidozyma* have the defect**, and they share the *iRV973* scaffold.
*C. parapsilosis*, independently curated, is healthy on the same metric under the same
configuration. So this is a property of one reconstruction, not of the model class, the
framework, or fungi.

**The separating feature is reversibility, not uncostedness.** *E. coli* has twelve uncosted
proton-moving reactions and **none reversible**; the three *Candidozyma* have 9–15 uncosted
**reversible** carriers and the solver uses one of them.

Three things had to be right or the audit mis-reads an organism: the coupling ion is inferred
per strain (*M. maripaludis* is sodium-driven); the ion can enter the energised compartment by
chemistry as well as translocation (*Synechocystis* scores 19 % on translocation alone and 100 %
when the lumen's water splitting and cytochrome *b*₆*f* are counted); and GECKO's arm/isozyme
split puts the two halves of ATP synthase in different reactions, so a naive test finds no ATP
synthase in eciML1515 at all.

*E. coli*, honestly: it does have an uncosted reverse pyruvate/proton symporter delivering 34 %
of ATP synthase's draw. It does not matter there because the chain over-supplies. **Reported,
not fixed — P4 owns eciML1515.**

## 2. The fix

| | what it does | chain supplies after | growth cost |
|---|---|---|---|
| (a) cost the transport | costs 78 mitochondrial carriers, Config A's mechanism | **0.04–0.05 %** — no change | −5 % |
| **(b) constrain the direction** | uncosted reversible carriers may not export protons into the cytosol | **200–272 %** | **−36 to −38 %** |
| (c) explicit bounds | not needed | — | — |

(a) fails on arithmetic: the leak costs about 1 % of the proteome budget and buys roughly ten
times the ATP the chain would have to pay for.

(b) is a thermodynamic argument, not an empirical patch: a symporter is driven *by* the
gradient and cannot build the gradient that drives it. Nothing is deleted and no numerical bound
is invented. **Iteration was required** — constraining the one carrier that leaks lets the
solver reroute through another, taking three to five rounds — and that is itself a finding
about how such defects behave.

Lives in `configs/experiments/candida_B5_respire.yaml` as ladder rung B5, not in `strain.yaml`,
so no committed output moves and **K1's gate still passes 79/79, exit 0**.

**The repair exposes a second defect, quantified.** The chain over-supplies at 200–272 % rather
than ~100 % because complex III in these models is encoded with its protons moving
cytosol→matrix, the opposite direction to a mitochondrion. It therefore spends proton-motive
force and eats **exactly half** of what cytochrome *c* oxidase pumps. Not fixed here; carried
through TASK 3 as a labelled sensitivity.

## 3. Does it respire like the organism? No — and it now fails informatively

Three scale-free comparisons, because the cell-mass conversion is about six-fold uncertain
(`OPEN_ITEMS` 1.9). Absolute per-cell respiration is written out and labelled and nothing is
concluded from it.

**Before the repair there was no decoupling at all.** qO₂/µ was constant to four significant
figures from 22 to 44 °C, and E_resp equalled E_growth to three decimals. Respiration was not a
separate process: the O₂ consumed was biosynthetic demand and scaled with growth exactly. The
measured ratio varies 7.8-fold over the same range.

| | measured | before | after (B5) | B5 + complex III |
|---|---|---|---|---|
| respiration per unit growth (*C. auris*, 28–40 °C) | 0.85 | 0.10 (**0.12×**) | 2.01 (2.35×) | 1.10 (**1.28×**) |
| ratio at 44 °C / at 30 °C | **4.70×** | 1.01× | 1.20× | 0.90× |
| E_resp − E_growth (eV) | **+0.33** | +0.003 | **−0.33** | −0.23 |
| growth / respiration peak (°C) | 34 / **44** | 38 / 38 | 36 / **40** | 38 / 40 |

* **Level: fixed.** From 8–12× too low to within 0.9–1.3× once complex III is corrected too.
* **Shape: qualitatively fixed.** Respiration now peaks 4–8 °C above growth, against a measured
  6–10 °C. Before, the two peaked at exactly the same temperature in all three models.
* **Temperature dependence: not fixed.** The organism raises respiration relative to growth
  4.7-fold between 30 and 44 °C; the model raises it 1.2-fold, and the activation-energy
  difference has the **wrong sign** in all four species.

Nothing was tuned. The measured phenomenon is a cell spending progressively more carbon on
respiration per unit growth as it heats up — the signature of maintenance, futile cycling, leak
or turnover. The model has one of those, NGAM(T), and it is far too weak to produce a 4.7-fold
swing. That is a statement about the maintenance layer, not the ETC.

## 4. The membrane constraint, re-tested

K4 ran its A_ETC sweep with two escape routes open. Both are now closed: the proton leak, and
fermentation. On the repaired *C. auris* at 40 °C, carbon uptake **triples** (12.0 → 35.9 mmol
C/gDW/h) as A_ETC tightens to zero — the cell buys its way out with carbon, as P4 found in
*E. coli* on M9. The cap is `c_max = 12.0`, the carbon the calibration strain uses unconstrained,
i.e. the tightest cap that does not itself reduce base growth.

**A required interspecies difference now exists**, and both changes were needed to get it:

| species | K4 | repaired, no cap | **repaired + cap** |
|---|---|---|---|
| *C. haemulonii* | none at any budget | none | **122× smaller A_ETC** |
| *C. duobushaemulonii* | none | none | none |
| *C. parapsilosis* | none | none | none |

Against the nearest measured comparator — 7× between-species variation in fungal bioenergetic
membrane content — that is about **17× short**.

**The direction still runs backwards.** At zero area, *C. auris* retains 0.231 of its
unconstrained peak against 0.371, 0.578 and 0.352 for the others. The thermotolerant species is
still the most membrane-limited, and the cap widens the gap. For the mechanism to explain the
phenotype the ordering would have to invert.

**The parameter caveat is untouched.** Zero of twenty area and turnover values are measured in
any *Candida*; all four species carry identical tables. A constraint with undifferentiated
parameters cannot **explain** a species difference however it now behaves.

## 5. Figure 4's arithmetic

| model state | required ΔTm | vs 0.411 °C predicted | vs 1.6 °C measured |
|---|---|---|---|
| the standalone (B0) | 32.5 °C | 79× | 20× |
| K2, the core's unfolding form | 13.8 °C | 34× | 8.6× |
| **K5, repaired chain, no cap** | **13.57 °C** | 33× | 8.5× |
| **K5, repaired chain + carbon cap** | **13.57 °C** | 33× | 8.5× |

**The requirement moves by 0.07 °C.** It falls, which is the expected direction, by half a
percent, which is not the expected magnitude. The counterfactual shifts *every* enzyme's Tm, so
the fermentation and biosynthetic enzymes denature along with the chain and the escape routes
are beside the point at the shift that kills the cell.

So the 13.8 °C figure was never propped up by the leaks. That was a live possibility before this
was computed and is now closed. Not adjudicated further.

---

## Verification

| check | result |
|---|---|
| K1 gate, `$CANDIDAS_ROOT` unset | **79/79 PASS, exit 0**, before and after |
| every K5 script re-run | exit 0, tables regenerate |
| `strains/eciML1515/`, `reports/ecoli_*` | **untouched** — P4 had not landed |
| `stamp_reports.py --check` | exit 0 |

## Files

| what | where |
|---|---|
| the audit, all seven strains | `task1_audit.md`, `task1_budget*.csv`, `task1_translocators*.csv` |
| the three candidate fixes | `task2_fix.md`, `task2_fix_comparison.csv`, `task2_reaction_justification.csv` |
| the repaired model | `configs/experiments/candida_B5_respire.yaml` |
| against measured respiration | `task3_respiration.md`, `task3_*.csv` |
| the membrane re-test | `task3b_membrane_retest.md`, `task3b_*.csv`, `task3b_flatness.json` |
| Figure 4's arithmetic | `task4_required_separation.md`, `task4_required_separation.csv` |
| decisions | `DECISIONS.md` |
