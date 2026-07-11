# Ea-dissection diagnostic: the two caveats

Tuned model (P2 v3 medians), rich BHI (and glucose where noted), Gurobi, O2 sinks closed.
**Confirmed before diagnosing:** solver = gurobi; 4 O2 sinks closed; `Ea_org = 0.9095 eV`,
window 17–35 °C, Topt 39 °C (reproduces the headline). Non-circularity preserved: `Ea_i` are
inputs; these are attributions.

## Caveat 1 — is the lipid-synthesis dominance real, or the acpP carrier-protein hub?

**acpP (P0A6A8)** is a shared acyl-carrier-protein hub: it participates in **30 reactions** in
the ecModel (7 of them flux-carrying at the BHI operating point). Its total growth control and
Ea contribution:

| medium | acpP Σ C_i | acpP contribution C_i·Ea_i | % of the kinetic term | lipid COG total | acpP part | genuine (non-acpP) |
|--------|-----------|---------------------------|-----------------------|-----------------|-----------|--------------------|
| BHI | 0.038 | 0.078 | **14.5 %** | 0.276 | 0.078 | **0.198** |
| glucose | 0.022 | 0.042 | 4.9 % | 0.163 | 0.042 | 0.121 |

**By-COG ranking, BHI, WITH vs WITHOUT acpP:**

| category | with acpP | without acpP |
|----------|-----------|--------------|
| lipid metab | 0.276 | **0.198** |
| carbohydrate / glycolysis | 0.152 | 0.152 |
| amino-acid metab | 0.034 | 0.034 |

Top enzymes without acpP (BHI): **gapA** (0.092), **fabB** (0.081), deoB (0.026), **glnA**
(0.025), **eno** (0.023), **fadA** (0.018) — all genuine catalytic enzymes.

**VERDICT: the lipid/fatty-acid dominance is REAL, not an acpP artefact.** acpP is a genuine
but minority contributor (14.5 % of the BHI kinetic term); the *genuine* fatty-acid enzymes
(fabB, fadA) carry the majority (0.198 of the 0.276), and **lipid metabolism still leads the
by-COG ranking after acpP is removed** (0.198 > glycolysis 0.152). The paper can claim the
lipid finding, with the honest note that ~28 % of the lipid-COG contribution is the shared
acyl-carrier hub. At **glucose-minimal** the story differs entirely — the controlling set is
**amino-acid biosynthesis** (argG dominant, 0.145), acpP is minor (4.9 %), and lipid is
secondary — consistent with the medium-dependent controlling set. Corrected tables/figure
saved with a `_no_carrier` suffix (originals untouched).

## Caveat 2 — the homogenisation → 1.32 eV

**What "homogenise" did:** set every enzyme's `Topt_i` and `dCp_i` (via `_Topt`, `_uCpt`) to
their dataset means (Topt → 40.8 °C), leaving `Tm`/`f_N` untouched, and recompute `Ea_org`.

The result is **largely a numerical / edge artefact, not a clean "heterogeneity lowers Ea"
transformation**, for three reasons:

1. **The rising-limb window SHIFTS.** With every `Topt` set equal, all enzymes peak together,
   the organismal peak *sharpens*, and the 10–95 %-of-rmax window moves from **17–35 °C to
   23–35 °C** — a narrower, hotter, intrinsically **steeper** region of the curve. A steeper
   window gives a higher Arrhenius slope regardless of the enzymes.
2. **Maintenance amplifies in that hot window.** Decomposing the homogenised case with the same
   MCA: control-weighted mean 0.814 + allocation −0.121 + **maintenance +0.400** + residual
   0.226 = 1.320. The maintenance term jumps from **−0.010 (heterogeneous) to +0.400**, because
   the shifted window sits near the peak where NGAM(T) shapes the limb most — this single
   window-position effect accounts for most of the rise.
3. **The homogenisation is incomplete.** Only `Topt`/`dCp` were set to the mean; `Tm` (hence the
   folded fraction `f_N`) was not, so the "common" `Ea_i` are *not* common — they still range
   from 0.70 to **22 eV** (sd 1.04) as low-`Tm` enzymes' `f_N` collapses inside the window.

(Edge checks: growth law was ON throughout; the descriptor was computed identically; the peak
Topt stayed at 39 °C — it is the *window*, not the peak, that moved.)

**VERDICT: do not over-interpret the 1.32.** The clean, defensible robustness statement is the
one from the *spread* sweep: `Ea_org` is **stable at ~0.90–0.93 eV over moderate changes in the
enzyme-Ea heterogeneity** (×0.5–1.0). The full-homogenisation value is confounded by the window
shift, maintenance-in-the-hot-window, and incomplete `Tm` homogenisation, and should be dropped
from (or explicitly caveated in) the write-up rather than cited as "heterogeneity lowers the
organism Ea".

## For the write-up

- **Keep** the lipid + glycolysis pathway-localisation claim (robust to acpP; note the hub).
- **Drop / caveat** the "homogenising raises Ea to 1.32 ⇒ heterogeneity lowers Ea_org" claim;
  use the moderate-spread robustness (~0.90–0.93) instead.
- The medium dependence (BHI = lipid/glycolysis vs glucose = amino-acid biosynthesis) is the
  more interesting robustness result and is clean.
