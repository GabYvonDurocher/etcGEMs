# N2 — summary

Five tasks, **all DONE**. TASK 0 merged N1 into `main` (the one permitted write to `main`);
TASKS 1–4 are on `n2/followups` and end in a PR that is not merged.

Nothing here altered a scientific conclusion. Two measurements were recorded, one stale
artefact was diagnosed and regenerated, and one default was flipped — and the flip moves
nothing above 2 × 10⁻¹² relative.

## Status

| task | status | one line |
|---|---|---|
| **0 — merge N1** | **DONE** | `bab2340` (`--no-ff`), pushed; PR #1 **MERGED**; gate 79/79 with `$CANDIDAS_ROOT` unset |
| **1 — the stale eciML1515 TPC** | **DONE** | Cause found before regenerating: **the file was already stale when it was committed**, by `a416fd1` two months earlier. 45 of 46 other outputs reproduce. |
| **2 — resolve D8** | **DONE** | Rescaling is the **default**; the gate keeps `legacy_fidelity`. **No quoted number changes.** |
| **3 — flatness guard** | **DONE** | Three notes, each with the fact that bounds it, in the files a reader reaches |
| **4 — A3's coverage numbers** | **DONE** | §5, §6(e) and §8 of the discussion notes |

## TASK 1 — the cause, and it is not what a stale file usually means

**`strains/eciML1515/outputs/tpc/` was already stale when it was committed.** Commit
`c6a20ad` (2026-09-07) produced Topt 31.0 °C / rmax 0.5429 while committing a file that says
37.0 °C / 0.3413. The content dates from 2026-07-02 and was carried unchanged for two months.

Bisected by checking the repository into scratch worktrees and re-running against each
state's own code:

| commit | Topt | rmax | |
|---|---|---|---|
| `27cafef^` | 37.0 | 0.3407 | what the committed file reflects |
| **`a416fd1`** | **30.0** | **0.5497** | **medium-dependent sector allocation — the cause** |
| `922e13d` | 31.0 | 0.5467 | growth-law partition |
| `8085036` | 31.0 | **0.5429** | O2-sink closure |
| today | 31.0 | 0.5429 | |

`a416fd1` re-grounded the sector split from the **pooled** measured 30 °C proteome to the
**Glucose-minimal** one (f_metab 0.285 → 0.483), so the pool budget rose 70% and the ribosome
cap moved out of the way. **The envelope never moved** — CTmax 46.856 → 46.881, Eₐ 0.934 →
0.956 — which is what pointed at allocation rather than the thermal layer. No scientific
conclusion depends on this file; it is the nominal glucose-minimal smoke test.

**45 of 46 other committed outputs reproduce** (132 files: every nominal TPC, all 28 Candida
`transfer_*`, both `audit_sinks*` per strain, both `fba` pool runs). The one that does not is
`strains/_toy/outputs/tpc/resolved_config.yaml`, structurally stale in the same way — its
numbers are fine (max **relative** difference 6.2 × 10⁻¹⁵). **Listed, not fixed.** Not
checked, and said so: sweeps, Bayesian calibrations, dissections — hours to days, several
stochastic, so reproduction is a different question there.

## TASK 2 — what flipping the default actually did

| rung | quantities moved | max abs | max rel |
|---|---|---|---|
| B0, B0-uncorrected | **0** | — | legacy fidelity |
| B1 / B1s / B2 / B3 | 137 / 138 / 125 / 128 | ≤ 1.06 × 10⁻¹¹ | ≤ 2.2 × 10⁻¹² |
| B4 | **0** | — | sectors → auto-off |

**No number quoted in K2's report or in the discussion notes changes at any reported
precision, so the list of prose needing a human update is empty.** That is measured — over
every numeric column of every strain in every summary, the fitted globals, the growth scale,
the MSE and every required separation — not assumed. The value of the change is that someone
running this on GLPK, or without a Gurobi licence, now gets the right answer.

Verified: gate 79/79 under legacy fidelity with `$CANDIDAS_ROOT` unset; *E. coli*,
*M. maripaludis* and *Synechocystis* nominal TPCs byte-identical, all three files each.

## TASK 3 — the three notes

Each carries the plateau **and** the fact that bounds it, because a plateau reported alone
invites a reasonable but wrong doubt.

* **K2 B4 row** — plateau 12–14 °C on a 22 °C grid, more than half the tested range; bounded
  by the required separation being stable to 0.3 °C across B1–B4.
* **K2 PART C1** — the same, plus why C1 survives it: the counterfactual is evaluated at a
  *fixed* 40 °C against a *fixed* floor, so it does not depend on where the peak is.
* **K2 PART C2 + discussion §4** — the two strains where the guard fires and the result is
  fine: *M. maripaludis* reports NaN because its a-priori curve is identically zero, and
  *Synechocystis*' plateau is 2.0 °C at 1% and 0.0 at 0.01%. A fired guard means "at risk",
  not "broken".

## TASK 4 — A3 into the notes

**§5** gains the measurement: 122–647 genes differ per comparison at the proteome level and
**0–15 are inside a metabolic model** — the models see about 2–5% of the gene-content
difference — with both methodological caveats (RBH-absence over-states threefold; a
description-only search missed AOX in *C. haemulonii* and returned nothing in
*C. parapsilosis*). **§6(e)** rewritten: all four locatable Xiao et al. candidates are present
in all four species, AOX and the glutaredoxins are in no model, so the mechanism is untestable
here on two grounds — stated as a **scope limit of these reconstructions, not a refutation**.
**§8 A3** marked DONE.

## What still needs a human

1. **`strains/_toy/outputs/tpc/resolved_config.yaml`** is stale. One command; left deliberately.
2. **Rescaling with proteome sectors** is still unsupported (it auto-disables). Extending it
   into `set_allocation` is small but touches the path *E. coli* and *M. maripaludis* run on.
3. **No reproducibility policy for the stochastic outputs** — sweeps, emcee chains, dissections.
   Nothing checks them, and a byte comparison is the wrong check.
4. **§6(e)'s scope-limit sentence** is the one most likely to be quoted out of context; worth
   one human read.
5. Carried from N1 and unchanged: Ilgaz should see `archive/gem_standalone/README.md` and
   `message_to_ilgaz.md` before either lands.

## Decisions

`DECISIONS.md`, D0–D8. Two record checks that did not literally pass and why that was right
(D0, D1); the rest are implementation choices, all reversible.
