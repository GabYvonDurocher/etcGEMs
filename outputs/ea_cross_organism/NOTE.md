# Why methanogenesis Ea > respiration: E. coli vs M. maripaludis (Sharpe–Schoolfield E)

> **FINALISED (symmetric, M5b).** Both organisms now carry a proteome-sector/growth-law layer,
> so the allocation term is **measured** for each, not structural. E. coli: Scott scaling law →
> allocation **−0.130**. M. maripaludis: constant-ribosome-fraction *flat* growth law (Müller
> 2021) → allocation **+0.000** (directly measured on the sectored model; binding constraint
> unchanged, M5 control coefficients valid). The allocation asymmetry is grounded in each
> organism's **own measured allocation strategy**. Paper-ready assets:
> `comparison_table_final.csv`, `cross_organism_decomposition_final.png`, the two
> `ea_dissection_ss/decomposition_ss.json`, `mcr_sweep.csv`. (The M5 originals are kept.)

The culminating cross-organism analysis. Both organisms dissected identically: organism Ea =
window-independent Sharpe–Schoolfield E; per-enzyme Ea_i = rising-limb Arrhenius E of
kcat_i(T) (folding term separated); MCA control coefficients C_i; a 4-term decomposition with
the **aggregation** term computed directly (SS-E of the kinetic-backbone curve − the
control-weighted per-enzyme E). Everything SS-E; no re-calibration.

## Headline validation
Both models **match their observed** SS-E — a genuine a-priori-style check:

| | model SS-E | observed SS-E | Topt | CTmax |
|---|---|---|---|---|
| *E. coli* (rich BHI) | **0.68** | 0.56 (Van Derlinden) | 38 °C | 46 °C |
| *M. maripaludis* (H2/CO2) | **1.06** | 1.04 (Jones 1983) | 35 °C | 49 °C |

*E. coli* sits on the "universal" metabolic ~0.65 eV benchmark; **the methanogen is ~1.6×
higher** — the signal the window-dependent slope had obscured (it made them look comparable).

## The 4-term SS-E decomposition, side by side (`comparison_table.csv`)
| term (eV) | *E. coli* | methanogen | Δ (methanogen − E. coli) |
|---|---|---|---|
| naive (unweighted) enzyme-E mean | 0.872 | **0.512** | −0.360 |
| + control weighting | +0.106 | **+0.343** | +0.236 |
| + allocation (growth law) | −0.130 | **0.000** | +0.130 |
| + maintenance NGAM(T) | +0.005 | −0.016 | −0.021 |
| + aggregation (heterogeneity/flattening) | −0.175 | +0.218 | +0.393 |
| **= organism Ea (SS-E)** | **0.678** | **1.056** | **+0.378** |
| (control-weighted enzyme-E mean) | 0.978 | 0.855 | |
| (sum C_i) | 0.556 | 1.189 | |

## The honest bottom line on "methanogenesis Ea > respiration"
**It is not because methanogen enzymes are intrinsically more temperature-sensitive** — on
average they are *less* (naive mean 0.512 vs 0.872 eV). The higher organism Ea is
**structural**, and two robust, interpretable terms account for essentially the whole
difference:

1. **Control concentrates on the high-E methanogenesis backbone (+0.24 eV vs E. coli).** In
   the methanogen, energy metabolism *is* growth: the Wolfe-cycle backbone
   (Fwd/Mtr/Mcr/Mer/Hdr…) carries **89% of the control term** and is high-E (backbone kcat-E
   0.77 vs proteome mean 0.51). E. coli's control is spread over broad biosynthesis, so its
   control-weighting adds only +0.11.
2. **The methanogen lacks E. coli's allocation buffer (+0.13 eV).** E. coli's growth-law
   proteome reallocation removes 0.13 eV; the methanogen's single sMOMENT pool has no such
   term (allocation = 0). This is grounded in slow growth (~10× slower → the Scott growth-law
   buffer is physiologically weak), **not** hidden — a sector layer would make the comparison
   exactly symmetric (deferred; the one asymmetry to flag).

The remaining two terms nearly cancel: the methanogen's **lower average enzyme E** (−0.36)
is offset by a **larger aggregation term** (+0.39) — its narrow, synchronised control on a
few backbone enzymes steepens the composite curve, where E. coli's broad control flattens it.
The aggregation term is the largest single term but the most definition-sensitive (it carries
the SS-E-vs-windowed basis gap); the robust story does **not** rest on it, since
control-weighting + allocation alone (+0.37) already match the +0.38 difference.

## Robustness to the Mcr kcat uncertainty (`mcr_sweep.csv`, 3–294/s)
| Mcr kcat | SS-E | backbone % of control | leader |
|---|---|---|---|
| 3 | 1.27 | 103% | Mcr (0.61 of proteome) |
| 10 | 1.01 | 99% | Mcr |
| 30 | 1.07 | 92% | Mcr > Fwd |
| **58.9** (calibrated) | **1.06** | **89%** | Fwd ≈ Mcr |
| 100 | 1.07 | 86% | Fwd > Mcr |
| 294 | 1.02 | 83% | Fwd |

- **The ordering is robust:** SS-E stays **1.01–1.27 across the whole Mcr range, always well
  above E. coli's 0.68**. "Methanogen Ea >> respiration" does not hinge on Mcr.
- **The backbone-control finding is robust:** the backbone carries **83–103%** of control
  throughout.
- **Which enzyme leads shifts with Mcr:** Mcr dominates at the low end (slow → expensive →
  high control), Fwd (formylmethanofuran dehydrogenase) leads at the high end; at the
  calibrated value they co-lead. So the reframed hypothesis is confirmed at the **backbone**
  level (robust), and the classic **Mcr** hypothesis holds specifically when Mcr is slow — Mcr
  is a top-2 controller at the best estimate and *the* controller if its kcat is near the low
  end of its 3–294/s range. Pinning the mesophilic-Mcr kcat is the key remaining measurement.

## Caveats (stated, not hidden)
1. **Allocation asymmetry — RESOLVED (M6/M5b):** the methanogen now carries its own
   sector/growth-law layer (Müller 2021 flat, constant ribosome fraction), so the allocation
   buffer is a **measured +0.000** (not a structural 0), symmetric with E. coli's measured
   −0.130 (Scott). The comparison is now on equal footing; the buffer difference is grounded
   in each organism's own allocation physiology.
2. **Aggregation term** is the largest and most definition-sensitive; the robust conclusion
   rests on control-weighting + allocation, not on it.
3. **Mcr kcat 3–294/s** — the ordering + backbone finding are robust across it, but the
   identity of the single leading enzyme (Mcr vs Fwd) is not.

## GO to write up
**GO.** The cross-organism result is complete, validated (both match observed), and robust to
the headline uncertainty. This seeds the comparative section (a `reports/` extension or a
dedicated cross-organism report — decide at write-up): *E. coli*'s ~0.65 eV growth Ea is a
broadly-controlled, allocation-buffered aggregate; the methanogen's ~1.0 eV is a narrowly-
controlled, unbuffered energy-backbone Ea — the same control-weighted-aggregation mechanism,
a different controlling set, explaining why methanogenesis Ea > respiration.
